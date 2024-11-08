from __future__ import annotations

import logging
from copy import deepcopy
from typing import NewType
import functools

from tqdm import tqdm
import numpy as np
import numpy.typing as npt
from pyaro import list_timeseries_engines, open_timeseries
from pyaro.timeseries import Data, Reader, Station
from pyaro.timeseries.Wrappers import VariableNameChangingReader

from pyaerocom.io.pyaro.pyaro_config import PyaroConfig
from pyaerocom.io.readungriddedbase import ReadUngriddedBase
from pyaerocom.tstype import TsType
from pyaerocom.ungriddeddata import UngriddedData

logger = logging.getLogger(__name__)


MetadataEntry = NewType("MetadataEntry", dict[str, str | list[str]])
Metadata = NewType("Metadata", dict[str, MetadataEntry])


class ReadPyaro(ReadUngriddedBase):
    __version__ = "1.0.1"

    SUPPORTED_DATASETS = list(list_timeseries_engines().keys())

    def __init__(self, config: PyaroConfig) -> None:
        self.config: PyaroConfig = config

        self._check_id()

        self.converter = PyaroToUngriddedData(self.config)
        self.reader = self.converter.reader
        self._data_dir = self.config.filename_or_obj_or_url
        self._data_name = self.config.name
        self._data_id = self.config.name

    """
    Definition of abstract methods from ReadUngriddedBase
    """

    @property
    def DATA_ID(self):
        return self._data_name

    @property
    def PROVIDES_VARIABLES(self):
        """
        return self.reader.get_variables()
        """
        return self.reader.variables()

    @property
    def DEFAULT_VARS(self):
        return self.PROVIDES_VARIABLES

    @property
    def TS_TYPE(self):
        """
        To be provided by the reader or engine
        """
        return "undefined"

    @property
    def _FILEMASK(self):
        return self.config.filename_or_obj_or_url

    @staticmethod
    def get_pyaro_readers():
        return list_timeseries_engines()

    def read(self, vars_to_retrieve=None, files=..., first_file=None, last_file=None):
        return self.converter.read(vars_to_retrieve=vars_to_retrieve)

    def read_file(self, filename, vars_to_retrieve=None):
        return self.converter.read(vars_to_retrieve)

    def _check_id(self):
        avail_readers = list_timeseries_engines()
        if self.config.data_id not in avail_readers:
            logger.warning(
                f"Could not find {self.config.data_id} in list of available Pyaro readers: {avail_readers}"
            )

def _calculate_ts_type(start: npt.NDArray[np.datetime64], end: npt.NDArray[np.datetime64]) -> npt.NDArray[TsType]:
    seconds = (end - start).astype("timedelta64[s]").astype(np.int32)

    @np.vectorize
    @functools.lru_cache(maxsize=128)
    def memoized_ts_type(x: np.int32) -> TsType:
        return TsType.from_total_seconds(x)

    return memoized_ts_type(seconds)


class PyaroToUngriddedData:
    _METADATAKEYINDEX = 0
    _TIMEINDEX = 1
    _LATINDEX = 2
    _LONINDEX = 3
    _ALTITUDEINDEX = 4  # altitude of measurement device
    _VARINDEX = 5
    _DATAINDEX = 6
    _DATAHEIGHTINDEX = 7
    _DATAERRINDEX = 8  # col where errors can be stored
    _DATAFLAGINDEX = 9  # can be used to store flags
    _STOPTIMEINDEX = 10  # can be used to store stop time of acq.
    _TRASHINDEX = 11  # index where invalid data can be moved to (e.g. when outliers are removed)

    # List of keys needed by every station from Pyaro. Used to find extra metadata
    STATION_KEYS = (
        "station",
        "latitude",
        "longitude",
        "altitude",
        "long_name",
        "country",
        "url",
    )

    def __init__(self, config: PyaroConfig) -> None:
        self.data: UngriddedData = UngriddedData()
        self.config = config
        self.reader: Reader = self._open_reader()

    def _open_reader(self) -> Reader:
        data_id = self.config.data_id
        if self.config.model_extra is not None:
            kwargs = self.config.model_extra
        else:
            kwargs = {}

        if self.config.name_map is None:
            return open_timeseries(
                data_id,
                self.config.filename_or_obj_or_url,
                filters=self.config.filters,
                **kwargs,
            )
        else:
            return VariableNameChangingReader(
                open_timeseries(
                    data_id,
                    self.config.filename_or_obj_or_url,
                    filters=self.config.filters,
                    **kwargs,
                ),
                self.config.name_map,
            )

    def _convert_to_ungriddeddata(self, pyaro_data: dict[str, Data]) -> UngriddedData:
        stations = self.get_stations()

        var_size = {var: len(pyaro_data[var]) for var in pyaro_data}
        vars = list(pyaro_data.keys())
        total_size = sum(list(var_size.values()))
        units = {var: {"units": pyaro_data[var].units} for var in pyaro_data}

        # Object necessary for ungriddeddata
        var_idx = {var: i for i, var in enumerate(vars)}
        metadata: Metadata = {}
        meta_idx: dict = {}  # = {s: {v: [] for v in vars} for s in metadata}

        # Helper objects
        station_idx = {}

        idx = 0
        metadata_idx = 0

        COLNO = 12
        outarray = np.nan * np.ones((sum(var_size.values()), COLNO), dtype=float, order="F")

        station_metadata: dict[float, dict] = dict()
        station_mapper: dict[str, float] = dict()
        station_key = 0.0

        var_metadata: dict[float, str] = dict()
        var_key = 0.0

        
        current_offset = 0
        for var, var_data in pyaro_data.items():
            next_offset = current_offset + len(var_data)
            idx = slice(current_offset, next_offset+1)

            curent_offset = next_offset

            # Assert ts_type of a station matches the above, but how?
            stations = var_data.stations
            unique_stations = set(np.unique(stations))
            unknown_stations = unique_stations.difference(station_metadata.keys())

            for s in unknown_stations:
                identifier = station_key
                station_key += 1.0
                station_mapper[s] = identifier
                station_metadata[identifier] = {
                    "variables": [var],
                    "data_id": self.config.data_id,
                    "station_name": s,
                    "latitude": np.nan,
                    "longitude": np.nan,
                }

            if var not in var_metadata.keys():
                identifier = var_key
                var_key += 1.0
                var_metadata[identifier] = var
            for varid, key in var_metadata.items():
                if key == var:
                    break

            # assert a station only contains one ts_type
            ts_types = _calculate_ts_type(var_data.start_times, var_data.end_times)
            for station in unique_stations:
                mask = stations == station
                if np.any(ts_types[mask] != ts_types[mask][0]):
                    raise Exception("ts_type mismatch")


            @np.vectorize
            @functools.lru_cache(maxsize=128)
            def map_station_to_identifier(x: str) -> float:
                return station_mapper[x]


            outarray[idx, UngriddedData._METADATAKEYINDEX] = map_station_to_identifier(stations)
            midtime = var_data.start_times + (var_data.end_times - var_data.start_times)/2
            outarray[idx, UngriddedData._TIMEINDEX] = midtime.astype("datetime64[s]")
            outarray[idx, UngriddedData._LATINDEX] = var_data.latitudes
            outarray[idx, UngriddedData._LONINDEX] = var_data.longitudes
            outarray[idx, UngriddedData._ALTITUDEINDEX] = var_data.altitudes
            outarray[idx, UngriddedData._VARINDEX] = varid
            outarray[idx, UngriddedData._DATAINDEX] = var_data.values
            # outarray[idx, UngriddedData._DATAHEIGHTINDEX] = ?? Unused ??
            outarray[idx, UngriddedData._DATAERRINDEX] = var_data.standard_deviations
            outarray[idx, UngriddedData._DATAFLAGINDEX] = var_data.flags  # Only counts if non-NaN?
            # outarray[idx, UngriddedData._STOPTIMEINDEX] = var_data.end_times # Seems unused?
            # outarray[idx, UngriddedData._TRASHINDEX]  # No need to set, only non-NaN values are considered trash
            

        metadata = {k: v for k, v in station_metadata.items()}

        meta_idx = dict()
        for station_key in station_metadata.keys():
            d = dict()
            for var_key, var_val in var_metadata.items():
                mask = (outarray[:, UngriddedData._METADATAKEYINDEX] == station_key) & (outarray[:, UngriddedData._VARINDEX] == var_key)
                indices = np.flatnonzero(mask)
                if len(indices) == 0:
                    continue
                d[var_val] = indices
            meta_idx[station_key] = d

        var_idx = {v: k for k, v, in var_metadata.items()}

        return UngriddedData._from_raw_parts(outarray, metadata, meta_idx, var_idx)


    def _get_metadata_from_pyaro(self, station: Station) -> list[dict[str, str]]:
        metadata = dict(
            instrument_name=None,
            data_revision="n/d",
            PI=None,
            filename=None,
            country_code=station["country"],
            data_level=None,
            revision_date=None,
            website=None,
            data_product=None,
            data_version=None,
            framework=None,
            instr_vert_loc=None,
            stat_merge_pref_attr=None,
        )
        for key in metadata:
            if key in station.keys():
                metadata[key] = station[key]

        return metadata

    def _get_additional_metadata(self, station: Station) -> list[dict[str, str]]:
        return station.metadata

    def _make_single_ungridded_metadata(
        self, station: Station, name: str, ts_type: TsType | None, units: dict[str, str]
    ) -> MetadataEntry:
        entry = dict(
            data_id=self.config.name,
            variables=list(self.get_variables()),
            var_info=units,
            latitude=station["latitude"],
            longitude=station["longitude"],
            altitude=station["altitude"],
            station_name=station["long_name"],
            station_id=name,
            country=station["country"],
            ts_type=str(ts_type) if ts_type is not None else "undefined",
        )
        entry.update(self._get_metadata_from_pyaro(station=station))
        entry.update(self._get_additional_metadata(station=station))

        return MetadataEntry(entry)

    def _pyaro_dataline_to_ungriddeddata_dataline(
        self, data: np.void, idx: int, var_idx: int
    ) -> np.ndarray:
        new_data = np.zeros(12)
        new_data[self._METADATAKEYINDEX] = idx
        new_data[self._TIMEINDEX] = data["start_times"]
        new_data[self._LATINDEX] = data["latitudes"]
        new_data[self._LONINDEX] = data["longitudes"]
        new_data[self._ALTITUDEINDEX] = data["altitudes"]
        new_data[self._VARINDEX] = var_idx
        new_data[self._DATAINDEX] = data["values"]
        new_data[self._DATAHEIGHTINDEX] = np.nan
        new_data[self._DATAERRINDEX] = data["standard_deviations"]
        new_data[self._DATAFLAGINDEX] = data["flags"]
        new_data[self._STOPTIMEINDEX] = data["end_times"]
        new_data[self._TRASHINDEX] = np.nan

        return new_data

    def _calculate_ts_type(self, start: np.datetime64, stop: np.datetime64) -> TsType:
        seconds = (stop - start).astype("timedelta64[s]").astype(np.int32)
        if seconds == 0:
            ts_type = TsType("hourly")
        else:
            ts_type = TsType.from_total_seconds(seconds)

        return ts_type

    def _add_ts_type_to_metadata(
        self, metadata: Metadata, ts_types: dict[str, TsType | None]
    ) -> Metadata:
        new_metadata: Metadata = deepcopy(metadata)
        for idx in new_metadata:
            station_name = new_metadata[idx]["station_name"]
            ts_type = str(ts_types[station_name])
            new_metadata[idx]["ts_type"] = ts_type if ts_type is not None else "undefined"
        return new_metadata

    def get_variables(self) -> list[str]:
        return self.reader.variables()

    def get_stations(self) -> dict[str, Station]:
        return self.reader.stations()

    def read(self, vars_to_retrieve=None) -> UngriddedData:
        allowed_vars = self.get_variables()
        if vars_to_retrieve is None:
            vars_to_retrieve = allowed_vars
        else:
            if isinstance(vars_to_retrieve, str):
                vars_to_retrieve = [vars_to_retrieve]

        data = {}
        for var in vars_to_retrieve:
            if var not in allowed_vars:
                logger.warning(
                    f"Variable {var} not in list over allowed variabes for {self.config.data_id}: {allowed_vars}"
                )
                continue

            data[var] = self.reader.data(varname=var)

        return self._convert_to_ungriddeddata(data)

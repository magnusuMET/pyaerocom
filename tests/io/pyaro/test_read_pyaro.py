from __future__ import annotations

import pandas as pd
import numpy as np

from pyaerocom import UngriddedData
from pyaerocom.io import ReadPyaro, PyaroConfig
from pyaerocom.io.pyaro.read_pyaro import PyaroToUngriddedData
from pyaerocom.io.pyaro.postprocess import matching_indices

from tests.conftest import lustre_unavail


def test_testfile(pyaro_test_data_file):
    assert pyaro_test_data_file.exists()


def test_readpyaro(pyaro_testdata):
    rp = pyaro_testdata

    assert isinstance(rp, ReadPyaro)


def test_variables(pyaro_testdata):
    rp = pyaro_testdata
    variables = ["NOx", "concso4", "od550aer", "NO"]

    assert rp.PROVIDES_VARIABLES == variables
    assert rp.DEFAULT_VARS == variables


####################################################
#   Tests for the helper class PyaroToUngriddedData
####################################################


def test_pyarotoungriddeddata_reading(pyaro_testdata):
    from math import ceil

    obj = pyaro_testdata.converter
    data = obj.read()
    assert isinstance(data, UngriddedData)

    # Checks is data is empty
    assert not data.is_empty
    assert len(data.unique_station_names) == 2

    # Tests the found stations
    all_stations = data.to_station_data_all("concso4", ts_type_preferred="daily")

    assert all_stations["stats"][0]["ts_type"] in ["hourly", "3daily", "2hourly", "2daily"]
    assert all_stations["stats"][0]["country"] == "NO"

    # Tests the dates
    start = pd.to_datetime("01.01.2010", dayfirst=True)
    end = pd.to_datetime("31.12.2010", dayfirst=True)
    dates = pd.date_range(start, end, freq="D")
    assert len(all_stations["stats"][0].dtime) == ceil(len(dates) / 2)


def test_pyarotoungriddeddata_reading_kwargs(pyaro_testdata_kwargs):
    obj = pyaro_testdata_kwargs.converter
    data = obj.read()
    assert isinstance(data, UngriddedData)

    # Checks if stations have correct countries
    all_stations = data.to_station_data_all("concso4")
    countries = ["NO", "GB"]
    assert all_stations["stats"][1]["country"].strip() == countries[0]
    assert all_stations["stats"][0]["country"].strip() == countries[1]


def test_pyarotoungriddeddata_reading_extra_metadata(pyaro_testdata_kwargs):
    obj = pyaro_testdata_kwargs.converter
    data = obj.read()
    assert isinstance(data, UngriddedData)

    # Checks if stations have correct countries
    all_stations = data.to_station_data_all("concso4", add_meta_keys=["area_classification"])
    area_type = ["Rural", "Urban"]
    assert all_stations["stats"][1]["area_classification"].strip() == area_type[0]
    assert all_stations["stats"][0]["area_classification"].strip() == area_type[1]


def test_pyarotoungriddeddata_stations(pyaro_testdata):
    obj = pyaro_testdata.converter

    assert len(obj.get_stations()) == 2


def test_pyarotoungriddeddata_variables(pyaro_testdata):
    obj = pyaro_testdata.converter

    assert obj.get_variables() == pyaro_testdata.PROVIDES_VARIABLES


def test_postprocessing(pyaro_test_data_file):
    config = PyaroConfig(
        reader_id="csv_timeseries",
        filename_or_obj_or_url=str(pyaro_test_data_file),
        name="test",
        name_map={
            "NO": "concno",
        },
        post_processing=[
            "concNno_from_concno",
        ],
        filters=dict(),
    )
    reader = ReadPyaro(config)
    assert set(reader.PROVIDES_VARIABLES).issuperset(["concno", "concNno"])
    data = reader.read(["concno", "concNno"])

    concno = data.all_datapoints_var("concno")
    concNno = data.all_datapoints_var("concNno")

    # Proportion of N in NO, ng -> ug conversion
    conversion_factor = 14.006 / (14.006 + 15.999) * 1e-3

    assert np.allclose(concno * conversion_factor, concNno)


def test_matching_indices():
    x = [0, 1, 2, 3, 4]
    y = [1, 1.5, 2, 2.1, 4, 5]

    xind, yind = matching_indices(x, y)

    assert np.all(xind == [1, 2, 4])
    assert np.all(yind == [0, 2, 4])


@lustre_unavail
def test_vmrox():
    config = PyaroConfig.from_dict(
        {
            "name": "whatever",
            "reader_id": "eeareader",
            "filename_or_obj_or_url": "/lustre/storeB/project/aerocom/aerocom1/AEROCOM_OBSDATA/EEA-AQDS/download",
            "filters": {
                "countries": {"include": ["NO"]},
            },
            "name_map": {
                "O3": "conco3",
                "NO2": "concno2",
            },
            "post_processing": [
                "vmro3_from_conco3",
                "vmrno2_from_concno2",
                "vmrox_from_vmrno2_vmro3",
            ],
            "dataset": "unverified",
        }
    )
    reader = PyaroToUngriddedData(config)
    data = reader.read(vars_to_retrieve=["vmrox"])

    _ = data.to_station_data_all()

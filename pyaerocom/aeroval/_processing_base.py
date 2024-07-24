import abc

from pyaerocom._lowlevel_helpers import TypeValidator
from pyaerocom.aeroval import EvalSetup
from pyaerocom.aeroval.experiment_output import ExperimentOutput
from pyaerocom.aeroval.json_utils import round_floats
from pyaerocom.colocation.colocated_data import ColocatedData
from pyaerocom.colocation.colocation_setup import ColocationSetup
from pyaerocom.colocation.colocator import Colocator
from pyaerocom.utils import recursive_defaultdict


class HasConfig:
    """
    Base class that ensures that evaluation configuration is available

    Attributes
    ----------
    cfg : EvalSetup
        AeroVal experiment setup
    exp_output : ExperimentOutput
        Manages output for an AeroVal experiment (e.g. path locations).

    """

    cfg = TypeValidator(EvalSetup)
    exp_output = TypeValidator(ExperimentOutput)

    def __init__(self, cfg: EvalSetup):
        self.cfg = cfg
        self.exp_output = ExperimentOutput(cfg)
        self.avdb = self.exp_output.avdb

    @property
    def raise_exceptions(self):
        return self.cfg.colocation_opts.raise_exceptions

    @property
    def reanalyse_existing(self):
        return self.cfg.colocation_opts.reanalyse_existing


class ProcessingEngine(HasConfig, abc.ABC):
    """
    Abstract base for classes supposed to do one or more processing tasks

    Requirement for a processing class is to inherit attrs from
    :class:`HasConfig` and, in addition to that, to have implemented a method
    :fun:`run` which is running the corresponding processing task and storing
    all the associated output files, that are read by the frontend.

    One example of an implementation is the
    :class:`pyaerocom.aeroval.modelmaps_engine.ModelMapsEngine`.
    """

    @abc.abstractmethod
    def run(self, *args, **kwargs) -> list:
        """
        Method that runs the processing based on settings in :attr:`cfg`

        Parameters
        ----------
        *args
            positional arguments.
        **kwargs
            Keyword arguments.

        Returns
        -------
        list
            list of output file paths generated by the engine.

        """
        pass

    def _add_heatmap_timeseries_entry(
        self,
        entry: dict,
        region: str,
        network: str,
        obsvar: str,
        layer: str,
        modelname: str,
        modvar: str,
    ):
        """Adds a heatmap entry to hm/ts

        :param entry: The entry to be added.
        :param network: Observation network
        :param obsvar: Observation variable
        :param layer: Vertical layer
        :param modelname: Model name
        :param modvar: Model variable
        """
        project = self.exp_output.proj_id
        experiment = self.exp_output.exp_id

        with self.avdb.lock():
            glob_stats = self.avdb.get_heatmap_timeseries(
                project, experiment, region, network, obsvar, layer, default={}
            )
            glob_stats = recursive_defaultdict(glob_stats)
            glob_stats[obsvar][network][layer][modelname][modvar] = round_floats(entry)
            self.avdb.put_heatmap_timeseries(
                glob_stats,
                project,
                experiment,
                region,
                network,
                obsvar,
                layer,
            )

    def _add_forecast_entry(
        self,
        entry: dict,
        region: str,
        network: str,
        obsvar: str,
        layer: str,
        modelname: str,
        modvar: str,
    ):
        """Adds a forecast entry to forecast

        :param entry: The entry to be added.
        :param network: Observation network
        :param obsvar: Observation variable
        :param layer: Vertical layer
        :param modelname: Model name
        :param modvar: Model variable
        """
        project = self.exp_output.proj_id
        experiment = self.exp_output.exp_id

        with self.avdb.lock():
            glob_stats = self.avdb.get_forecast(
                project, experiment, region, network, obsvar, layer, default={}
            )
            glob_stats = recursive_defaultdict(glob_stats)
            glob_stats[obsvar][network][layer][modelname][modvar] = round_floats(entry)
            self.avdb.put_forecast(
                glob_stats,
                project,
                experiment,
                region,
                network,
                obsvar,
                layer,
            )

    def _add_heatmap_entry(
        self,
        entry,
        frequency: str,
        network: str,
        obsvar: str,
        layer: str,
        modelname: str,
        modvar: str,
    ):
        """Adds a heatmap entry to glob_stats

        :param entry: The entry to be added.
        :param region: The region (eg. ALL)
        :param obsvar: Observation variable.
        :param layer: Vertical Layer (eg. SURFACE)
        :param modelname: Model name
        :param modelvar: Model variable.
        """
        project = self.exp_output.proj_id
        experiment = self.exp_output.exp_id

        with self.avdb.lock():
            glob_stats = self.avdb.get_glob_stats(project, experiment, frequency, default={})
            glob_stats = recursive_defaultdict(glob_stats)
            glob_stats[obsvar][network][layer][modelname][modvar] = round_floats(entry)
            self.avdb.put_glob_stats(glob_stats, project, experiment, frequency)

    def _write_station_data(self, data):
        """Writes timeseries weekly.

        :param data: Data to be written.
        """
        project = self.exp_output.proj_id
        experiment = self.exp_output.exp_id

        location = data["station_name"]
        network = data["obs_name"]
        obsvar = data["var_name_web"]
        layer = data["vert_code"]
        modelname = data["model_name"]
        with self.avdb.lock():
            station_data = self.avdb.get_timeseries_weekly(
                project, experiment, location, network, obsvar, layer, default={}
            )
            station_data[modelname] = round_floats(data)
            self.avdb.put_timeseries_weekly(
                station_data, project, experiment, location, network, obsvar, layer
            )

    def _write_timeseries(self, data):
        """Write timeseries"""
        if not isinstance(data, list):
            data = [data]

        project = self.exp_output.proj_id
        experiment = self.exp_output.exp_id
        with self.avdb.lock():
            for d in data:
                location = d["station_name"]
                network = d["obs_name"]
                obsvar = d["var_name_web"]
                layer = d["vert_code"]
                modelname = d["model_name"]

                timeseries = self.avdb.get_timeseries(
                    project, experiment, location, network, obsvar, layer, default={}
                )
                timeseries[modelname] = round_floats(d)
                self.avdb.put_timeseries(
                    timeseries, project, experiment, location, network, obsvar, layer
                )

    def _add_profile_entry(
        self, data: ColocatedData, profile_viz: dict, periods: list[str], seasons: list[str]
    ):
        with self.avdb.lock():
            current = self.avdb.get_profiles(
                self.exp_output.proj_id, self.exp_output.exp_id, default={}
            )
            current = recursive_defaultdict(current)

            for freq, coldata in data.items():
                model_name = coldata.model_name

                midpoint = (
                    float(coldata.data.attrs["vertical_layer"]["end"])
                    + float(coldata.data.attrs["vertical_layer"]["start"])
                ) / 2
                if not "z" in current[model_name]:
                    current[model_name]["z"] = [midpoint]  # initalize with midpoint

                if (
                    midpoint > current[model_name]["z"][-1]
                ):  # only store incremental increases in the layers
                    current[model_name]["z"].append(midpoint)

                for per in periods:
                    for season in seasons:
                        perstr = f"{per}-{season}"

                        if not perstr in current[model_name]["obs"][freq]:
                            current[model_name]["obs"][freq][perstr] = []
                        if not perstr in current[model_name]["mod"][freq]:
                            current[model_name]["mod"][freq][perstr] = []

                        current[model_name]["obs"][freq][perstr].append(
                            profile_viz["obs"][freq][perstr]
                        )
                        current[model_name]["mod"][freq][perstr].append(
                            profile_viz["mod"][freq][perstr]
                        )

                if not "metadata" in current[model_name]:
                    current[model_name]["metadata"] = {
                        "z_unit": coldata.data.attrs["altitude_units"],
                        "z_description": "Altitude ASL",
                        "z_long_description": "Altitude Above Sea Level",
                        "unit": coldata.unitstr,
                    }
                current[model_name] = round_floats(current[model_name])

            self.avdb.put_profiles(current, self.exp_output.proj_id, self.exp_output.exp_id)


class HasColocator(HasConfig):
    """
    Config class that also has the ability to co-locate
    """

    def _get_diurnal_only(self, obs_name):
        """
        Check if colocated data is flagged for only diurnal processing

        Parameters
        ----------
        obs_name : string
            Name of observational subset
        colocated_data : ColocatedData
            A ColocatedData object that will be checked for suitability of
            diurnal processing.

        Returns
        -------
        diurnal_only : bool
        """
        entry = self.cfg.get_obs_entry(obs_name)
        try:
            diurnal_only = entry["diurnal_only"]
        except KeyError:
            diurnal_only = False
        return diurnal_only

    def get_colocator(self, model_name: str = None, obs_name: str = None) -> Colocator:
        """
        Instantiate colocation engine

        Parameters
        ----------
        model_name : str, optional
            name of model. The default is None.
        obs_name : str, optional
            name of obs. The default is None.

        Returns
        -------
        Colocator

        """
        col_cfg = {**self.cfg.colocation_opts.model_dump()}
        outdir = self.cfg.path_manager.get_coldata_dir()
        col_cfg["basedir_coldata"] = outdir

        if not model_name and not obs_name:
            col_stp = ColocationSetup(**col_cfg)
            return Colocator(col_stp)

        if model_name:
            mod_cfg = self.cfg.get_model_entry(model_name)
            col_cfg["model_cfg"] = mod_cfg

            # LB: Hack and at what lowlevel_helpers's import_from was doing
            for key, val in mod_cfg.items():
                if key in ColocationSetup.model_fields:
                    col_cfg[key] = val
        if obs_name:
            obs_cfg = self.cfg.get_obs_entry(obs_name)
            pyaro_config = obs_cfg["obs_config"] if "obs_config" in obs_cfg else None
            col_cfg["obs_config"] = pyaro_config

            # LB: Hack and at what lowlevel_helpers's import_from was doing
            for key, val in obs_cfg.items():
                if key in ColocationSetup.model_fields:
                    col_cfg[key] = val

            col_cfg["add_meta"].update(diurnal_only=self._get_diurnal_only(obs_name))

        col_stp = ColocationSetup(**col_cfg)
        col = Colocator(col_stp)

        return col


class DataImporter(HasColocator):
    """
    Class that supports reading of model and obs data based on an eval config.

    Depending on a :class:`EvalSetup`, reading of model and obs data may have
    certain constraints (e.g. freq, years, alias variable names, etc.), which
    are / can be specified flexibly for each model and obs entry in an
    analysis setup (:class:`EvalSetup`). Proper handling of these reading
    constraints and data import settings are handled in the
    :class:`pyaerocom.colocation_auto.Colocator` engine, therefore the reading
    in this class is done via the :class:`Colocator` engine.


    """

    def read_model_data(self, model_name, var_name):
        """
        Import model data

        Parameters
        ----------
        model_name : str
            Name of model in :attr:`cfg`,
        var_name : str
            Name of variable to be read.

        Returns
        -------
        data : GriddedData
            loaded model data.

        """
        col = self.get_colocator(model_name=model_name)
        data = col.get_model_data(var_name)

        return data

    def read_ungridded_obsdata(self, obs_name, var_name):
        """
        Import ungridded observation data

        Parameters
        ----------
        obs_name : str
            Name of observation network in :attr:`cfg`
        var_name : str
            Name of variable to be read.

        Returns
        -------
        data : UngriddedData
            loaded obs data.

        """

        col = self.get_colocator(obs_name=obs_name)

        data = col._read_ungridded(var_name)
        return data

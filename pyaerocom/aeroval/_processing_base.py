import abc

from pyaerocom._lowlevel_helpers import TypeValidator
from pyaerocom.aeroval import EvalSetup
from pyaerocom.aeroval.experiment_output import ExperimentOutput
from pyaerocom.colocation.colocation_setup import ColocationSetup
from pyaerocom.colocation.colocator import Colocator


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
        return self.cfg.get_obs_entry(obs_name).get("diurnal_only", False)

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
    :class:`pyaerocom.colocation.Colocator` engine, therefore the reading
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

    def read_gridded_obsdata(self, obs_name, var_name):
        """
        Import gridded observation data, usually satellite data

        Args:
            obs_name (str): Name of observation network in :attr:`cfg`
            var_name (str): Name of variable to be read.
        """
        col = self.get_colocator(obs_name=obs_name)
        data = col._read_gridded(var_name, is_model=False)
        return data

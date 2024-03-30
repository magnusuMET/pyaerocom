from __future__ import annotations
import logging
import os
from getpass import getuser

from pyaerocom import __version__, const
from pyaerocom._lowlevel_helpers import (
    AsciiFileLoc,
    DirLoc,
)
from pyaerocom.aeroval.aux_io_helpers import ReadAuxHandler
from pyaerocom.aeroval.collections import ModelCollection, ObsCollection
from pyaerocom.aeroval.helpers import _check_statistics_periods, _get_min_max_year_periods
from pyaerocom.aeroval.json_utils import read_json, set_float_serialization_precision, write_json
from pyaerocom.colocation_auto import ColocationSetup
from pyaerocom.exceptions import AeroValConfigError

from pydantic import (
    BaseModel,
    ConfigDict,
    computed_field,
    field_validator,
    field_serializer,
    PositiveInt,
)
from dataclasses import field
from typing import Optional, Literal

from pathlib import Path

logger = logging.getLogger(__name__)


class OutputPaths(BaseModel):
    """
    Setup class for output paths of json files and co-located data

    This interface generates all paths required for an experiment.

    Attributes
    ----------
    proj_id : str
        project ID
    exp_id : str
        experiment ID
    json_basedir : str

    """

    # Pydantic ConfigDict
    model_config = ConfigDict(arbitrary_types_allowed=True)

    JSON_SUBDIRS: list[str] = [
        "map",
        "ts",
        "ts/diurnal",
        "scat",
        "hm",
        "hm/ts",
        "contour",
        "profiles",
    ]

    json_basedir: Path | str = os.path.join(const.OUTPUTDIR, "aeroval/data")
    coldata_basedir: Path | str = os.path.join(const.OUTPUTDIR, "aeroval/coldata")

    @field_validator("json_basedir", "coldata_basedir")
    def validate_basedirs(cls, v):
        if not os.path.exists(v):
            tmp = Path(v) if isinstance(v, str) else v
            tmp.mkdir(parents=True, exist_ok=True)
        return v

    ADD_GLOB: list[str] = ["coldata_basedir", "json_basedir"]

    proj_id: str
    exp_id: str

    def _check_init_dir(self, loc, assert_exists):
        if assert_exists and not os.path.exists(loc):
            os.makedirs(loc)
        return loc

    def get_coldata_dir(self, assert_exists=True):
        loc = os.path.join(self.coldata_basedir, self.proj_id, self.exp_id)
        return self._check_init_dir(loc, assert_exists)

    def get_json_output_dirs(self, assert_exists=True):
        out = {}
        base = os.path.join(self.json_basedir, self.proj_id, self.exp_id)
        for subdir in self.JSON_SUBDIRS:
            loc = self._check_init_dir(os.path.join(base, subdir), assert_exists)
            out[subdir] = loc
        return out


class ModelMapsSetup(BaseModel):
    maps_freq: Literal["monthly", "yearly"] = "monthly"
    maps_res_deg: PositiveInt = 5


class StatisticsSetup(BaseModel, extra="allow"):
    """
    Setup options for statistical calculations

    Attributes
    ----------
    weighted_stats : bool
        if True, statistics are calculated using area weights,
        this is only relevant for gridded / gridded evaluations.
    annual_stats_constrained : bool
        if True, then only sites are considered that satisfy a potentially
        specified annual resampling constraint (see
        :attr:`pyaerocom.colocation_auto.ColocationSetup.min_num_obs`). E.g.

        lets say you want to calculate statistics (bias,
        correlation, etc.) for monthly model / obs data for a given site and
        year. Lets further say, that there are only 8 valid months of data, and
        4 months are missing, so statistics will be calculated for that year
        based on 8 vs. 8 values. Now if
        :attr:`pyaerocom.colocation_auto.ColocationSetup.min_num_obs` is
        specified in way that requires e.g. at least 9 valid months to
        represent the whole year, then this station will not be considered in
        case `annual_stats_constrained` is True, else it will. Defaults to
        False.
    stats_tseries_base_freq : str, optional
        The statistics Time Series display in AeroVal (under Overall Evaluation)
        is computed in intervals of a certain frequency, which is specified
        via :attr:`TimeSetup.main_freq` (defaults to monthly). That is,
        monthly colocated data is used as a basis to compute the statistics
        for each month (e.g. if you have 10 sites, then statistics will be
        computed based on 10 monthly values for each month of the timeseries,
        1 value for each site). `stats_tseries_base_freq` may be specified in
        case a higher resolution is supposed to be used as a basis to compute
        the timeseries in the resolution specified by
        :attr:`TimeSetup.main_freq` (e.g. if daily is specified here, then for
        the above example 310 values would be used - 31 for each site - to
        compute the statistics for a given month (in this case, a month with 31
        days, obviously).
    drop_stats: tuple, optional
        tuple of strings with names of statistics (as determined by keys in
        aeroval.glob_defaults.py's statistics_defaults) to not compute. For example,
        setting drop_stats = ("mb", "mab"), results in json files in hm/ts with
        entries which do not contain the mean bias and mean absolute bias,
        but the other statistics are preserved.
    stats_decimals: int, optional
        If provided, overwrites the decimals key in glod_defaults for the statistics, which has a deault of 3.
        Setting this higher of lower changes the number of decimals shown on the Aeroval webpage.
    round_floats_precision: int, optional
        Sets the precision argument for the function `pyaerocom.aaeroval.json_utils:set_float_serialization_precision`


    Parameters
    ----------
    kwargs
        any of the supported attributes, e.g.
        `StatisticsSetup(annual_stats_constrained=True)`

    """

    MIN_NUM: PositiveInt = 1
    weighted_stats: bool = True
    annual_stats_constrained: bool = False
    add_trends: bool = False
    trends_min_yrs: PositiveInt = 7
    stats_tseries_base_freq: str | None = None
    use_fairmode: bool = False
    use_diurnal: bool = False
    obs_only_stats: bool = False
    only_stats_for_model: bool = False  # LB: casues namespace conflicts. see if way around
    drop_stats: tuple[str, ...] = ()
    stats_decimals: int | None = None
    round_floats_precision: Optional[int] = None

    if round_floats_precision:
        set_float_serialization_precision(round_floats_precision)


class TimeSetup(BaseModel):

    DEFAULT_FREQS: Literal["monthly", "yearly"] = "monthly"
    SEASONS: list[str] = ["all", "DJF", "MAM", "JJA", "SON"]
    main_freq: str = "monthly"
    freqs: list[str] = ["monthly", "yearly"]
    periods: list[str] = []
    add_seasons: bool = True

    def get_seasons(self):
        """
        Get list of seasons to be analysed

        Returns :attr:`SEASONS` if :attr:`add_seasons` it True, else `[
        'all']` (only whole year).

        Returns
        -------
        list
            list of season strings for analysis

        """
        if self.add_seasons:
            return self.SEASONS
        return ["all"]

    def _get_all_period_strings(self):
        """
        Get list of all period strings for evaluation

        Returns
        -------
        list
            list of period / season strings
        """
        output = []
        for per in self.periods:
            for season in self.get_seasons():
                perstr = f"{per}-{season}"
                output.append(perstr)
        return output


class WebDisplaySetup(BaseModel):
    # Pydantic ConfigDict
    model_config = ConfigDict()
    model_config["protected_namespaces"] = ()
    # WebDisplaySetup attributes
    map_zoom: Literal["World", "Europe", "xEMEP"] = "World"
    regions_how: Literal["default", "aerocom", "htap", "country"] = "default"
    map_zoom: str = "World"
    add_model_maps: bool = False
    modelorder_from_config: bool = True
    obsorder_from_config: bool = True
    var_order_menu: tuple[str, ...] = ()
    obs_order_menu: tuple[str, ...] = ()
    model_order_menu: tuple[str, ...] = ()
    hide_charts: tuple[str, ...] = ()
    hide_pages: tuple[str, ...] = ()
    ts_annotations: dict[str, str] = field(default_factory=dict)
    add_pages: tuple[str, ...] = ()


class EvalRunOptions(BaseModel):

    clear_existing_json: bool = True
    only_json: bool = False
    only_colocation: bool = False
    #: If True, process only maps (skip obs evaluation)
    only_model_maps: bool = False
    obs_only: bool = False


class ProjectInfo(BaseModel):
    proj_id: str


class ExperimentInfo(BaseModel):
    exp_id: str
    exp_name: str = ""
    exp_descr: str = ""
    public: bool = False
    exp_pi: str = getuser()
    pyaerocom_version: str = __version__


class EvalSetup(BaseModel):
    """Composite class representing a whole analysis setup

    This represents the level at which json I/O happens for configuration
    setup files.
    """

    # Pydantic ConfigDict
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow", protected_namespaces=())

    IGNORE_JSON: list[str] = ["_aux_funs"]
    ADD_GLOB: list[str] = ["io_aux_file"]
    # # LB: will need to address
    io_aux_file: AsciiFileLoc | str = AsciiFileLoc(
        default="",
        assert_exists=False,
        auto_create=False,
        logger=logger,
        tooltip=".py file containing additional read methods for modeldata",
    )
    # io_aux_file : Path
    _aux_funs: dict = {}

    proj_id: str
    exp_id: str

    @computed_field
    @property
    def proj_info(self) -> ProjectInfo:
        return ProjectInfo(proj_id=self.proj_id)

    @computed_field
    @property
    def exp_info(self) -> ExperimentInfo:
        return ExperimentInfo(exp_id=self.exp_id)

    @computed_field
    @property
    def path_manager(self) -> OutputPaths:
        if hasattr(self, "model_extra") & bool(
            cfg_extra_keys := set(self.model_extra).intersection(set(OutputPaths.model_fields))
        ):
            subset_dict = {k: self.model_extra[k] for k in cfg_extra_keys}
            return OutputPaths(proj_id=self.proj_id, exp_id=self.exp_id, **subset_dict)
        else:
            return OutputPaths(proj_id=self.proj_id, exp_id=self.exp_id)

    # This is an attempt at a hack to get keys from a general CFG into their appropriate respective classes
    # It's hard to come up with a way to do this that doesn't introduce breaking changes
    # Introducing breaking changes only seems appropriate after a config format is settled.
    # Note: all these computed fields could be more easily defined if the config were
    # rigid enough to have they explicitly defined (e.g., in a TOML file), rather than dumping everything
    # into one large config dict and then dishing out get the relevant parts to each class.
    @computed_field
    @property
    def time_cfg(self) -> TimeSetup:
        if hasattr(self, "model_extra") & bool(
            time_cfg_keys := set(self.model_extra).intersection(set(TimeSetup.model_fields))
        ):
            subset_dict = {k: self.model_extra[k] for k in time_cfg_keys}
            return TimeSetup(**subset_dict)
        else:
            return TimeSetup()

    @computed_field
    @property
    def modelmaps_opts(self) -> ModelMapsSetup:
        if hasattr(self, "model_extra") & bool(
            cfg_extra_keys := set(self.model_extra).intersection(set(ModelMapsSetup.model_fields))
        ):
            subset_dict = {k: self.model_extra[k] for k in cfg_extra_keys}
            return ModelMapsSetup(**subset_dict)
        else:
            return ModelMapsSetup()

    # # Etc. etc... could do above many times. Is there a way to do it with an update function??
    # def _update(self, obj: Generic[T]) -> Generic[T]:
    #     if hasattr(self, "model_extra"):
    #         extra_obj_cfg_keys = set(self.model_extra).intersection(set(obj.__fields__))
    #         if extra_obj_cfg_keys:
    #             subset_dict = {k: self.model_extra[k] for k in extra_obj_cfg_keys}
    #             return obj(**subset_dict)
    #         else:
    #             return obj()
    #     else:
    #         return obj()

    # TODO: Use Pydantic for ColocationSetup
    @computed_field
    @property
    def colocation_opts(self) -> ColocationSetup:
        if hasattr(self, "model_extra") & bool(
            cfg_extra_keys := set(self.model_extra).intersection(
                set(ColocationSetup().__dict__.keys())
            )
        ):
            subset_dict = {k: self.model_extra[k] for k in cfg_extra_keys}
            # need to pass some default values to the ColocationSetup if not provided in config
            default_dict = {"save_coldata": True, "keep_data": False, "resample_how": "mean"}
            for key in default_dict:
                if key not in subset_dict:
                    subset_dict[key] = default_dict[key]

            return ColocationSetup(**subset_dict)
        else:
            return ColocationSetup(save_coldata=True, keep_data=False, resample_how="mean")

    @field_serializer("colocation_opts")
    def serialize_colocation_opts(self, colocation_opts: ColocationSetup):
        return colocation_opts.json_repr()

    @computed_field
    @property
    def webdisp_opts(self) -> WebDisplaySetup:
        if hasattr(self, "model_extra") & bool(
            cfg_extra_keys := set(self.model_extra).intersection(set(WebDisplaySetup.model_fields))
        ):
            subset_dict = {k: self.model_extra[k] for k in cfg_extra_keys}
            return WebDisplaySetup(**subset_dict)
        else:
            return WebDisplaySetup()

    @computed_field
    @property
    def processing_opts(self) -> EvalRunOptions:
        if hasattr(self, "model_extra") & bool(
            cfg_extra_keys := set(self.model_extra).intersection(set(EvalRunOptions.model_fields))
        ):
            subset_dict = {k: self.model_extra[k] for k in cfg_extra_keys}
            return EvalRunOptions(**subset_dict)
        else:
            return EvalRunOptions()

    var_web_info: dict = {}

    @computed_field
    @property
    def statistics_opts(self) -> StatisticsSetup:
        if hasattr(self, "model_extra") & bool(
            cfg_extra_keys := set(self.model_extra).intersection(set(StatisticsSetup.model_fields))
        ):
            subset_dict = {k: self.model_extra[k] for k in cfg_extra_keys}
            return StatisticsSetup(**subset_dict)
        else:
            return StatisticsSetup(weighted_stats=True, annual_stats_constrained=False)

    # ObsCollection and ModelCollection require special attention b/c they're not based on Pydantic.
    # TODO Use Pydantic for ObsCollection and ModelCollection
    obs_cfg: ObsCollection | dict = ObsCollection()

    @field_validator("obs_cfg")
    def validate_obs_cfg(cls, v):
        if not isinstance(v, ObsCollection):
            return ObsCollection(v)
        return v

    @field_serializer("obs_cfg")
    def serialize_obs_cfg(self, obs_cfg: ObsCollection):
        return obs_cfg.json_repr()

    model_cfg: ModelCollection | dict = ModelCollection()

    @field_validator("model_cfg")
    def validate_model_cfg(cls, v):
        if not isinstance(v, ModelCollection):
            return ModelCollection(v)
        return v

    @field_serializer("model_cfg")
    def serialize_model_cfg(self, model_cfg: ModelCollection):
        return model_cfg.json_repr()

    @property
    def json_filename(self) -> str:
        """
        str: Savename of config file: cfg_<proj_id>_<exp_id>.json
        """
        return f"cfg_{self.proj_id}_{self.exp_id}.json"

    @property
    def gridded_aux_funs(self) -> dict:
        if not bool(self._aux_funs) and os.path.exists(self.io_aux_file):
            self._import_aux_funs()
        return self._aux_funs

    def get_obs_entry(self, obs_name) -> dict:
        return self.obs_cfg.get_entry(obs_name).to_dict()

    def get_model_entry(self, model_name) -> dict:
        """Get model entry configuration

        Since the configuration files for experiments are in json format, they
        do not allow the storage of executable custom methods for model data
        reading. Instead, these can be specified in a python module that may
        be specified via :attr:`add_methods_file` and that contains a
        dictionary `FUNS` that maps the method names with the callable methods.

        As a result, this means that, by default, custom read methods for
        individual models in :attr:`model_config` do not contain the
        callable methods but only the names. This method will take care of
        handling this and will return a dictionary where potential custom
        method strings have been converted to the corresponding callable
        methods.

        Parameters
        ----------
        model_name : str
            name of model

        Returns
        -------
        dict
            Dictionary that specifies the model setup ready for the analysis
        """
        cfg = self.model_cfg.get_entry(model_name)
        cfg = cfg.prep_dict_analysis(self.gridded_aux_funs)
        return cfg

    def to_json(self, outdir: str, ignore_nan: bool = True, indent: int = 3) -> None:
        """
        Save configuration as JSON file

        Parameters
        ----------
        outdir : str
            directory where the config json file is supposed to be stored
        ignore_nan : bool
            set NaNs to Null when writing
        indent : int
            json indentation

        """
        filepath = os.path.join(outdir, self.json_filename)
        data = self.json_repr()
        write_json(data, filepath, ignore_nan=ignore_nan, indent=indent)
        return filepath

    @staticmethod
    def from_json(filepath: str) -> EvalSetup:
        """Load configuration from json config file"""
        settings = read_json(filepath)
        return EvalSetup(**settings)

    def json_repr(self):
        return self.model_dump()

    def _import_aux_funs(self) -> None:
        h = ReadAuxHandler(self.io_aux_file)
        self._aux_funs.update(**h.import_all())

    def _check_time_config(self) -> None:
        periods = self.time_cfg.periods
        colstart = self.colocation_opts["start"]
        colstop = self.colocation_opts["stop"]

        if len(periods) == 0:
            if colstart is None:
                raise AeroValConfigError("Either periods or start must be set...")
            per = self.colocation_opts._period_from_start_stop()
            periods = [per]
            logger.info(
                f"periods is not set, inferred {per} from start / stop colocation settings."
            )

        self.time_cfg.periods = _check_statistics_periods(periods)
        start, stop = _get_min_max_year_periods(periods)
        if colstart is None:
            self.colocation_opts["start"] = start
        if colstop is None:
            self.colocation_opts["stop"] = (
                stop + 1
            )  # add 1 year since we want to include stop year

from copy import deepcopy

import pytest

from pyaerocom.aeroval.setupclasses import EvalSetup
from pyaerocom.exceptions import EvalEntryNameError
from tests.fixtures.aeroval.cfg_test_exp1 import CFG


@pytest.fixture
def cfg_exp1(update: dict | None) -> dict:
    cfg = deepcopy(CFG)
    if update:
        cfg.update(update)

    return cfg


@pytest.fixture
def eval_setup(cfg_exp1: dict) -> EvalSetup:
    return EvalSetup.model_validate(cfg_exp1)


@pytest.mark.parametrize(
    "cfg,update",
    [
        ("cfgexp1", dict()),
        ("cfgexp1", dict(obs_cfg=dict(OBS=CFG["obs_cfg"]["AERONET-Sun"]))),
    ],
)
def test_EvalSetup___init__(eval_config: dict, update: dict):
    eval_config.update(update)
    EvalSetup(**eval_config)


@pytest.mark.parametrize(
    "cfg,update,error",
    [
        (
            "cfgexp1",
            dict(model_cfg=dict(WRONG_MODEL=CFG["model_cfg"]["TM5-AP3-CTRL"])),
            "Invalid name: WRONG_MODEL",
        ),
        (
            "cfgexp1",
            dict(obs_cfg=dict(WRONG_OBS=CFG["obs_cfg"]["AERONET-Sun"])),
            "Invalid name: WRONG_OBS",
        ),
        (
            "cfgexp1",
            dict(obs_cfg=dict(OBS=dict(web_interface_name="WRONG_OBS"))),
            "Invalid name: WRONG_OBS",
        ),
    ],
)
def test_EvalSetup___init__INVALID_ENTRY_NAMES(eval_config: dict, update: dict, error: str):
    eval_config.update(update)
    with pytest.raises(EvalEntryNameError) as e:
        EvalSetup(**eval_config)
    assert error in str(e.value)


@pytest.mark.parametrize("update", ((None),))
def test_EvalSetup_ProjectInfo(eval_setup: EvalSetup, cfg_exp1: dict):
    assert eval_setup.proj_info.proj_id == cfg_exp1["proj_id"]


@pytest.mark.parametrize("update", ((None),))
def test_EvalSetup_ExperimentInfo(eval_setup: EvalSetup, cfg_exp1: dict):
    exp_info = eval_setup.exp_info
    assert exp_info.exp_id == cfg_exp1["exp_id"]
    assert exp_info.exp_descr == cfg_exp1["exp_descr"]
    assert exp_info.exp_name == cfg_exp1["exp_name"]
    assert exp_info.public == cfg_exp1["public"]


@pytest.mark.parametrize("update", ((None),))
def test_EvalSetup_TimeSetup(eval_setup: EvalSetup, cfg_exp1: dict):
    time_cfg = eval_setup.time_cfg
    assert time_cfg.freqs == cfg_exp1["freqs"]
    assert time_cfg.main_freq == cfg_exp1["main_freq"]
    assert time_cfg.periods == cfg_exp1["periods"]


@pytest.mark.parametrize(
    "update",
    (
        pytest.param(None, id="defaults"),
        pytest.param(dict(maps_freq="yearly", maps_res_deg=10), id="custom"),
    ),
)
def test_EvalSetup_ModelMapsSetup(eval_setup: EvalSetup, cfg_exp1: dict, update: dict):
    modelmaps_opts = eval_setup.modelmaps_opts
    if update:
        assert modelmaps_opts.maps_freq == cfg_exp1["maps_freq"] == update["maps_freq"]
        assert modelmaps_opts.maps_res_deg == cfg_exp1["maps_res_deg"] == update["maps_res_deg"]
    else:  # defaults
        assert "maps_freq" not in cfg_exp1
        assert modelmaps_opts.maps_freq == "monthly"
        assert "maps_res_deg" not in cfg_exp1
        assert modelmaps_opts.maps_res_deg == 5


@pytest.mark.parametrize(
    "update",
    (
        pytest.param(None, id="defaults"),
        pytest.param(dict(obs_only=True, only_colocation=True), id="custom"),
    ),
)
def test_EvalSetup_EvalRunOptions(eval_setup: EvalSetup, cfg_exp1: dict, update: dict):
    processing_opts = eval_setup.processing_opts
    assert processing_opts.clear_existing_json == cfg_exp1["clear_existing_json"]
    assert processing_opts.only_json == cfg_exp1["only_json"]
    assert processing_opts.only_model_maps == cfg_exp1["only_model_maps"]
    if update:
        assert processing_opts.obs_only == cfg_exp1["obs_only"] == update["obs_only"]
        assert (
            processing_opts.only_colocation
            == cfg_exp1["only_colocation"]
            == update["only_colocation"]
        )
    else:  # defaults
        assert "obs_only" not in cfg_exp1
        assert processing_opts.obs_only is False
        assert "only_colocation" not in cfg_exp1
        assert processing_opts.only_colocation is False


@pytest.mark.parametrize(
    "update",
    (
        pytest.param(None, id="default"),
        pytest.param(
            dict(
                trends_min_yrs=10,
                use_diurnal=True,
                use_fairmode=True,
                weighted_stats=False,
                model_only_stats=True,
                obs_only_stats=True,
                add_trends=True,
                annual_stats_constrained=True,
            ),
            id="custom",
        ),
    ),
)
def test_EvalSetup_StatisticsSetup(eval_setup: EvalSetup, cfg_exp1: dict, update: dict):
    statistics_opts = eval_setup.statistics_opts
    if update:
        assert (
            statistics_opts.trends_min_yrs
            == cfg_exp1["trends_min_yrs"]
            == update["trends_min_yrs"]
        )
        assert statistics_opts.use_diurnal == cfg_exp1["use_diurnal"] == update["use_diurnal"]
        assert statistics_opts.use_fairmode == cfg_exp1["use_fairmode"] == update["use_fairmode"]
        assert (
            statistics_opts.weighted_stats
            == cfg_exp1["weighted_stats"]
            == update["weighted_stats"]
        )
        assert (
            statistics_opts.model_only_stats
            == cfg_exp1["model_only_stats"]
            == update["model_only_stats"]
        )
        assert (
            statistics_opts.obs_only_stats
            == cfg_exp1["obs_only_stats"]
            == update["obs_only_stats"]
        )
        assert statistics_opts.add_trends == cfg_exp1["add_trends"] == update["add_trends"]
        assert (
            statistics_opts.annual_stats_constrained
            == cfg_exp1["annual_stats_constrained"]
            == update["annual_stats_constrained"]
        )
    else:  # defaults
        assert "trends_min_yrs" not in cfg_exp1
        assert statistics_opts.trends_min_yrs == 7
        assert "use_diurnal" not in cfg_exp1
        assert statistics_opts.use_diurnal is False
        assert "use_fairmode" not in cfg_exp1
        assert statistics_opts.use_fairmode is False
        assert statistics_opts.weighted_stats == cfg_exp1["weighted_stats"] == True  # noqa: E712
        assert "model_only_stats" not in cfg_exp1
        assert statistics_opts.model_only_stats is False
        assert "obs_only_stats" not in cfg_exp1
        assert statistics_opts.obs_only_stats is False
        assert "add_trends" not in cfg_exp1
        assert statistics_opts.add_trends is False
        assert (
            statistics_opts.annual_stats_constrained  # noqa: E712
            == cfg_exp1["annual_stats_constrained"]
            == True
        )


@pytest.mark.parametrize("update", ((None),))
def test_EvalSetup_WebDisplaySetup(eval_setup: EvalSetup, cfg_exp1: dict):
    webdisp_opts = eval_setup.webdisp_opts
    # from config
    assert webdisp_opts.add_model_maps == cfg_exp1["add_model_maps"]
    assert webdisp_opts.map_zoom == cfg_exp1["map_zoom"]
    assert webdisp_opts.add_model_maps == cfg_exp1["add_model_maps"]
    # defaults
    assert "modelorder_from_config" not in cfg_exp1
    assert webdisp_opts.modelorder_from_config is True
    assert "obsorder_from_config" not in cfg_exp1
    assert webdisp_opts.obsorder_from_config is True

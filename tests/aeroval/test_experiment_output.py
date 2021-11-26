from __future__ import annotations

import os
from pathlib import Path
from typing import Type

import pytest

from pyaerocom import const
from pyaerocom._lowlevel_helpers import read_json, write_json
from pyaerocom.aeroval import ExperimentProcessor
from pyaerocom.aeroval import experiment_output as mod
from pyaerocom.aeroval.setupclasses import EvalSetup

from ..conftest import geojson_unavail
from .cfg_test_exp1 import CFG as cfgexp1

BASEDIR_DEFAULT = os.path.join(const.OUTPUTDIR, "aeroval/data")
from ._outbase import AEROVAL_OUT as BASEOUT

DUMMY_OUT = os.path.join(BASEOUT, "dummy")


@pytest.fixture(scope="module")
def dummy_setup():
    return EvalSetup(proj_id="proj", exp_id="exp", json_basedir=DUMMY_OUT)


@pytest.fixture(scope="module")
def dummy_expout(dummy_setup):
    return mod.ExperimentOutput(dummy_setup)


@pytest.mark.parametrize(
    "proj_id,json_basedir",
    [
        ("bla", None),
        ("bla", "/"),
    ],
)
def test_ProjectOutput(proj_id: str, json_basedir: str | None):
    val = mod.ProjectOutput(proj_id, json_basedir)
    assert val.proj_id == proj_id
    if json_basedir is not None:
        assert Path(val.json_basedir).exists()


@pytest.mark.parametrize(
    "proj_id,json_basedir,exception,error",
    [
        pytest.param(42, None, ValueError, "need str, got 42", id="ValueError"),
        pytest.param(
            "bla", "/blablub/blaaaa", FileNotFoundError, "/blablub/blaaaa", id="FileNotFoundError"
        ),
    ],
)
def test_ProjectOutput_error(proj_id, json_basedir, exception: Type[Exception], error: str):
    with pytest.raises(exception) as e:
        mod.ProjectOutput(proj_id, json_basedir)
    assert str(e.value) == error


def test_ProjectOutput_proj_dir(tmpdir):
    loc = str(tmpdir)
    val = mod.ProjectOutput("test", loc)
    path = os.path.join(loc, "test")
    assert val.proj_dir == path
    assert os.path.exists(path)


def test_ProjectOutput_experiments_file(tmpdir):
    loc = str(tmpdir)
    val = mod.ProjectOutput("test", loc)
    fp = os.path.join(loc, "test", "experiments.json")
    assert val.experiments_file == fp
    assert os.path.exists(fp)


@pytest.mark.parametrize("add", [None, "exp"])
def test_ProjectOutput_available_experiments(tmpdir, add):
    loc = str(tmpdir)
    val = mod.ProjectOutput("test", loc)
    fp = val.experiments_file
    if add is not None:
        write_json({add: 42}, fp)
        assert add in val.available_experiments
    else:
        val.available_experiments == []


def test_ProjectOutput__add_entry_experiments_json(tmpdir):
    loc = str(tmpdir)
    val = mod.ProjectOutput("test", loc)
    val._add_entry_experiments_json("test", 42)
    assert "test" in val.available_experiments


def test_ProjectOutput__del_entry_experiments_json(tmpdir):
    loc = str(tmpdir)
    exp_id = "test"
    val = mod.ProjectOutput("test", loc)
    val._add_entry_experiments_json(exp_id, {})
    assert exp_id in val.available_experiments
    val._del_entry_experiments_json(exp_id)
    assert exp_id not in val.available_experiments
    # to catch KeyError and make sure it passes
    val._del_entry_experiments_json(exp_id)


def test_ExperimentOutput():
    cfg = EvalSetup(proj_id="proj", exp_id="exp")
    val = mod.ExperimentOutput(cfg)
    assert isinstance(val.cfg, EvalSetup)
    assert val.proj_id == cfg["proj_info"]["proj_id"]
    assert os.path.exists(BASEDIR_DEFAULT)
    assert os.path.samefile(val.json_basedir, BASEDIR_DEFAULT)


def test_ExperimentOutput_error():
    with pytest.raises(ValueError) as e:
        mod.ExperimentOutput(None)
    assert str(e.value) == "need instance of <class 'pyaerocom.aeroval.setupclasses.EvalSetup'>"


def test_ExperimentOutput_exp_id(dummy_expout):
    assert dummy_expout.exp_id == "exp"


def test_ExperimentOutput_exp_dir(dummy_expout):

    exp_dir = os.path.join(DUMMY_OUT, "proj", "exp")
    assert dummy_expout.exp_dir == exp_dir


def test_ExperimentOutput_regions_file(dummy_expout):
    assert dummy_expout.regions_file == os.path.join(dummy_expout.exp_dir, "regions.json")


def test_ExperimentOutput_statistics_file(dummy_expout):
    assert dummy_expout.statistics_file == os.path.join(dummy_expout.exp_dir, "statistics.json")


def test_ExperimentOutput_var_ranges_file(dummy_expout):
    assert dummy_expout.var_ranges_file == os.path.join(dummy_expout.exp_dir, "ranges.json")


def test_ExperimentOutput_menu_file(dummy_expout):
    assert dummy_expout.menu_file == os.path.join(dummy_expout.exp_dir, "menu.json")


def test_ExperimentOutput_results_available_False(dummy_setup):
    eo = mod.ExperimentOutput(dummy_setup)
    assert not eo.results_available
    fp = eo.exp_dir
    assert not eo.results_available


def test_ExperimentOutput_update_menu_EMPTY(dummy_expout):
    dummy_expout.update_menu()
    assert os.path.exists(dummy_expout.menu_file)
    assert read_json(dummy_expout.menu_file) == {}


def test_ExperimentOutput_update_interface_EMPTY(dummy_expout):
    dummy_expout.update_interface()


def test_ExperimentOutput_update_heatmap_json_EMPTY(dummy_expout):
    dummy_expout._sync_heatmaps_with_menu_and_regions()


def test_ExperimentOutput__info_from_map_file():
    output = mod.ExperimentOutput._info_from_map_file(
        "EBAS-2010-ac550aer_Surface_ECHAM-HAM-ac550dryaer.json"
    )
    assert output == ("EBAS-2010", "ac550aer", "Surface", "ECHAM-HAM", "ac550dryaer")


@pytest.mark.parametrize(
    "filename",
    [
        "blaaaa",
        "EBAS-2010-ac550aer_Surface_ECHAM-HAM_ac550dryaer.json",
    ],
)
def test_ExperimentOutput__info_from_map_file_error(filename: str):
    with pytest.raises(ValueError) as e:
        mod.ExperimentOutput._info_from_map_file(filename)
    assert str(e.value) == (
        f"invalid map filename: {filename}. "
        "Must contain exactly 2 underscores _ to separate obsinfo, vertical and model info"
    )


def test_ExperimentOutput__results_summary_EMPTY(dummy_expout):
    assert dummy_expout._results_summary() == {
        "obs": [],
        "ovar": [],
        "vc": [],
        "mod": [],
        "mvar": [],
    }


def test_ExperimentOutput_clean_json_files_EMPTY(dummy_expout):
    modified = dummy_expout.clean_json_files()
    assert len(modified) == 0


@pytest.mark.skip(reason="needs revision")
def test_ExperimentOutput__clean_modelmap_files(dummy_expout):
    dummy_expout._clean_modelmap_files()


@pytest.mark.parametrize("also_coldata", [True, False])
def test_ExperimentOutput_delete_experiment_data(tmpdir, also_coldata):
    json_dir = os.path.join(tmpdir, "json")
    coldata_dir = os.path.join(tmpdir, "coldata")
    stp = EvalSetup(
        proj_id="proj", exp_id="exp", coldata_basedir=coldata_dir, json_basedir=json_dir
    )

    eo = mod.ExperimentOutput(stp)
    expdir = os.path.join(json_dir, "proj", "exp")
    coldir = os.path.join(coldata_dir, "proj", "exp")
    col_out = eo.cfg.path_manager.get_coldata_dir()
    assert os.path.samefile(coldir, col_out)
    assert os.path.samefile(expdir, eo.exp_dir)
    assert os.path.exists(coldata_dir)
    assert os.path.exists(coldir)
    eo.delete_experiment_data(also_coldata=also_coldata)
    assert not os.path.exists(expdir)
    if also_coldata:
        assert not os.path.exists(coldir)
    else:
        assert os.path.exists(coldata_dir)


@pytest.mark.parametrize(
    "var,val",
    [
        (
            "ang4487aer",
            {"scale": [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2], "colmap": "coolwarm"},
        ),
        (
            "concprcpso4",
            {"colmap": "coolwarm", "scale": [0, 1.25, 2.5, 3.75, 5, 6.25, 7.5, 8.75, 10]},
        ),
    ],
)
def test_ExperimentOutput__get_cmap_info(dummy_expout, var, val):
    assert dummy_expout._get_cmap_info(var) == val


### BELOW ARE TESTS ON ACTUAL OUTPUT THAT DEPEND ON EVALUATION RUNS


def test_ExperimentOutput_delete_experiment_data_CFG1():
    cfg = EvalSetup(**cfgexp1)
    cfg.webdisp_opts.regions_how = "htap"
    cfg.webdisp_opts.add_model_maps = False
    cfg.statistics_opts.add_trends = False
    cfg.time_cfg.add_seasons = False
    proc = ExperimentProcessor(cfg)
    proc.run()
    chk = proc.exp_output.exp_dir
    assert os.path.exists(chk)
    proc.exp_output.delete_experiment_data()
    assert not os.path.exists(chk)


@geojson_unavail
def test_Experiment_Output_clean_json_files_CFG1():
    cfg = EvalSetup(**cfgexp1)
    proc = ExperimentProcessor(cfg)
    proc.run()
    modified = proc.exp_output.clean_json_files()
    assert len(modified) == 0


@geojson_unavail
def test_Experiment_Output_clean_json_files_CFG1_INVALIDMOD():
    cfg = EvalSetup(**cfgexp1)
    cfg.model_cfg["mod1"] = cfg.model_cfg["TM5-AP3-CTRL"]
    proc = ExperimentProcessor(cfg)
    proc.run()
    del cfg.model_cfg["mod1"]
    modified = proc.exp_output.clean_json_files()
    assert len(modified) == 15


@geojson_unavail
def test_Experiment_Output_clean_json_files_CFG1_INVALIDOBS():
    cfg = EvalSetup(**cfgexp1)
    cfg.obs_cfg["obs1"] = cfg.obs_cfg["AERONET-Sun"]
    proc = ExperimentProcessor(cfg)
    proc.run()
    del cfg.obs_cfg["obs1"]
    modified = proc.exp_output.clean_json_files()
    assert len(modified) == 13


@pytest.mark.parametrize(
    "add_names,order,result",
    [
        (["c", "b", "a"], None, ["a", "b", "c"]),
        (["c", "b", "a"], ["c", "b", "a"], ["c", "b", "a"]),
        (["c", "b", "a"], [42], ["a", "b", "c"]),
        (["c", "b", "a"], ["b"], ["b", "a", "c"]),
        (["c", "b", "a"], ["b", "c"], ["b", "c", "a"]),
    ],
)
def test_ExperimentOutput_reorder_experiments(dummy_expout, add_names, order, result):

    out = dummy_expout
    path = Path(out.experiments_file)

    data = dict().fromkeys(add_names, dict(public=True))
    assert list(data) == add_names

    write_json(data, path, indent=4)
    out.reorder_experiments(order)
    new = read_json(path)
    assert list(new) == result
    path.unlink()


def test_ExperimentOutput_reorder_experiments_error(dummy_expout):
    with pytest.raises(ValueError) as e:
        dummy_expout.reorder_experiments("b")
    assert str(e.value) == "need list as input"

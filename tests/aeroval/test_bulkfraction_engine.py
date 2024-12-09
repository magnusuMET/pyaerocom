import pytest

from pyaerocom.aeroval.bulkfraction_engine import BulkFractionEngine
from pyaerocom.aeroval import EvalSetup
from tests.fixtures.aeroval import cfg_test_bulk


@pytest.fixture
def bulkengine_instance() -> BulkFractionEngine:
    cfg = EvalSetup(**cfg_test_bulk.CFG)
    bfe = BulkFractionEngine(cfg)
    return bfe


def test__get_bulk_vars(bulkengine_instance: BulkFractionEngine):
    obsentry = bulkengine_instance.cfg.obs_cfg.get_entry("EBAS-m")
    assert (
        bulkengine_instance._get_bulk_vars("concwetrdn", obsentry)
        == obsentry.bulk_options["concwetrdn"]["vars"]
    )

    with pytest.raises(KeyError, match="Could not find bulk vars entry"):
        bulkengine_instance._get_bulk_vars("concwetrdn2", obsentry)


def test_get_colocators_modelexists(bulkengine_instance: BulkFractionEngine):
    obsentry = bulkengine_instance.cfg.obs_cfg.get_entry("EBAS-m")
    freq = obsentry.ts_type
    bulk_vars = bulkengine_instance._get_bulk_vars("concwetrdn", obsentry)
    cols_exist = bulkengine_instance.get_colocators(
        bulk_vars, "concwetrdn", freq, "EMEP", "EBAS-m", True
    )

    assert len(cols_exist.keys()) == 2

    assert (
        cols_exist[bulk_vars[0]].colocation_setup.model_use_vars[bulk_vars[0]]
        == cols_exist[bulk_vars[1]].colocation_setup.model_use_vars[bulk_vars[1]]
    )


def test_get_colocators(bulkengine_instance: BulkFractionEngine):
    obsentry = bulkengine_instance.cfg.obs_cfg.get_entry("EBAS-m")
    freq = obsentry.ts_type
    bulk_vars = bulkengine_instance._get_bulk_vars("concwetrdn", obsentry)
    cols_exist = bulkengine_instance.get_colocators(
        bulk_vars, "concwetrdn", freq, "EMEP", "EBAS-m", False
    )

    assert len(cols_exist.keys()) == 2

    assert cols_exist[bulk_vars[0]].colocation_setup.obs_vars[0] == bulk_vars[0]
    assert cols_exist[bulk_vars[1]].colocation_setup.obs_vars[0] == bulk_vars[1]

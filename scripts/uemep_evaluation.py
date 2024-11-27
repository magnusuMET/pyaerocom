from pyaerocom.aeroval.config.uemep.uemep_base import get_CFG


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import pyaerocom as pya
    from pyaerocom import const
    from pyaerocom.aeroval import EvalSetup, ExperimentProcessor

    plt.close("all")
    cfg = get_CFG(2024, 2022, "/lustre/storeB/project/fou/kl/emep/ModelRuns/2024_uEMEP_rerun_2022_aeroval")

    cfg.update(
        {
            "add_model_maps": False,
            "proj_id": "uemep_test",
            "exp_id": "20241125",
            "exp_pi": "thlun8736@met.no",
            "json_basedir": "/lustre/storeB/users/thlun8736/python/aeroval/data",
            "coldata_basedir": "/lustre/storeB/users/thlun8736/python/aeroval/coldata",
            "raise_exceptions": False
        }
    )
    # O3 info is only in monthly / daily while all other variables are only
    # in hourly. The following seems to make it run, but there may be a better way.
    # ¯\_(ツ)_/¯
    #cfg["model_cfg"]["EMEP"]["model_ts_type_read"] = {
    #    "vmro3max": "daily",
    #    "concpm10": "hourly",
    #    "concpm25": "hourly",
    #    "prmm": "hourly"
    #}
    stp = EvalSetup(**cfg)

    ana = ExperimentProcessor(stp)

    res = ana.run()
from pyaerocom.aeroval.collections import ObsCollection, ModelCollection


def test_obscollection():
    oc = ObsCollection()
    oc.add_entry("model1", dict(obs_id="bla", obs_vars="od550aer", obs_vert_type="Column"))
    assert oc

    oc.add_entry(
        "AN-EEA-MP",
        dict(
            is_superobs=True,
            obs_id=("AirNow", "EEA-NRT-rural", "MarcoPolo"),
            obs_vars=["concpm10", "concpm25", "vmro3", "vmrno2"],
            obs_vert_type="Surface",
        ),
    )

    assert "AN-EEA-MP" in oc.keylist()


def test_modelcollection():
    mc = ModelCollection()
    mc.add_entry("model1", dict(model_id="bla", obs_vars="od550aer", obs_vert_type="Column"))
    assert mc

    mc.add_entry(
        "ECMWF_OSUITE",
        dict(
            model_id="ECMWF_OSUITE",
            obs_vars=["concpm10"],
            obs_vert_type="Surface",
        ),
    )

    assert "ECMWF_OSUITE" in mc.keylist()

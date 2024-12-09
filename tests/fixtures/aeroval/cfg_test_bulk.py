import os

OBS_GROUNDBASED = {
    "EBAS-m": dict(
        obs_id="EBASMC",
        web_interface_name="EBAS-m",
        obs_vars=[
            "concwetrdn",
        ],
        obs_vert_type="Surface",
        colocate_time=True,
        ts_type="monthly",
        is_bulk=True,
        bulk_options={
            "concwetrdn": dict(
                vars=["wetrdn", "wetrdnpr"],
                model_exists=False,
                mode="fraction",
                units="mg N m-3",
            )
        },
    )
}

folder_EMEP = f"/lustre/storeB/project/fou/kl/emep/ModelRuns/2022_REPORTING/TRENDS/2013/"


# Setup for models used in analysis
MODELS = {
    "EMEP": dict(
        model_id="EMEP",
        model_data_dir=folder_EMEP,
        gridded_reader_id={"model": "ReadMscwCtm"},
        model_ts_type_read="monthly",
    ),
}

CFG = dict(
    model_cfg=MODELS,
    obs_cfg=OBS_GROUNDBASED,
    json_basedir=os.path.abspath("./data"),
    # coldata_basedir = os.path.abspath('../../coldata'),
    coldata_basedir=os.path.abspath("./coldata"),
    # io_aux_file=os.path.abspath("../../eval_py/gridded_io_aux.py"),
    # if True, existing colocated data files will be deleted
    reanalyse_existing=True,
    only_json=False,
    add_model_maps=False,
    only_model_maps=False,
    clear_existing_json=False,
    # if True, the analysis will stop whenever an error occurs (else, errors that
    # occurred will be written into the logfiles)
    raise_exceptions=True,
    # Regional filter for analysis
    filter_name="ALL-wMOUNTAINS",
    # colocation frequency (no statistics in higher resolution can be computed)
    ts_type="monthly",
    map_zoom="Europe",
    freqs=["daily", "monthly", "yearly"],
    periods=["2013"],
    main_freq="monthly",
    maps_freq="yearly",
    zeros_to_nan=False,
    colocate_time=True,
    resample_how={"vmro3max": {"daily": {"hourly": "max"}}},
    obs_remove_outliers=False,
    model_remove_outliers=False,
    harmonise_units=True,
    regions_how="country",  #'default',#'country',
    annual_stats_constrained=True,
    proj_id="bulk",
    exp_id="bulktest_wetrdnpr",
    exp_name="Evaluation of EMEP Bulk",
    exp_descr=("Evaluation of EMEP Bulk"),
    exp_pi="Daniel Heinesen",
    public=True,
    # directory where colocated data files are supposed to be stored
    weighted_stats=True,
    var_order_menu=[
        "concwetrdn",
    ],
)

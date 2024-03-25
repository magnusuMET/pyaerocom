CFG = {
   "proj_info": {
      "proj_id": "cams2-83"
   },
   "exp_info": {
      "exp_id": "forecast-last-week",
      "exp_name": "CAMS regional evaluation (forecast)",
      "exp_descr": "Evaluation of the forecast for the latest week for which both model data and observations are available, using EEA NRT observations received via Meteo France.",
      "public": True,
      "exp_pi": "<a href='https://atmosphere.copernicus.eu/help-and-support'>CAMS user support</a>",
   },
   "time_cfg": {
      "main_freq": "hourly",
      "freqs": [
         "hourly",
         "daily"
      ],
      "add_seasons": True,
      "periods": [
         "2024/03/16-2024/03/23"
      ]
   },
   "modelmaps_opts": {
      "maps_res_deg": 5
   },
   "colocation_opts": {
      "obs_vars": [],
      "ts_type": "hourly",
      "start": "2024/03/16 00:00:00",
      "stop": "2024/03/23 23:00:00",
      "filter_name": "ALL-wMOUNTAINS",
      "basedir_coldata": "/home/uemep/MyPyaerocom/colocated_data",
      "save_coldata": True,
      "obs_use_climatology": False,
      "_obs_cache_only": False,
      "obs_filters": {},
      "read_opts_ungridded": {},
      "model_read_opts": {},
      "model_use_vars": {},
      "model_rename_vars": {},
      "model_add_vars": {},
      "model_to_stp": False,
      "model_read_aux": {},
      "model_use_climatology": False,
      "model_kwargs": {},
      "gridded_reader_id": {
         "model": "ReadGridded",
         "obs": "ReadGridded"
      },
      "flex_ts_type": True,
      "min_num_obs": {
         "daily": {
            "hourly": 18
         }
      },
      "resample_how": {
         "vmro3": {
            "daily": {
               "hourly": "max"
            }
         }
      },
      "obs_remove_outliers": False,
      "model_remove_outliers": False,
      "obs_outlier_ranges": {},
      "model_outlier_ranges": {},
      "zeros_to_nan": True,
      "harmonise_units": True,
      "colocate_time": False,
      "reanalyse_existing": True,
      "raise_exceptions": False,
      "keep_data": False,
      "add_meta": {}
   },
   "statistics_opts": {
      "weighted_stats": False,
      "annual_stats_constrained": False,
      "add_trends": False,
      "trends_min_yrs": 7,
      "use_diurnal": False,
      "forecast_evaluation": False,
      "forecast_days": 4,
      "use_fairmode": True
   },
   "webdisp_opts": {
      "regions_how": "country",
      "map_zoom": "Europe",
      "add_model_maps": True,
      "modelorder_from_config": True,
      "obsorder_from_config": True,
      "var_order_menu": [
         "vmrno2",
         "vmro3max",
         "vmro3",
         "conco3",
         "vmrox",
         "concso2",
         "vmrco",
         "concpm25",
         "concpm10",
         "concso4",
         "concNtno3",
         "concNtnh",
         "concNnh3",
         "concNnh4",
         "concNhno3",
         "concNno3pm25",
         "concNno3pm10",
         "concsspm25",
         "concsspm10",
         "concCecpm25",
         "concCocpm25",
         "wetoxs",
         "wetrdn",
         "wetoxn",
         "pr",
         "drysox",
         "dryrdn",
         "dryoxn",
         "dryo3",
         "dryvelo3"
      ],
      "obs_order_menu": [],
      "model_order_menu": [],
      "hide_charts": [],
      "hide_pages": []
   },
   "processing_opts": {
      "clear_existing_json": False,
      "only_json": False,
      "only_colocation": False,
      "only_model_maps": True,
      "obs_only": False
   },
   "cams2_83_cfg": {
      "use_cams2_83": True,
      "cams2_83_model": "emep",
      "cams2_83_dateshift": 0
   },
   "obs_cfg": {
      "EEA": {
         "obs_id": "CAMS2_83.NRT",
         "obs_vars": [
            "concno2",
            "concco",
            "conco3",
            "concso2",
            "concpm10",
            "concpm25"
         ],
         "obs_vert_type": "Surface",
         "obs_aux_requires": {},
         "is_superobs": False,
         "only_superobs": False,
         "read_opts_ungridded": {
            "files": [
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240316.csv",
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240317.csv",
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240318.csv",
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240319.csv",
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240320.csv",
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240321.csv",
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240322.csv",
               "/lustre/storeB/project/fou/kl/CAMS2_83/obs/202403/obsmacc4verif_20240323.csv"
            ],
            "force_caching": True
         },
         "web_interface_name": "Obs",
         
      }
   },
   "model_cfg": {
      "EMEP": {
         "model_id": "CAMS2-83.EMEP.day0.FC",
         "model_ts_type_read": "",
         "model_use_vars": {},
         "model_add_vars": {},
         "model_rename_vars": {},
         "model_read_aux": {},
         "model_data_dir": "/lustre/storeB/project/fou/kl/CAMS2_83/model",
         "gridded_reader_id": {
            "model": "ReadCAMS2_83"
         },
         "model_kwargs": {
            "daterange": [
               "2024-03-16",
               "2024-03-23"
            ]
         },
         "model_name": "EMEP"
      },
   },
   "var_web_info": {},
   "path_manager": {
      "proj_id": "cams2-83",
      "exp_id": "forecast-last-week",
      "json_basedir": "/lustre/storeB/project/fou/kl/CAMS2_83/evaluation/data",
      "coldata_basedir": "/lustre/storeB/project/fou/kl/CAMS2_83/evaluation/coldata"
   },
   "io_aux_file": ""
}

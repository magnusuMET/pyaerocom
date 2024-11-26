import logging
from traceback import format_exc

import numpy as np
import xarray as xr

from pyaerocom import ColocatedData
from pyaerocom.aeroval._processing_base import HasColocator, ProcessingEngine
from pyaerocom.aeroval.obsentry import ObsEntry
from pyaerocom.aeroval.coldatatojson_engine import ColdataToJsonEngine
from pyaerocom.aeroval.setup_classes import EvalSetup
from pyaerocom.helpers import get_lowest_resolution
from pyaerocom.colocation.colocator import Colocator
from pyaerocom.colocation.colocation_setup import ColocationSetup

logger = logging.getLogger(__name__)


class BulkFractionEngine(ProcessingEngine, HasColocator):
    def __init__(self, cfg: EvalSetup):
        super().__init__(cfg)

    def run(self, var_list: list | str | None, model_name: str, obs_name: str):
        sobs_cfg = self.cfg.obs_cfg.get_entry(obs_name)

        if var_list is None:
            var_list = sobs_cfg.obs_vars
        elif isinstance(var_list, str):
            var_list = [var_list]
        elif not isinstance(var_list, list):
            raise ValueError(f"invalid input for var_list: {var_list}.")

        for var_name in var_list:
            bulk_vars = self._get_bulk_vars(var_name, sobs_cfg)
            self._run_var(model_name, obs_name, var_name, bulk_vars)

    def _get_bulk_vars(self, var_name: str, cfg: ObsEntry) -> list:
        bulk_vars = cfg.bulk_vars
        if var_name not in bulk_vars:
            raise KeyError(f"Could not find bulk vars entry for {var_name}")

        if len(bulk_vars[var_name]) != 2:
            raise ValueError(
                f"(Only) 2 entries must be present for bulk vars to calculate fraction for {var_name}. Found {bulk_vars[var_name]}"
            )

        return bulk_vars[var_name]

    def _run_var(self, model_name: str, obs_name: str, var_name: str, bulk_vars: list):

        col = self.get_colocator(bulk_vars, model_name, obs_name)
        # if self.cfg.processing_opts.only_json:
        #     files_to_convert = col.get_available_coldata_files(bulk_vars)
        # else:
        coldatas = col.run(bulk_vars)
        files_to_convert = col.files_written
        num_key, denum_key = bulk_vars[0], bulk_vars[1]
        self._divide_coldatas(
            coldatas[num_key][num_key], coldatas[denum_key][denum_key], var_name
        )

    def _divide_coldatas(
        self, num_coldata: ColocatedData, denum_coldata: ColocatedData, var_name: str
    ) -> ColocatedData:
        new_data = num_coldata.data / denum_coldata.data
        cd = ColocatedData(new_data)
        cd.data.attrs["var_name"] = [var_name, var_name]
        cd.metadata["var_name_input"] = [var_name, var_name]
        return cd

    def get_colocator(
        self, bulk_vars: list, model_name: str = None, obs_name: str = None
    ) -> Colocator:
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

        if model_name:
            mod_cfg = self.cfg.get_model_entry(model_name)
            col_cfg["model_cfg"] = mod_cfg

            # Hack and at what lowlevel_helpers's import_from was doing
            for key, val in mod_cfg.items():
                if key in ColocationSetup.model_fields:
                    col_cfg[key] = val
        if obs_name:
            obs_cfg = self.cfg.get_obs_entry(obs_name)
            pyaro_config = obs_cfg["obs_config"] if "obs_config" in obs_cfg else None
            col_cfg["obs_config"] = pyaro_config

            # Hack and at what lowlevel_helpers's import_from was doing
            for key, val in obs_cfg.model_dump().items():
                if key in ColocationSetup.model_fields:
                    col_cfg[key] = val

            col_cfg["add_meta"].update(
                diurnal_only=self.cfg.get_obs_entry(obs_name).diurnal_only
            )
        col_cfg["obs_vars"] = set(bulk_vars)
        col_stp = ColocationSetup(**col_cfg)
        col = Colocator(col_stp)

        return col

import logging

from pyaerocom import ColocatedData
from pyaerocom.aeroval._processing_base import HasColocator, ProcessingEngine
from pyaerocom.aeroval.obsentry import ObsEntry
from pyaerocom.aeroval.coldatatojson_engine import ColdataToJsonEngine
from pyaerocom.aeroval.setup_classes import EvalSetup

from pyaerocom.colocation.colocator import Colocator
from pyaerocom.colocation.colocation_setup import ColocationSetup


logger = logging.getLogger(__name__)


class BulkFractionEngine(ProcessingEngine, HasColocator):
    def __init__(self, cfg: EvalSetup):
        super().__init__(cfg)

    def run(self, var_list: list | str | None, model_name: str, obs_name: str):
        self.sobs_cfg = self.cfg.obs_cfg.get_entry(obs_name)

        if var_list is None:
            var_list = self.sobs_cfg.obs_vars
        elif isinstance(var_list, str):
            var_list = [var_list]
        elif not isinstance(var_list, list):
            raise ValueError(f"invalid input for var_list: {var_list}.")

        files_to_convert = []
        for var_name in var_list:
            bulk_vars = self._get_bulk_vars(var_name, self.sobs_cfg)
            # for freq in self.cfg.time_cfg.freqs:
            #     if TsType(freq) > TsType(self.sobs_cfg.ts_type):
            #         continue
            #     print(f"Colocating {var_name}, {freq}")
            freq = self.sobs_cfg.ts_type
            cd, fp = self._run_var(model_name, obs_name, var_name, bulk_vars, freq, self.sobs_cfg)
            files_to_convert.append(fp)

        engine = ColdataToJsonEngine(self.cfg)
        engine.run(files_to_convert)

    def _get_bulk_vars(self, var_name: str, cfg: ObsEntry) -> list:
        bulk_vars = cfg.bulk_options
        if var_name not in bulk_vars:
            raise KeyError(f"Could not find bulk vars entry for {var_name}")

        if len(bulk_vars[var_name]["vars"]) != 2:
            raise ValueError(
                f"(Only) 2 entries must be present for bulk vars to calculate fraction for {var_name}. Found {bulk_vars[var_name]}"
            )

        return bulk_vars[var_name]["vars"]

    def _run_var(
        self,
        model_name: str,
        obs_name: str,
        var_name: str,
        bulk_vars: list,
        freq: str,
        obs_entry: ObsEntry,
    ) -> tuple[ColocatedData, str]:
        model_exists = obs_entry.bulk_options[var_name]["model_exists"]

        cols = self.get_colocators(bulk_vars, var_name, freq, model_name, obs_name, model_exists)
        # if self.cfg.processing_opts.only_json:
        #     files_to_convert = col.get_available_coldata_files(bulk_vars)
        # else:
        coldatas = {}
        for bv in cols:
            coldatas[bv] = cols[bv].run(bv)
        # files_to_convert = col.files_written
        num_key, denum_key = bulk_vars[0], bulk_vars[1]
        if model_exists:
            cd = self._combine_coldatas(
                coldatas[num_key][var_name][num_key],
                coldatas[denum_key][var_name][denum_key],
                var_name,
                obs_entry,
            )
        else:
            cd = self._combine_coldatas(
                coldatas[num_key][num_key][num_key],
                coldatas[denum_key][denum_key][denum_key],
                var_name,
                obs_entry,
            )
        fp = cd.to_netcdf(
            out_dir=cols[num_key].output_dir,
            savename=cd._aerocom_savename(
                var_name,
                obs_name,
                var_name,
                model_name,
                cols[num_key].get_start_str(),
                cols[num_key].get_stop_str(),
                freq,
                cols[num_key].colocation_setup.filter_name,
                None,  # cd.data.attrs["vert_code"],
            ),
        )
        return cd, fp

    def _combine_coldatas(
        self,
        num_coldata: ColocatedData,
        denum_coldata: ColocatedData,
        var_name: str,
        obs_entry: ObsEntry,
    ) -> ColocatedData:
        mode = obs_entry.bulk_options[var_name]["mode"]
        model_exists = obs_entry.bulk_options[var_name]["model_exists"]
        units = obs_entry.bulk_options[var_name]["units"]

        if mode == "fraction":
            new_data = num_coldata.data / denum_coldata.data

        elif mode == "product":
            new_data = num_coldata.data * denum_coldata.data
        else:
            raise ValueError("Mode must be either fraction of product.")
        if model_exists:
            # TODO: Unsure if this works!!!
            new_data[1] = num_coldata.data[1].where(new_data[1])

        cd = ColocatedData(new_data)

        cd.data.attrs = num_coldata.data.attrs
        cd.data.attrs["var_name"] = [var_name, var_name]
        cd.data.attrs["var_units"] = [units, units]
        cd.metadata["var_name_input"] = [var_name, var_name]
        return cd

    def get_colocators(
        self,
        bulk_vars: list,
        var_name: str,
        freq: str,
        model_name: str = None,
        obs_name: str = None,
        model_exists: bool = False,
    ) -> dict[str | Colocator]:
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

            col_cfg["add_meta"].update(diurnal_only=self.cfg.get_obs_entry(obs_name).diurnal_only)
        cols = {}
        col_cfg["ts_type"] = freq
        for bulk_var in bulk_vars:
            col_cfg["obs_vars"] = bulk_var
            if model_exists:
                col_cfg["model_use_vars"] = {
                    bulk_var: var_name,
                }
            col_stp = ColocationSetup(**col_cfg)
            col = Colocator(col_stp)

            cols[bulk_var] = col

        return cols

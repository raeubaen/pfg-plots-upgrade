import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from Plugin import Plugin
import ECAL

from TTStatus import TTStatus


def read_hist(one_run_root_object, labels, run_dict, supermodule, status_dict):
    status_df = pd.DataFrame(status_dict)

    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    yproj = one_run_root_object.ProjectionY("yproj", 1, 1)
    #loop on the TH2F histogram: iy -> status, ix -> trigger tower
    for iy in range(1, nbinsy+1):
        if labels[iy-1] == "ENABLED" or labels[iy-1] == "SUPPRESSED":
            continue
        for ix in range(1, nbinsx+1):
            if one_run_root_object.GetBinContent(ix, iy) != 0:
                status_df_match = (status_df["label"] == supermodule) & (status_df["tt_ccu"] == ix) & (status_df["status"] > 0)
                if status_df_match.any():
                  print("skipping: ", supermodule, ix, status_df[status_df_match].x_phi, status_df[status_df_match].y_eta)
                  continue

                run_dict["label"].append(f"{supermodule} TT{ix}")
                run_dict["status"].append(iy)
                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy)/yproj.GetEntries())

class FEStatusBits(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")

        
    def process_one_run(self, run_info):
        #labels of the trigger towers status bits
        labels = ECAL.FEstatus_labels        
        #dictionary with single run status info to fill with histogram data
        run_dict = {"label": [], "status": [], "value": []}

        status_dict = TTStatus(self.buildopener).get_status_dict(run_info)

        #EB
        EBsupermodules_list = ECAL.EBsupermodules_list
        for i, EBsupermodule in enumerate(EBsupermodules_list):
            self.folder = "EcalBarrel/EBStatusFlagsTask/FEStatus/"
            self.plot_name = f"EBSFT front-end status bits {EBsupermodule}"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, labels, run_dict, EBsupermodule, status_dict)
                        
        #EE
        EEsupermodules_list = ECAL.EEsupermodules_list
        for i, EEsupermodule in enumerate(EEsupermodules_list):
            self.folder = "EcalEndcap/EEStatusFlagsTask/FEStatus/"
            self.plot_name = f"EESFT front-end status bits {EEsupermodule}"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, labels, run_dict, EEsupermodule, status_dict)
            
        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)

        
    #history plot function
    def create_history_plots(self, save_path):
        self.color_scale_settings(255)
        available_runs = self.get_available_runs()
        run_dict = {"label": [], "status": [], "value": [], "run": []}
        for i, run in enumerate(available_runs):
            data_one_run = self.get_data_one_run(run)
            for key in data_one_run:
                run_dict[key] += data_one_run[key]
            run_dict["run"] += [run for j in range(len(data_one_run["label"]))]

        #ordering
        run_df = pd.DataFrame(run_dict)
        if run_df.empty:
            print("Dataframe is empty, no info to plot")
            return
        run_df[["detector", "tower_num", "tt_num"]] = run_df["label"].str.extract(r'(EB|EE)([+-]?\d+)\s+TT(\d+)')
        run_df["tower_num"] = run_df["tower_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df = run_df.sort_values(by=["detector_priority", "tower_num", "tt_num"]).drop(columns=["detector_priority", "tower_num", "tt_num", "detector"])

        #filling history plot
        statuses = ECAL.FEstatus_match
        for i, stat in enumerate(statuses):
            curr_df = run_df[run_df.status == statuses[stat]]
            run_list_stat = list(pd.unique(curr_df.run))
            if not run_list_stat:
                continue
            self.fill_history_subplots(curr_df, available_runs, f"FEStatusBits_{stat}", f"{save_path}")

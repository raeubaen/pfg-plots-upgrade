import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from Plugin import Plugin
import ECAL

from TTStatus import TTStatus

from ReadoutFlagsForced import read_hist

class ReadoutFlagsDropped(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    def process_one_run(self, run_info):
        #load the file with all the info about the ECAL channels
        channels_df = pd.read_csv(self.ecal_channels_csv_path)
        #info for matching the SM with fed number
        supermodules_FED = ECAL.supermodules_FED_match
        #dictionary with single run info to fill with histogram data
        run_dict = {"label": [], "value": []}
        status_dict = TTStatus(self.buildopener).get_status_dict(run_info)

        #EB
        self.folder = "EcalBarrel/EBSelectiveReadoutTask/"
        self.plot_name = "EBSRT FR Flagged Dropped Readout"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EB", channels_df, supermodules_FED, run_dict, status_dict)

        #EE-
        self.folder = "EcalEndcap/EESelectiveReadoutTask/"
        self.plot_name = "EESRT FR Flagged Dropped Readout EE -"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE-", channels_df, supermodules_FED, run_dict, status_dict)

        #EE+
        self.folder = "EcalEndcap/EESelectiveReadoutTask/"
        self.plot_name = "EESRT FR Flagged Dropped Readout EE +"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE+", channels_df, supermodules_FED, run_dict, status_dict)

        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)


    #history plot function
    def create_history_plots(self, save_path):
        self.color_scale_settings(255)
        available_runs = self.get_available_runs()
        run_dict = {"label": [], "value": [], "run": []}
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
        run_df[["detector", "sm_num", "tcc_num", "tt_ccu", "tt_num"]] = run_df["label"].str.extract(r'(EB|EE)([+-]?\d+)\s+TCC(\d+)\s+(TT|CCU)(\d+)')
        run_df["sm_num"] = run_df["sm_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df["tcc_num"] = run_df["tcc_num"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df["tt_ccu_priority"] = run_df["tt_ccu"].map({"TT": 0, "CCU": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_num", "tcc_num", "tt_ccu_priority", "tt_num"]).drop(columns=["detector_priority",
        "sm_num", "tcc_num", "tt_ccu_priority", "tt_num", "detector", "tt_ccu"])

        #filling history plot
        self.fill_history_subplots(run_df, available_runs, "ReadoutFlagsDropped", f"{save_path}")

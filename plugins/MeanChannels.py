import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from Plugin import Plugin
import ECAL

LOW_LIMIT = 100
UP_LIMIT = 300
MIN_VALUE = 5



def read_hist(one_run_root_object, run_dict, supermodule):
    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    for iy in range(1, nbinsy+1):
        for ix in range(1, nbinsx+1):
            if (one_run_root_object.GetBinContent(ix, iy) < LOW_LIMIT and one_run_root_object.GetBinContent(ix, iy) > MIN_VALUE) or one_run_root_object.GetBinContent(ix, iy) > UP_LIMIT:
                if "EB-" in supermodule: #y -> iphi, x -> ieta
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                    run_dict["label"].append(f"{supermodule} [+{y}, -{x}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif "EB+" in supermodule: #y -> iphi, x -> ieta
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(-one_run_root_object.GetYaxis().GetBinLowEdge(iy))
                    run_dict["label"].append(f"{supermodule} [+{y}, +{x}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif "EE" in supermodule: #y -> iy, x -> ix
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                    run_dict["label"].append(f"{supermodule} [+{x}, +{y}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


class MeanChannels(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    def process_one_run(self, run_info):
        #dictionary with single run status info to fill with histogram data
        run_dict = {"label": [], "value": []}

        #EB
        EBsupermodules_list = ECAL.EBsupermodules_list
        for i, EBsupermodule in enumerate(EBsupermodules_list):
            self.folder = "EcalBarrel/EBPedestalOnlineTask/Gain12/"
            self.plot_name = f"EBPOT pedestal {EBsupermodule} G12"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, run_dict, EBsupermodule)

        #EE
        EEsupermodules_list = ECAL.EEsupermodules_list
        for i, EEsupermodule in enumerate(EEsupermodules_list):
            self.folder = "EcalEndcap/EEPedestalOnlineTask/Gain12/"
            self.plot_name = f"EEPOT pedestal {EEsupermodule} G12"
            self.serverurl_online = "online"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, run_dict, EEsupermodule)
        
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
        run_df[["detector", "sm_ch", "iphi_ix", "ieta_iy"]] = run_df["label"].str.extract(r'(EB|EE)([+-]?\d+)\s+\[([+-]?\d+),\s*([+-]?\d+)\]')
        run_df["sm_ch"] = run_df["sm_ch"].astype(int)
        run_df["iphi_ix"] = run_df["iphi_ix"].astype(int)
        run_df["ieta_iy"] = run_df["ieta_iy"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_ch", "iphi_ix", "ieta_iy"]).drop(columns=["detector_priority",
        "detector", "sm_ch", "iphi_ix", "ieta_iy"])
        df_high = run_df.loc[run_df["value"] > 300]
        df_low = run_df.loc[run_df["value"] < 100]

        #filling mean > 300 history plot
        self.fill_history_subplots(df_high, available_runs, "mean_channels_greater_300", f"{save_path}", change_hist_limits=True)
        #filling mean < 100 history plot
        self.fill_history_subplots(df_low, available_runs, "mean_channels_less_100", f"{save_path}", change_hist_limits=True)
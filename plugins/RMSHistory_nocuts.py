import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from Plugin import Plugin
import ECAL
from ChannelStatus import ChannelStatus


LOW_LIMIT = 0.1
UP_LIMIT = 0.1
MIN_VALUE = 0



def read_hist(one_run_root_object, run_dict, supermodule, status_dict, ch_list):
    status_df = pd.DataFrame(status_dict)


    print("ch_list", ch_list)

    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    for iy in range(1, nbinsy+1):
        for ix in range(1, nbinsx+1):
            if (one_run_root_object.GetBinContent(ix, iy) < LOW_LIMIT and one_run_root_object.GetBinContent(ix, iy) > MIN_VALUE) or one_run_root_object.GetBinContent(ix, iy) > UP_LIMIT:
                if "EB-" in supermodule: #y -> iphi, x -> -ieta
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                    for c in ch_list:
                      if c["y_eta"] == -x and c["x_phi"] == y: break
                    else: continue
                    run_dict["label"].append(f"{supermodule} [+{y}, -{x}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif "EB+" in supermodule: #y -> iphi, x -> ieta
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(-one_run_root_object.GetYaxis().GetBinLowEdge(iy))
                    for c in ch_list:
                      if c["y_eta"] == x and c["x_phi"] == y: break
                    else: continue
                    run_dict["label"].append(f"{supermodule} [+{y}, +{x}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif "EE" in supermodule: #y -> iy, x -> ix
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                    for c in ch_list:
                      if c["y_eta"] == x and c["x_phi"] == y: break
                    else: continue
                    run_dict["label"].append(f"{supermodule} [+{x}, +{y}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


class RMSHistory_nocuts(Plugin):
    def __init__(self, buildopener, ch_list):
        Plugin.__init__(self, buildopener, folder="", plot_name="")
        self.channel_list = ch_list

    def process_one_run(self, run_info):
        #dictionary with single run status info to fill with histogram data
        run_dict = {"label": [], "value": []}

        status_dict = ChannelStatus(self.buildopener).get_status_dict(run_info)

        #EB
        EBsupermodules_list = ECAL.EBsupermodules_list
        for i, EBsupermodule in enumerate(EBsupermodules_list):
            currentSM_ch_list = []
            for c in self.channel_list:
              if c["SM"] == EBsupermodule:
                currentSM_ch_list.append(c)
            if len(currentSM_ch_list) == 0: continue
            self.folder = "EcalBarrel/EBPedestalOnlineClient/"
            self.plot_name = f"EBPOT pedestal rms map G12 {EBsupermodule}"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, run_dict, EBsupermodule, status_dict, currentSM_ch_list)

        #EE
        EEsupermodules_list = ECAL.EEsupermodules_list
        for i, EEsupermodule in enumerate(EEsupermodules_list):
            currentSM_ch_list = []
            for c in self.channel_list:
              if c["SM"] == EBsupermodule:
                currentSM_ch_list.append(c)
            if len(currentSM_ch_list) == 0: continue
            self.folder = "EcalEndcap/EEPedestalOnlineClient/"
            self.plot_name = f"EEPOT pedestal rms map G12 {EEsupermodule}"
            self.serverurl_online = "online"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, run_dict, EEsupermodule, status_dict, currentSM_ch_list)

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
        run_df = run_df.sort_values(by=["detector_priority", "sm_ch", "iphi_ix", "ieta_iy"]) #.drop(columns=["detector_priority","detector", "sm_ch", "iphi_ix", "ieta_iy"])
        df_high = run_df.loc[run_df["value"] > UP_LIMIT]
        df_low = run_df.loc[run_df["value"] < LOW_LIMIT]

        #filling RMS > 300 history plot
        self.fill_history_subplots(df_high, available_runs, f"RMS_channels_greater_{UP_LIMIT}", f"{save_path}", change_hist_limits=True)
        #filling RMS < 100 history plot
        self.fill_history_subplots(df_low, available_runs, f"RMS_channels_less_{LOW_LIMIT}", f"{save_path}", change_hist_limits=True)

        run_df.loc[run_df.detector.str.contains("EB")].drop(columns=["label","detector","detector_priority"]).to_csv(f"{save_path}/EB_RMSHistory.csv", index=None)

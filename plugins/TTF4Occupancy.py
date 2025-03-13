import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from collections import Counter
from Plugin import Plugin
import ECAL



def read_hist(one_run_root_object, detector, df, supermodules_FED, run_dict):
    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    if detector == "EB":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                    df_phi = df[df["iphi"] == x+1] #+1 because the low edge belongs to the previous SM
                    df_phi_eta = df_phi[df_phi["ieta"] == y+1] #+1 because the low edge belongs to the previous SM
                    info_dict = ECAL.fill_tcc_tt(df_phi_eta, supermodules_FED)
                    run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} TT{info_dict['tt_ccu']}")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
    if detector == "EE-":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    if not df_x_y.empty:
                        df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                        info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED)
                        run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} TT{info_dict['tt_ccu']}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
    if detector == "EE+":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    if not df_x_y.empty:
                        df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                        info_dict = ECAL.fill_tcc_tt(df_x_y_p, supermodules_FED)
                        run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} TT{info_dict['tt_ccu']}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


#remove those multiple tt/ccu labels to avoid repetitions in the summary plot 
def remove_doubles(run_dict):
    sm_tt = run_dict["label"]
    values = run_dict["value"]
    if not sm_tt or not values:
        return {"label": [], "value": []}
    tt_map = {}
    eb_map = {}
    for ch, val in zip(sm_tt, values):
        parts = ch.split()
        region, tcc, tt = parts[0], parts[1], parts[2]
        if region.startswith("EB"):
            eb_map[ch] = val
        else:
            key = (region[0:3], tcc, tt)
            if key not in tt_map:
                tt_map[key] = []
            tt_map[key].append(ch)
    cleaned_sm_tt = list(eb_map.keys())
    cleaned_values = list(eb_map.values())
    for key, labels in tt_map.items():
        if len(set(labels)) > 1:
            counter = Counter(labels)
            chosen_label = max(counter, key=counter.get)
        else:
            chosen_label = labels[0]
        index = sm_tt.index(chosen_label)
        cleaned_sm_tt.append(chosen_label)
        cleaned_values.append(values[index])
    max_value = max(cleaned_values)
    normalized_values = [v / max_value for v in cleaned_values]
    return {"label": cleaned_sm_tt, "value": normalized_values}


class TTF4Occupancy(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    def process_one_run(self, run_info):
        #load the file with all the info about the ECAL channels
        channels_df = pd.read_csv("/eos/user/d/delvecch/www/PFG/ecalchannels.csv")
        #info for matching the SM with fed number
        supermodules_FED = ECAL.supermodules_FED_match
        #dictionary with single run info to fill with histogram data
        run_dict = {"label": [], "value": []}

        #EB
        self.folder = "EcalBarrel/EBTriggerTowerTask/"
        self.plot_name = "EBTTT TTF4 Occupancy"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EB", channels_df, supermodules_FED, run_dict)
        
        #EE-
        self.folder = "EcalEndcap/EETriggerTowerTask/"
        self.plot_name = "EETTT TTF4 Occupancy EE -"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE-", channels_df, supermodules_FED, run_dict)

        #EE+
        self.folder = "EcalEndcap/EETriggerTowerTask/"
        self.plot_name = "EETTT TTF4 Occupancy EE +"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE+", channels_df, supermodules_FED, run_dict)

        #fill _data inside generic Plugin class after removing repetitions
        run_dict_unique = remove_doubles(run_dict)
        self.fill_data_one_run(run_info, run_dict_unique)


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
        run_df[["detector", "sm_num", "tcc_num", "tt_num"]] = run_df["label"].str.extract(r'(EB|EE)([+-]?\d+)\s+TCC(\d+)\s+TT(\d+)')
        run_df["sm_num"] = run_df["sm_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df["tcc_num"] = run_df["tcc_num"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_num", "tcc_num", "tt_num"]).drop(columns=["detector_priority",
        "sm_num", "tcc_num", "tt_num", "detector"])

        #filling history plot
        self.fill_history_subplots(run_df, available_runs, "TTF4Occupancy", f"{save_path}")
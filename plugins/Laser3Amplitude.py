import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd
import numpy as np

from Plugin import Plugin
from EELightMonitoringRegions import EELightMR
import ECAL



def read_hist_EB(one_run_root_object, supermodule, Ichannels, Lchannels):
    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    sm = int(supermodule[2:])
    if sm < 0:
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                if isIBlock(sm, one_run_root_object, ix, iy):
                    Ichannels["SM_ch"].append(f"{supermodule} [+{y}, -{x}]")
                    Ichannels["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif isLBlock(sm, one_run_root_object, ix, iy):
                    Lchannels["SM_ch"].append(f"{supermodule} [+{y}, -{x}]")
                    Lchannels["value"].append(one_run_root_object.GetBinContent(ix, iy))
    elif sm > 0:
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                y = int(-one_run_root_object.GetYaxis().GetBinLowEdge(iy))
                if isIBlock(sm, one_run_root_object, ix, iy):
                    Ichannels["SM_ch"].append(f"{supermodule} [+{y}, +{x}]")
                    Ichannels["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif isLBlock(sm, one_run_root_object, ix, iy):
                    Lchannels["SM_ch"].append(f"{supermodule} [+{y}, +{x}]")
                    Lchannels["value"].append(one_run_root_object.GetBinContent(ix, iy))


def read_hist_EE(one_run_root_object, supermodule, EEchannels):
    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    for iy in range(1, nbinsy+1):
        for ix in range(1, nbinsx+1):
            if abs(one_run_root_object.GetBinContent(ix, iy)) != 0:
                x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                EEchannels["SM_ch"].append(f"{supermodule} [+{x}, +{y}]")
                EEchannels["value"].append(one_run_root_object.GetBinContent(ix, iy))
                EEchannels["LightMR"].append(EELightMR(x, y))


def isIBlock(sm_num, one_run_root_object, ix, iy):
    a = abs(int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))) > 5
    l1 = abs(sm_num) * 20
    l2 = l1 - 20
    low = l1 if sm_num > 0 else l2
    b = abs(int(-one_run_root_object.GetYaxis().GetBinLowEdge(iy)) - low) < 10 if sm_num > 0 else abs(int(one_run_root_object.GetYaxis().GetBinUpEdge(iy)) - low) <= 10
    block = a and b
    return block


def isLBlock(sm_num, one_run_root_object, ix, iy):
    return not isIBlock(sm_num, one_run_root_object, ix, iy)


def dividebymedian_EB(Ichannels, Lchannels):
    #I region
    Ichannels_array = np.array(Ichannels["value"])
    Imedian = np.median(Ichannels_array)
    if Imedian != 0:
        Ichannels_val_over_median = Ichannels_array / Imedian
        Ichannels["value"] = Ichannels_val_over_median.tolist()
    #L region
    Lchannels_array = np.array(Lchannels["value"])
    Lmedian = np.median(Lchannels_array)
    if Lmedian != 0:
        Lchannels_val_over_median = Lchannels_array / Lmedian
        Lchannels["value"] = Lchannels_val_over_median.tolist()


def dividebymedian_EE(EEchannels):
    df = pd.DataFrame(EEchannels)
    medians_by_region = df.groupby("LightMR")["value"].transform("median")
    df["normalized_value"] = df["value"] / medians_by_region
    EEchannels["value"] = df["normalized_value"].tolist()


def check_common_channels(run_dict_temp):
    runs_to_remove = [run for run, data in run_dict_temp.items() if all(abs(val) == 0 for val in data["value"])]
    for run in runs_to_remove:
        del run_dict_temp[run]
    if not run_dict_temp:
        return
    common_channels = set(run_dict_temp[next(iter(run_dict_temp))]["SM_ch"])
    for run_data in run_dict_temp.values():
        common_channels &= set(run_data["SM_ch"])
    for run, data in run_dict_temp.items():
        filtered_SM_ch = []
        filtered_value = []
        for ch, val in zip(data["SM_ch"], data["value"]):
            if ch in common_channels:
                filtered_SM_ch.append(ch)
                filtered_value.append(val)
        data["SM_ch"] = filtered_SM_ch
        data["value"] = filtered_value
    return run_dict_temp.keys()


def getBadXY(available_runs, run_dict_temp, run_dict):
    channels_array = np.array([run_dict_temp[run]["SM_ch"] for run in available_runs])
    values_array = np.array([run_dict_temp[run]["value"] for run in available_runs])
    values_array[values_array == -0] = 0
    zero_cols = np.any(abs(values_array) == 0, axis=0)
    mask_keep_cols = ~zero_cols
    channels_filtered = channels_array[:, mask_keep_cols]
    values_filtered = values_array[:, mask_keep_cols]
    medians_over_runs = np.median(values_filtered, axis=0)
    MEDIANUP_EB = 1.15
    MEDIANLOW_EB = 0.85
    MEDIANUP_EE = 1.30
    MEDIANLOW_EE = 0.70
    num_channels = values_filtered.shape[1]
    for i in range(num_channels):
        values_column = values_filtered[:, i]
        channels = channels_filtered[:, i]
        median = medians_over_runs[i]
        for j, run in enumerate(available_runs):
            if "EB" in channels[0]:
                lower_bound = median * MEDIANLOW_EB
                upper_bound = median * MEDIANUP_EB
                if values_column[j] < lower_bound or values_column[j] > upper_bound:
                    run_dict["SM_ch"].extend(channels.tolist())
                    run_dict["value"].extend(values_column.tolist())
                    run_dict["run"].extend(list(available_runs))
                    break
            elif "EE" in channels[0]:
                lower_bound = median * MEDIANLOW_EE
                upper_bound = median * MEDIANUP_EE
                if values_column[j] < lower_bound or values_column[j] > upper_bound:
                    run_dict["SM_ch"].extend(channels.tolist())
                    run_dict["value"].extend(values_column.tolist())
                    run_dict["run"].extend(list(available_runs))
                    break


def df_to_hist(row, hist, tower_list, run_list):
    hist.Fill(run_list.index(row["run"])+1, tower_list.index(row["SM_ch"])+1, row["value"])


def hist_config(run_list, tower_list, hist, ybin_start, ybin_end, name, eos_site):
    #axis labels
    for ix, run in enumerate(run_list, start=1):
        hist.GetXaxis().SetBinLabel(ix, str(run))
    for iy in range(ybin_end-ybin_start):
        hist.GetYaxis().SetBinLabel(iy+1, str(tower_list[ybin_start+iy]))
    #canva settings
    canva = ROOT.TCanvas(f"canva_{name}", "", 3600, 2250)
    canva.SetGrid()
    ROOT.gStyle.SetLineColor(ROOT.kGray+1)
    ROOT.gStyle.SetLineStyle(3)
    canva.SetLeftMargin(0.18)
    canva.SetRightMargin(0.15)
    canva.SetTopMargin(0.05)
    canva.SetBottomMargin(0.15)
    #hist settings
    hist.SetStats(False)
    hist.GetXaxis().LabelsOption("v")
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetZaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTickLength(0.03)
    hist.GetYaxis().SetTickLength(0.02)
    hist.GetZaxis().SetTickLength(0.02)
    hist.SetMinimum(0.)
    hist.SetMarkerSize(1.5)
    ROOT.gStyle.SetPaintTextFormat(".1e")
    hist.Draw("text COLZ")
    canva.Modified()
    canva.Update()
    #saving
    canva.SaveAs(f"{eos_site}{name}.pdf")
    canva.SaveAs(f"{eos_site}{name}.png")
    canva.SaveAs(f"{eos_site}{name}.root")


class Laser3Amplitude(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    #process single run, for both barrel and endcap
    def process_one_run(self, run_info):
        run_dict = {"SM_ch": [], "value":[]}

        #barrel supermodules
        EBsupermodules_list = ECAL.EBsupermodules_list
        #loop on barrel supermodules
        for i, EBsupermodule in enumerate(EBsupermodules_list):
            self.folder = "EcalBarrel/EBLaserTask/Laser3/"
            self.plot_name = f"EBLT amplitude {EBsupermodule} L3"
            Ichannels = {"SM_ch": [], "value": []}
            Lchannels = {"SM_ch": [], "value": []}
            one_run_root_object = self.get_root_object(run_info)
            read_hist_EB(one_run_root_object, EBsupermodule, Ichannels, Lchannels)
            dividebymedian_EB(Ichannels, Lchannels)
            run_dict["SM_ch"].extend(Ichannels["SM_ch"] + Lchannels["SM_ch"])
            run_dict["value"].extend(Ichannels["value"] + Lchannels["value"])
        
        #endcap supermodules
        EEsupermodules_list = ECAL.EEsupermodules_list
        #loop on endcap supermodules
        for i, EEsupermodule in enumerate(EEsupermodules_list):
            self.folder = "EcalEndcap/EELaserTask/Laser3/"
            self.plot_name = f"EELT amplitude {EEsupermodule} L3"
            EEchannels = {"SM_ch": [], "value": [], "LightMR": []}
            one_run_root_object = self.get_root_object(run_info)
            read_hist_EE(one_run_root_object, EEsupermodule, EEchannels)
            dividebymedian_EE(EEchannels)
            run_dict["SM_ch"].extend(EEchannels["SM_ch"])
            run_dict["value"].extend(EEchannels["value"])
        
        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)

    
    def create_history_plots(self):
        #copy the single runs dict into a temporary dict
        available_runs = self.get_available_runs()
        run_dict_temp = {}
        for i, run in enumerate(available_runs):
            data_one_run = self.get_data_one_run(run)
            run_dict_temp[run] = data_one_run
        available_runs_filtered = check_common_channels(run_dict_temp)
        run_dict = {"SM_ch": [], "value": [], "run": []}
        getBadXY(available_runs_filtered, run_dict_temp, run_dict)

        #from dict to dataframe + ordering
        run_df = pd.DataFrame(run_dict)
        run_df[["detector", "sm_ch", "iphi_ix", "ieta_iy"]] = run_df["SM_ch"].str.extract(r'(EB|EE)([+-]?\d+)\s+\[([+-]?\d+),\s*([+-]?\d+)\]')
        run_df["sm_ch"] = run_df["sm_ch"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_ch", "iphi_ix", "ieta_iy"]).drop(columns=["detector_priority",
        "detector", "sm_ch", "iphi_ix", "ieta_iy"])
        df_EB = run_df.loc[run_df["SM_ch"].str.contains("EB", case=False)]
        df_EE = run_df.loc[run_df["SM_ch"].str.contains("EE", case=False)]

        #EB plot
        tower_list = list(pd.unique(df_EB.SM_ch))
        run_list = list(available_runs_filtered)
        hist = ROOT.TH2F(f"Laser3Amplitude_EB", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
        df_EB.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)
        #filling the subhistograms
        nbinsy = hist.GetNbinsY()
        max_bins = 15
        n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
        for i in range(n_subhist):
            ybin_start = i * max_bins
            ybin_end = min((i+1) * max_bins, nbinsy)
            subhist = ROOT.TH2F(f"Laser3Amplitude_EB_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start, ybin_start, ybin_end+1)
            for ix in range(len(run_list)):
                for iy in range(ybin_end-ybin_start):
                    subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))
            if n_subhist == 1:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, "Laser3Amplitude_EB", "/eos/user/d/delvecch/www/PFG/")
            else:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"Laser3Amplitude_EB_part{i+1}", "/eos/user/d/delvecch/www/PFG/")

        #EE plot
        tower_list = list(pd.unique(df_EE.SM_ch))
        run_list = list(available_runs_filtered)
        hist = ROOT.TH2F(f"Laser3Amplitude_EE", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
        df_EE.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)
        #filling the subhistograms
        nbinsy = hist.GetNbinsY()
        max_bins = 15
        n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
        for i in range(n_subhist):
            ybin_start = i * max_bins
            ybin_end = min((i+1) * max_bins, nbinsy)
            subhist = ROOT.TH2F(f"Laser3Amplitude_EE_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start, ybin_start, ybin_end+1)
            for ix in range(len(run_list)):
                for iy in range(ybin_end-ybin_start):
                    subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))
            if n_subhist == 1:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, "Laser3Amplitude_EE", "/eos/user/d/delvecch/www/PFG/")
            else:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"Laser3Amplitude_EE_part{i+1}", "/eos/user/d/delvecch/www/PFG/")

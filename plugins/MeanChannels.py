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
                    run_dict["SM_ch"].append(f"{supermodule} [+{y}, -{x}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif "EB+" in supermodule: #y -> iphi, x -> ieta
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(-one_run_root_object.GetYaxis().GetBinLowEdge(iy))
                    run_dict["SM_ch"].append(f"{supermodule} [+{y}, +{x}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                elif "EE" in supermodule: #y -> iy, x -> ix
                    x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                    y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                    run_dict["SM_ch"].append(f"{supermodule} [+{x}, +{y}]")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


def df_to_hist(row, hist, tower_list, run_list):
    hist.Fill(run_list.index(row["run"])+1, tower_list.index(row["SM_ch"])+1, row["value"])


def hist_config(run_list, tower_list, hist, ybin_start, ybin_end, name, eos_site, option=0): #option = 0 -> z in [0, 1], option = 1 -> z > 300, option = 2 -> z < 100
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
    canva.SetRightMargin(0.12)
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
    if option == 1:
        hist.SetMinimum(300.)
        hist.SetMaximum(hist.GetMaximum())
    elif option == 2:
        hist.SetMaximum(100.)
        hist.SetMinimum(hist.GetMinimum())
    hist.SetMarkerSize(1.5)
    ROOT.gStyle.SetPaintTextFormat(".1e")
    hist.Draw("text COLZ")
    canva.Modified()
    canva.Update()
    #saving
    canva.SaveAs(f"{eos_site}{name}.pdf")
    canva.SaveAs(f"{eos_site}{name}.png")
    canva.SaveAs(f"{eos_site}{name}.root")


class MeanChannels(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    #process single run, all the supermodules for both barrel and endcap
    def process_one_run(self, run_info):
        #dictionary with single run status info
        run_dict = {"SM_ch": [], "value": []}

        #barrel supermodules
        EBsupermodules_list = ECAL.EBsupermodules_list
        #loop on barrel supermodules
        for i, EBsupermodule in enumerate(EBsupermodules_list):
            self.folder = "EcalBarrel/EBPedestalOnlineTask/Gain12/"
            self.plot_name = f"EBPOT pedestal {EBsupermodule} G12"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, run_dict, EBsupermodule)

        #endcap supermodules
        EEsupermodules_list = ECAL.EEsupermodules_list
        #loop on endcap supermodules
        for i, EEsupermodule in enumerate(EEsupermodules_list):
            self.folder = "EcalEndcap/EEPedestalOnlineTask/Gain12/"
            self.plot_name = f"EEPOT pedestal {EEsupermodule} G12"
            self.serverurl_online = "online"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, run_dict, EEsupermodule)
        
        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)


    def create_history_plots(self):
        available_runs = self.get_available_runs()
        run_dict = {"SM_ch": [], "value": [], "run": []}
        for i, run in enumerate(available_runs):
            data_one_run = self.get_data_one_run(run)
            for key in data_one_run:
                run_dict[key] += data_one_run[key]
            run_dict["run"] += [run for j in range(len(data_one_run["SM_ch"]))]
        #from dict to dataframe + ordering
        run_df = pd.DataFrame(run_dict)
        run_df[["detector", "sm_ch", "iphi_ix", "ieta_iy"]] = run_df["SM_ch"].str.extract(r'(EB|EE)([+-]?\d+)\s+\[([+-]?\d+),\s*([+-]?\d+)\]')
        run_df["sm_ch"] = run_df["sm_ch"].astype(int)
        run_df["iphi_ix"] = run_df["iphi_ix"].astype(int)
        run_df["ieta_iy"] = run_df["ieta_iy"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_ch", "iphi_ix", "ieta_iy"]).drop(columns=["detector_priority",
        "detector", "sm_ch", "iphi_ix", "ieta_iy"])
        df_high = run_df.loc[run_df["value"] > 300]
        df_low = run_df.loc[run_df["value"] < 100]

        #mean > 300
        tower_list = list(pd.unique(df_high.SM_ch))
        run_list = list(available_runs)
        hist = ROOT.TH2F(f"MeanChannels_greater300", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
        df_high.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)
        #filling the subhistograms
        nbinsy = hist.GetNbinsY()
        max_bins = 15
        n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
        for i in range(n_subhist):
            ybin_start = i * max_bins
            ybin_end = min((i+1) * max_bins, nbinsy)
            subhist = ROOT.TH2F(f"MeanChannels_greater300_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start, ybin_start, ybin_end+1)
            for ix in range(len(run_list)):
                for iy in range(ybin_end-ybin_start):
                    subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))
            if n_subhist == 1:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, "mean_channels_greater_300", "/eos/user/d/delvecch/www/PFG/", option = 1)
            else:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"mean_channels_greater_300_part{i+1}", "/eos/user/d/delvecch/www/PFG/", option = 1)
        
        #mean < 100
        tower_list = list(pd.unique(df_low.SM_ch))
        run_list = list(available_runs)
        hist = ROOT.TH2F(f"MeanChannels_less100", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
        df_low.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)
        #filling the subhistograms
        nbinsy = hist.GetNbinsY()
        max_bins = 15
        n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
        for i in range(n_subhist):
            ybin_start = i * max_bins
            ybin_end = min((i+1) * max_bins, nbinsy)
            subhist = ROOT.TH2F(f"MeanChannels_less100_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start, ybin_start, ybin_end+1)
            for ix in range(len(run_list)):
                for iy in range(ybin_end-ybin_start):
                    subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))
            if n_subhist == 1:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, "mean_channels_less_100", "/eos/user/d/delvecch/www/PFG/", option = 2)
            else:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"mean_channels_less_100_part{i+1}", "/eos/user/d/delvecch/www/PFG/", option = 2)
        
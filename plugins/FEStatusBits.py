import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from Plugin import Plugin



def read_hist(one_run_root_object, labels, run_dict, supermodule):
    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    yproj = one_run_root_object.ProjectionY("yproj", 1, 1)
    #loop on the TH2F histogram: iy -> labels, ix -> trigger tower
    for iy in range(1, nbinsy+1):
        if labels[iy-1] == "ENABLED" or labels[iy-1] == "SUPPRESSED":
            continue
        for ix in range(1, nbinsx+1):
            if one_run_root_object.GetBinContent(ix, iy) != 0:
                run_dict["tower"].append(f"{supermodule} TT{ix}")
                run_dict["status"].append(iy)
                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy)/yproj.GetEntries())


def df_to_hist(row, hist, tower_list, run_list):
    hist.Fill(run_list.index(row["run"])+1, tower_list.index(row["tower"])+1, row["value"])


def general_settings(n_contours):
    ROOT.gStyle.SetNumberContours(n_contours)
    ROOT.gStyle.SetPalette(ROOT.kBeach)
    ROOT.TColor.InvertPalette()


def hist_config(run_list, tower_list, hist, ybin_start, ybin_end, status, eos_site):
    #axis labels
    for ix, run in enumerate(run_list, start=1):
        hist.GetXaxis().SetBinLabel(ix, str(run))
    for iy in range(ybin_end-ybin_start):
        hist.GetYaxis().SetBinLabel(iy+1, str(tower_list[ybin_start+iy]))
    #canva settings
    canva = ROOT.TCanvas("canva_{status}", "", 3600, 2250)
    canva.SetGrid()
    ROOT.gStyle.SetLineColor(ROOT.kGray+1)
    ROOT.gStyle.SetLineStyle(3)
    canva.SetLeftMargin(0.15)
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
    hist.SetMinimum(0.)
    hist.SetMaximum(1.)
    hist.SetMarkerSize(1.5)
    ROOT.gStyle.SetPaintTextFormat(".1e")
    hist.Draw("text COLZ")
    canva.Modified()
    canva.Update()
    #saving
    canva.SaveAs(f"{eos_site}{status}.pdf")
    canva.SaveAs(f"{eos_site}{status}.png")
    canva.SaveAs(f"{eos_site}{status}.root")


class FEStatusBits(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")

        
    #process single run, all the supermodules for both barrel and endcap
    def process_one_run(self, run_info):
        #labels of the trigger towers bits
        labels = ["ENABLED", "DISABLED", "TIMEOUT", "HEADERERROR", "CHANNELID", "LINKERROR", "BLOCKSIZE", "SUPPRESSED","FORCEDFULLSUPP",
        "L1ADESYNC", "BXDESYNC", "L1ABXDESYNC", "FIFOFULL", "HPARITY", "VPARITY", "FORCEDZS"]        
        #dictionary with single run status info
        run_dict = {"tower": [], "status": [], "value": []}
        
        #barrel supermodules
        EBsupermodules_list = ["EB-18", "EB-17", "EB-16", "EB-15", "EB-14", "EB-13", "EB-12", "EB-11", "EB-10", "EB-09", "EB-08",
        "EB-07", "EB-06", "EB-05", "EB-04", "EB-03", "EB-02", "EB-01", "EB+01", "EB+02", "EB+03", "EB+04", "EB+05", "EB+06", "EB+07",
        "EB+08", "EB+09", "EB+10", "EB+11", "EB+12", "EB+13", "EB+14", "EB+15", "EB+16", "EB+17", "EB+18"]
        #loop on barrel supermodules
        for i, EBsupermodule in enumerate(EBsupermodules_list):
            self.folder = "EcalBarrel/EBStatusFlagsTask/FEStatus/"
            self.plot_name = f"EBSFT front-end status bits {EBsupermodule}"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, labels, run_dict, EBsupermodule)
                        
        #endcap supermodules
        EEsupermodules_list = ["EE-09", "EE-08", "EE-07", "EE-06", "EE-05", "EE-04", "EE-03", "EE-02", "EE-01", "EE+01", "EE+02", "EE+03", "EE+04", "EE+05", "EE+06", "EE+07", "EE+08", "EE+09"]
        #loop on endcap supermodules
        for i, EEsupermodule in enumerate(EEsupermodules_list):
            self.folder = "EcalEndcap/EEStatusFlagsTask/FEStatus/"
            self.plot_name = f"EESFT front-end status bits {EEsupermodule}"
            one_run_root_object = self.get_root_object(run_info)
            read_hist(one_run_root_object, labels, run_dict, EEsupermodule)
            
        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)

        
    #history plot function
    def create_history_plots(self):
        general_settings(255)
        available_runs = self.get_available_runs()
        run_dict = {"tower": [], "status": [], "value": [], "run": []}
        for i, run in enumerate(available_runs):
            data_one_run = self.get_data_one_run(run)
            for key in data_one_run:
                run_dict[key] += data_one_run[key]
            run_dict["run"] += [run for j in range(len(data_one_run["tower"]))]
        #from dict to dataframe + ordering
        run_df = pd.DataFrame(run_dict)
        run_df[["detector", "tower_num", "tt_num"]] = run_df["tower"].str.extract(r'(EB|EE)([+-]?\d+)\s+TT(\d+)')
        run_df["tower_num"] = run_df["tower_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df = run_df.sort_values(by=["detector_priority", "tower_num", "tt_num"]).drop(columns=["detector_priority", "tower_num", "tt_num", "detector"])

        #creating the initial histograms
        statuses = {"ENABLED": 1, "DISABLED": 2, "TIMEOUT": 3, "HEADERERROR": 4, "CHANNELID": 5, "LINKERROR": 6, "BLOCKSIZE": 7, "SUPPRESSED": 8,"FORCEDFULLSUPP": 9, "L1ADESYNC": 10, "BXDESYNC": 11, "L1ABXDESYNC": 12, "FIFOFULL": 13, "HPARITY": 14, "VPARITY": 15, "FORCEDZS": 16}
        for i, stat in enumerate(statuses):
            curr_df = run_df[run_df.status == statuses[stat]]
            tower_list = list(pd.unique(curr_df.tower))
            run_list = list(available_runs)
            run_list_stat = list(pd.unique(curr_df.run))
            if not run_list_stat:
                continue
            hist = ROOT.TH2F(f"FEStatusBits_{stat}", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
            curr_df.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)

            #filling the subhistograms
            nbinsy = hist.GetNbinsY()
            max_bins = 15
            n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
            for i in range(n_subhist):
                ybin_start = i * max_bins
                ybin_end = min((i+1) * max_bins, nbinsy)
                subhist = ROOT.TH2F(f"FEStatusBits_{stat}_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start, ybin_start, ybin_end+1)
                for ix in range(len(run_list)):
                    for iy in range(ybin_end-ybin_start):
                        subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))
                if n_subhist == 1:
                    hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"FEStatusBits_{stat}", "/eos/user/d/delvecch/www/PFG/")
                else:
                    hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"FEStatusBits_{stat}_part{i+1}", "/eos/user/d/delvecch/www/PFG/")
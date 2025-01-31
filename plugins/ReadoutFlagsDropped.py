import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd
import numpy as np
from array import array

from Plugin import Plugin



def df_to_hist(row, hist, tower_list, run_list):
    hist.Fill(run_list.index(row["run"])+1, tower_list.index(row["tower"])+1, row["value"])


class ReadoutFlagsDropped(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    #process single run, for both barrel and endcap
    def process_one_run(self, run_info):
        #dataframe with relative SM, TT and (eta, phi) for channels
        df = pd.read_csv("/eos/user/d/delvecch/www/PFG/ecalchannels.csv")
        #dictionary for match between the SM and FE
        supermodules_FED = {"EB-18": 627, "EB-17": 626, "EB-16": 625, "EB-15": 624, "EB-14": 623, "EB-13": 622, "EB-12": 621, "EB-11": 620,
        "EB-10": 619, "EB-09": 618, "EB-08": 617, "EB-07": 616, "EB-06": 615, "EB-05": 614, "EB-04": 613, "EB-03": 612, "EB-02": 611,
        "EB-01": 610, "EB+01": 628, "EB+02": 629, "EB+03": 630, "EB+04": 631, "EB+05": 632, "EB+06": 633, "EB+07": 634, "EB+08": 635,
        "EB+09": 636, "EB+10": 637, "EB+11": 638, "EB+12": 639, "EB+13": 640, "EB+14": 641, "EB+15": 642, "EB+16": 643, "EB+17": 644,
        "EB+18": 645}
        #dictionary with single run info
        run_dict = {"tower": [], "value": []}

        #barrel single run
        self.folder = "EcalBarrel/EBSelectiveReadoutTask/"
        self.plot_name = "EBSRT FR Flagged Dropped Readout"
        self.serverurl_online = "online"
        print(self.serverurl_online)
        one_run_root_object = self.get_root_object(run_info)
        nbinsx = one_run_root_object.GetNbinsX()
        nbinsy = one_run_root_object.GetNbinsY()
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                    df_phi = df[df["iphi"] == x+1] #+1 because the low edge belongs to the previous SM
                    df_phi_eta = df_phi[df_phi["ieta"] == y+1] #+1 because the low edge belongs to the previous SM
                    EB_SM = next((key for key, fe in supermodules_FED.items() if fe == df_phi_eta["fed"].iloc[0]), None)
                    tt = df_phi_eta["tower"].iloc[0]
                    run_dict["tower"].append(f"{EB_SM} TT{tt}")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))

        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)


    #history plot function
    def create_history_plots(self):
        available_runs = self.get_available_runs()
        run_dict = {"tower": [], "value": [], "run": []}
        for i, run in enumerate(available_runs):
            data_one_run = self.get_data_one_run(run)
            for key in data_one_run:
                run_dict[key] += data_one_run[key]
            run_dict["run"] += [run for j in range(len(data_one_run["tower"]))]
        #from dict to dataframe
        run_df = pd.DataFrame(run_dict)
        run_df[["sm_num", "tt_num"]] = run_df["tower"].str.extract(r'EB([+-]?\d+)\s+TT(\d+)')
        run_df["sm_num"] = run_df["sm_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df = run_df.sort_values(by=["sm_num", "tt_num"]).drop(columns=["sm_num", "tt_num"])

        #general settings for the canvas
        ROOT.gStyle.SetNumberContours(255)
        ROOT.gStyle.SetPalette(ROOT.kBeach)
        #ROOT.TColor.InvertPalette()
        ROOT.gStyle.SetLabelSize(0.06)

        tower_list = list(pd.unique(run_df.tower))
        run_list = list(pd.unique(run_df.run))
        hist = ROOT.TH2F(f"ReadoutFlagsDropped", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
        run_df.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)

        #number of subhist
        nbinsy = hist.GetNbinsY()
        max_bins = 15
        n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
        if n_subhist == 1:
            #axis labels
            for ix, run in enumerate(run_list, start=1):
                hist.GetXaxis().SetBinLabel(ix, str(run))
            for iy, tower in enumerate(tower_list, start=1):
                hist.GetYaxis().SetBinLabel(iy, str(tower))
                
            #canvas options
            c = ROOT.TCanvas("c", "", 3600, 2250)
            c.SetGrid()
            ROOT.gStyle.SetLineColor(ROOT.kGray+1)
            ROOT.gStyle.SetLineStyle(3)
            c.SetLeftMargin(0.15)
            c.SetRightMargin(0.12)
            c.SetTopMargin(0.05)
            c.SetBottomMargin(0.15)
            c.Modified()
            c.Update()

            #hist options
            hist.SetStats(False)
            hist.GetXaxis().LabelsOption("v")
            hist.GetXaxis().SetLabelSize(0.06)
            hist.GetYaxis().SetLabelSize(0.06)
            hist.GetZaxis().SetLabelSize(0.06)
            hist.GetXaxis().SetTickLength(0.03)
            hist.GetYaxis().SetTickLength(0.02)
            hist.GetZaxis().SetTickLength(0.02)
            hist.SetMinimum(0.)
            hist.SetMaximum(1.)
            hist.SetMarkerSize(1.5)
            ROOT.gStyle.SetPaintTextFormat(".1e")
            hist.Draw("text COLZ")
            c.Modified()
            c.Update()

            #save
            c.SaveAs(f"/eos/user/d/delvecch/www/PFG/ReadoutFlagsDropped.pdf")
            c.SaveAs(f"/eos/user/d/delvecch/www/PFG/ReadoutFlagsDropped.png")
            c.SaveAs(f"/eos/user/d/delvecch/www/PFG/ReadoutFlagsDropped.root")

        else:
            for i in range(n_subhist):
                ybin_start = i * max_bins
                ybin_end = min((i+1) * max_bins, nbinsy)
                subhist = ROOT.TH2F(f"ReadoutFlagsDropped_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start,
                ybin_start, ybin_end+1)
                for ix in range(len(run_list)):
                    for iy in range(ybin_end-ybin_start):
                        subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))

                #axis labels
                for ix, run in enumerate(run_list, start=1):
                    subhist.GetXaxis().SetBinLabel(ix, str(run))
                for iy in range(ybin_end-ybin_start):
                    subhist.GetYaxis().SetBinLabel(iy+1, str(tower_list[ybin_start+iy]))

                #canvas options
                c = ROOT.TCanvas("c", "", 3600, 2250)
                c.SetGrid()
                ROOT.gStyle.SetLineColor(ROOT.kGray+1)
                ROOT.gStyle.SetLineStyle(3)
                c.SetLeftMargin(0.15)
                c.SetRightMargin(0.12)
                c.SetTopMargin(0.05)
                c.SetBottomMargin(0.15)
                c.Modified()
                c.Update()

                #subhist options
                subhist.SetStats(False)
                subhist.GetXaxis().LabelsOption("v")
                subhist.GetXaxis().SetLabelSize(0.06)
                subhist.GetYaxis().SetLabelSize(0.06)
                subhist.GetZaxis().SetLabelSize(0.06)
                subhist.GetXaxis().SetTickLength(0.03)
                subhist.GetYaxis().SetTickLength(0.02)
                subhist.GetZaxis().SetTickLength(0.02)
                subhist.SetMinimum(0.)
                subhist.SetMaximum(1.)
                subhist.SetMarkerSize(1.5)
                ROOT.gStyle.SetPaintTextFormat(".1e")
                subhist.Draw("text COLZ")
                c.Modified()
                c.Update()

                #save
                c.SaveAs(f"/eos/user/d/delvecch/www/PFG/ReadoutFlagsDropped_part{i+1}.pdf")
                c.SaveAs(f"/eos/user/d/delvecch/www/PFG/ReadoutFlagsDropped_part{i+1}.png")
                c.SaveAs(f"/eos/user/d/delvecch/www/PFG/ReadoutFlagsDropped_part{i+1}.root")
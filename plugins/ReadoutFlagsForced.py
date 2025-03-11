import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

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
                    run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} TT{info_dict['tt_ccu']}")
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
                        info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                        run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                            info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                            run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                                run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                                run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
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
                        info_dict = ECAL.fill_tcc_tt(df_x_y_p, supermodules_FED, key=1)
                        run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                            info_dict = ECAL.fill_tcc_tt(df_x_y_p, supermodules_FED, key=1)
                            run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_p, supermodules_FED, key=1)
                                run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_p, supermodules_FED, key=1)
                                run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


def df_to_hist(row, hist, tower_list, run_list):
    hist.Fill(run_list.index(row["run"])+1, tower_list.index(row["tower"])+1, row["value"])


def hist_config(run_list, tower_list, hist, ybin_start, ybin_end, name, eos_site):
    #axis labels
    for ix, run in enumerate(run_list, start=1):
        hist.GetXaxis().SetBinLabel(ix, str(run))
    for iy in range(ybin_end-ybin_start):
        hist.GetYaxis().SetBinLabel(iy+1, str(tower_list[ybin_start+iy]))
    #canva settings
    canva = ROOT.TCanvas(f"canva_{name}", "", 3600, 2000)
    canva.SetGrid()
    ROOT.gStyle.SetLineColor(ROOT.kGray+1)
    ROOT.gStyle.SetLineStyle(3)
    canva.SetLeftMargin(0.2)
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
    canva.SaveAs(f"{eos_site}{name}.pdf")
    canva.SaveAs(f"{eos_site}{name}.png")
    canva.SaveAs(f"{eos_site}{name}.root")


class ReadoutFlagsForced(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    #process single run
    def process_one_run(self, run_info):
        #dataframe with relative SM, TT and (eta, phi) for channels
        df = pd.read_csv("/eos/user/d/delvecch/www/PFG/ecalchannels.csv")
        #dictionary for matching between the SM and FE
        supermodules_FED = ECAL.supermodules_FED_match
        #dictionary with single run info
        run_dict = {"tower": [], "value": []}

        #EB
        self.folder = "EcalBarrel/EBSelectiveReadoutTask/"
        self.plot_name = "EBSRT readout unit with SR forced"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EB", df, supermodules_FED, run_dict)
        
        #EE-
        self.folder = "EcalEndcap/EESelectiveReadoutTask/"
        self.plot_name = "EESRT readout unit with SR forced EE -"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE-", df, supermodules_FED, run_dict)

        #EE+
        self.folder = "EcalEndcap/EESelectiveReadoutTask/"
        self.plot_name = "EESRT readout unit with SR forced EE +"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE+", df, supermodules_FED, run_dict)

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
        run_df[["detector", "sm_num", "tcc_num", "tt_ccu", "tt_num"]] = run_df["tower"].str.extract(r'(EB|EE)([+-]?\d+)\s+TCC(\d+)\s+(TT|CCU)(\d+)')
        run_df["sm_num"] = run_df["sm_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df["tcc_num"] = run_df["tcc_num"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df["tt_ccu_priority"] = run_df["tt_ccu"].map({"TT": 0, "CCU": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_num", "tcc_num", "tt_ccu_priority", "tt_num"]).drop(columns=["detector_priority",
        "sm_num", "tcc_num", "tt_ccu_priority", "tt_num", "detector", "tt_ccu"])

        #creating the initial histogram
        tower_list = list(pd.unique(run_df.tower))
        run_list = list(available_runs)
        hist = ROOT.TH2F(f"ReadoutFlagsForced", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
        run_df.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)

        #filling the subhistogram
        nbinsy = hist.GetNbinsY()
        max_bins = 15
        n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
        for i in range(n_subhist):
            ybin_start = i * max_bins
            ybin_end = min((i+1) * max_bins, nbinsy)
            subhist = ROOT.TH2F(f"ReadoutFlagsForced_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start, ybin_start, ybin_end+1)
            for ix in range(len(run_list)):
                for iy in range(ybin_end-ybin_start):
                    subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))
            if n_subhist == 1:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, "ReadoutFlagsForced", "/eos/user/d/delvecch/www/PFG/")
            else:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"ReadoutFlagsForced_part{i+1}", "/eos/user/d/delvecch/www/PFG/")

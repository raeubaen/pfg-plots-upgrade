import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from Plugin import Plugin



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
                    EB_SM = next((key for key, fe in supermodules_FED.items() if fe == df_phi_eta["fed"].iloc[0]), None)
                    tt = df_phi_eta["tower"].iloc[0]
                    tcc = df_phi_eta["tcc"].iloc[0]
                    run_dict["tower"].append(f"{EB_SM} TCC{tcc} TT{tt}")
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
                        EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                        ccu = df_x_y_m["ccu"].iloc[0]
                        tcc = df_x_y_m["tcc"].iloc[0]
                        run_dict["tower"].append(f"{EEm_SM} TCC{tcc} CCU{ccu}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                            EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                            ccu = df_x_y_m["ccu"].iloc[0]
                            tcc = df_x_y_m["tcc"].iloc[0]
                            run_dict["tower"].append(f"{EEm_SM} TCC{tcc} CCU{ccu}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                                ccu = df_x_y_m["ccu"].iloc[0]
                                tcc = df_x_y_m["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEm_SM} TCC{tcc} CCU{ccu}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                                ccu = df_x_y_m["ccu"].iloc[0]
                                tcc = df_x_y_m["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEm_SM} TCC{tcc} CCU{ccu}")
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
                        EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                        ccu = df_x_y_p["ccu"].iloc[0]
                        tcc = df_x_y_p["tcc"].iloc[0]
                        run_dict["tower"].append(f"{EEp_SM} TCC{tcc} CCU{ccu}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                            EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                            ccu = df_x_y_p["ccu"].iloc[0]
                            tcc = df_x_y_p["tcc"].iloc[0]
                            run_dict["tower"].append(f"{EEp_SM} TCC{tcc} CCU{ccu}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                                ccu = df_x_y_p["ccu"].iloc[0]
                                tcc = df_x_y_p["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEp_SM} TCC{tcc} CCU{ccu}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                                ccu = df_x_y_p["ccu"].iloc[0]
                                tcc = df_x_y_p["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEp_SM} TCC{tcc} CCU{ccu}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


def df_to_hist(row, hist, tower_list, run_list):
    hist.Fill(run_list.index(row["run"])+1, tower_list.index(row["tower"])+1, row["value"])


def general_settings(n_contours, label_size = 0.06):
    ROOT.gStyle.SetNumberContours(n_contours)
    ROOT.gStyle.SetPalette(ROOT.kBeach)
    ROOT.gStyle.SetLabelSize(label_size)


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
    hist.GetXaxis().SetLabelSize(0.06)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetZaxis().SetLabelSize(0.06)
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


    #process single run, for both barrel and endcap
    def process_one_run(self, run_info):
        #dataframe with relative SM, TT and (eta, phi) for channels
        df = pd.read_csv("/eos/user/d/delvecch/www/PFG/ecalchannels.csv")
        #dictionary for match between the SM and FE
        supermodules_FED = {"EB-18": 627, "EB-17": 626, "EB-16": 625, "EB-15": 624, "EB-14": 623, "EB-13": 622, "EB-12": 621, "EB-11": 620,
        "EB-10": 619, "EB-09": 618, "EB-08": 617, "EB-07": 616, "EB-06": 615, "EB-05": 614, "EB-04": 613, "EB-03": 612, "EB-02": 611,
        "EB-01": 610, "EB+01": 628, "EB+02": 629, "EB+03": 630, "EB+04": 631, "EB+05": 632, "EB+06": 633, "EB+07": 634, "EB+08": 635,
        "EB+09": 636, "EB+10": 637, "EB+11": 638, "EB+12": 639, "EB+13": 640, "EB+14": 641, "EB+15": 642, "EB+16": 643, "EB+17": 644,
        "EB+18": 645, "EE-09": 603, "EE-08": 602, "EE-07": 601, "EE-06": 609, "EE-05": 608, "EE-04": 607, "EE-03": 606, "EE-02": 605, 
        "EE-01": 604, "EE+01": 649, "EE+02": 650, "EE+03": 651, "EE+04": 652, "EE+05": 653, "EE+06": 654, "EE+07": 646, "EE+08": 647, "EE+09": 648}
        #dictionary with single run info
        run_dict = {"tower": [], "value": []}

        #barrel single run
        self.folder = "EcalBarrel/EBSelectiveReadoutTask/"
        self.plot_name = "EBSRT readout unit with SR forced"
        self.serverurl_online = "online"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EB", df, supermodules_FED, run_dict)
        
        #endcap- single run
        self.folder = "EcalEndcap/EESelectiveReadoutTask/"
        self.plot_name = "EESRT readout unit with SR forced EE -"
        self.serverurl_online = "online"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE-", df, supermodules_FED, run_dict)

        #endcap+ single run
        self.folder = "EcalEndcap/EESelectiveReadoutTask/"
        self.plot_name = "EESRT readout unit with SR forced EE +"
        self.serverurl_online = "online"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE+", df, supermodules_FED, run_dict)

        print(run_dict)

        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)


    #history plot function
    def create_history_plots(self):
        general_settings(255, label_size = 0.06)
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
        #run_list = list(pd.unique(run_df.run))
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

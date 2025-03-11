import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd

from Plugin import Plugin
import ECAL



def read_hist_status(one_run_root_object_status, status_dict, detector, df, supermodules_FED):
    nbinsx = one_run_root_object_status.GetNbinsX()
    nbinsy = one_run_root_object_status.GetNbinsY()
    if detector == "EB":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object_status.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object_status.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object_status.GetYaxis().GetBinUpEdge(iy)
                    if y <= 0:
                        y -= 1
                    #print(f"(x, y) != 0: ({x}, {y})")
                    df_phi = df[df["iphi"] == x]
                    df_phi_eta = df_phi[df_phi["ieta"] == y]
                    #print(f"df_phi_eta:\n{df_phi_eta}")
                    info_dict = ECAL.fill_tcc_tt(df_phi_eta, supermodules_FED)
                    status_dict["det_SM"].append(f"{info_dict['SM_label']}")
                    status_dict["tcc"].append(info_dict['tcc'])
                    status_dict["tt_ccu"].append(info_dict['tt_ccu'])
                    #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} TT{info_dict['tt_ccu']}")
                    status_dict["x_phi"].append(x)
                    status_dict["y_eta"].append(y)
                    status_dict["status"].append(one_run_root_object_status.GetBinContent(ix, iy))
                    #print(f"{one_run_root_object_status.GetBinContent(ix, iy)}")
    if detector == "EE-":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object_status.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object_status.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object_status.GetYaxis().GetBinUpEdge(iy)
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    if df_x_y.empty:
                        continue
                    #print(f"(x, y) != 0: ({x}, {y})")
                    df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                    #print(f"df_x_y_m:\n{df_x_y_m}")
                    info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                    status_dict["det_SM"].append(f"{info_dict['SM_label']}")
                    status_dict["tcc"].append(info_dict['tcc'])
                    status_dict["tt_ccu"].append(info_dict['tt_ccu'])
                    #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                    status_dict["x_phi"].append(x)
                    status_dict["y_eta"].append(y)
                    status_dict["status"].append(one_run_root_object_status.GetBinContent(ix, iy))
                    #print(f"{one_run_root_object_status.GetBinContent(ix, iy)}")
    if detector == "EE+":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object_status.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object_status.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object_status.GetYaxis().GetBinUpEdge(iy)
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    if df_x_y.empty:
                        continue
                    #print(f"(x, y) != 0: ({x}, {y})")
                    df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE- fed
                    #print(f"df_x_y_p:\n{df_x_y_p}")
                    info_dict = ECAL.fill_tcc_tt(df_x_y_p, supermodules_FED, key=1)
                    status_dict["det_SM"].append(f"{info_dict['SM_label']}")
                    status_dict["tcc"].append(info_dict['tcc'])
                    status_dict["tt_ccu"].append(info_dict['tt_ccu'])
                    #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                    status_dict["x_phi"].append(x)
                    status_dict["y_eta"].append(y)
                    status_dict["status"].append(one_run_root_object_status.GetBinContent(ix, iy))
                    #print(f"{one_run_root_object_status.GetBinContent(ix, iy)}")


def read_hist(one_run_root_object, status_dict, detector, df, supermodules_FED, run_dict):
    status_df = pd.DataFrame(status_dict)
    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    if detector == "EB":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                    #print(f"(x, y) != 0: ({x}, {y})")
                    df_phi = df[df["iphi"] == x+1] #+1 because the low edge belongs to the previous SM
                    df_phi_eta = df_phi[df_phi["ieta"] == y+1] #+1 because the low edge belongs to the previous SM
                    info_dict = ECAL.fill_tcc_tt(df_phi_eta, supermodules_FED)
                    #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} TT{info_dict['tt_ccu']}")
                    status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                    #print(status_df_match)
                    if not status_df_match.empty:
                        run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} TT{info_dict['tt_ccu']}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
    if detector == "EE-":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                    #print(f"(x, y) != 0: ({x}, {y})")
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    #print(df_x_y)
                    if not df_x_y.empty:
                        df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                        info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                        #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                        status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                        #print(status_df_match)
                        if not status_df_match.empty:
                            run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        #print(f"(x, y) != 0: ({x}, {y})")
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        #print(df_x_y)
                        if not df_x_y.empty:
                            df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                            info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                            #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                            #print(status_df_match)
                            if not status_df_match.empty:
                                run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            #print(f"(x, y) != 0: ({x}, {y})")
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            #print(df_x_y)
                            if not df_x_y.empty:
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                                #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                #print(status_df_match)
                                if not status_df_match.empty:
                                    run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                #print(f"(x, y) != 0: ({x}, {y})")
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                #print(df_x_y)
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                                #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                #print(status_df_match)
                                if not status_df_match.empty:
                                    run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
    if detector == "EE+":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                    #print(f"(x, y) != 0: ({x}, {y})")
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    #print(df_x_y)
                    if not df_x_y.empty:
                        df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                        info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                        #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                        status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                        #print(status_df_match)
                        if not status_df_match.empty:
                            run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        #print(f"(x, y) != 0: ({x}, {y})")
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        #print(df_x_y)
                        if not df_x_y.empty:
                            df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                            info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                            #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                            #print(status_df_match)
                            if not status_df_match.empty:
                                run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            #print(f"(x, y) != 0: ({x}, {y})")
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            #print(df_x_y)
                            if not df_x_y.empty:
                                df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                                #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                #print(status_df_match)
                                if not status_df_match.empty:
                                    run_dict["tower"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                #print(f"(x, y) != 0: ({x}, {y})")
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                #print(df_x_y)
                                df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, key=1)
                                #print(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                status_df_match = status_df[(status_df["det_SM"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                #print(status_df_match)
                                if not status_df_match.empty:
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


class MLDQM(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")

    
    #process single run, for both barrel and endcap
    def process_one_run(self, run_info):
        #dataframe with relative SM, TT and (eta, phi) for channels
        df = pd.read_csv("/eos/user/d/delvecch/www/PFG/ecalchannels.csv")
        #dictionary for matching between the SM and FE
        supermodules_FED = ECAL.supermodules_FED_match
        #dictionary with single run status map
        status_dict = {"det_SM": [], "tcc": [], "tt_ccu": [], "x_phi": [], "y_eta": [], "status": []}
        #dictionary with single run info
        run_dict = {"tower": [], "value": []}

        #EB
        self.folder = "EcalBarrel/EBIntegrityClient/"
        self.plot_name = "EBIT channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EB", df, supermodules_FED)
        self.folder = "EcalBarrel/EBOccupancyTask/"
        self.plot_name = "EBOT ML bad tower count normalized"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, status_dict, "EB", df, supermodules_FED, run_dict)
        print(run_dict)

        #EE-
        self.folder = "EcalEndcap/EEIntegrityClient/"
        self.plot_name = "EEIT EE - channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EE-", df, supermodules_FED)
        self.folder = "EcalEndcap/EEOccupancyTask/"
        self.plot_name = "EEOT ML bad tower count normalized EE -"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, status_dict, "EE-", df, supermodules_FED, run_dict)
        print(run_dict)

        #EE+
        self.folder = "EcalEndcap/EEIntegrityClient/"
        self.plot_name = "EEIT EE + channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EE+", df, supermodules_FED)
        self.folder = "EcalEndcap/EEOccupancyTask/"
        self.plot_name = "EEOT ML bad tower count normalized EE +"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, status_dict, "EE+", df, supermodules_FED, run_dict)
        print(run_dict)


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
        print(run_dict)
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
        hist = ROOT.TH2F(f"MLDQM", "", len(run_list), 0., len(run_list)+1, len(tower_list), 0., len(tower_list)+1)
        run_df.apply(lambda row: df_to_hist(row, hist, tower_list, run_list), axis=1)

        #filling the subhistograms
        nbinsy = hist.GetNbinsY()
        max_bins = 15
        n_subhist = nbinsy // max_bins + (1 if nbinsy % max_bins > 0 else 0)
        for i in range(n_subhist):
            ybin_start = i * max_bins
            ybin_end = min((i+1) * max_bins, nbinsy)
            subhist = ROOT.TH2F(f"MLDQM_part{i+1}", "", len(run_list), 0., len(run_list)+1, ybin_end-ybin_start, ybin_start, ybin_end+1)
            for ix in range(len(run_list)):
                for iy in range(ybin_end-ybin_start):
                    subhist.SetBinContent(ix+1, iy+1, hist.GetBinContent(ix+1, ybin_start+iy+1))
            if n_subhist == 1:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, "MLDQM", "/eos/user/d/delvecch/www/PFG/")
            else:
                hist_config(run_list, tower_list, subhist, ybin_start, ybin_end, f"MLDQM_part{i+1}", "/eos/user/d/delvecch/www/PFG/")
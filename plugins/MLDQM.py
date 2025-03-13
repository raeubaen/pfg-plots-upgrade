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
                    df_phi = df[df["iphi"] == x]
                    df_phi_eta = df_phi[df_phi["ieta"] == y]
                    info_dict = ECAL.fill_tcc_tt(df_phi_eta, supermodules_FED)
                    status_dict["label"].append(f"{info_dict['SM_label']}")
                    status_dict["tcc"].append(info_dict['tcc'])
                    status_dict["tt_ccu"].append(info_dict['tt_ccu'])
                    status_dict["x_phi"].append(x)
                    status_dict["y_eta"].append(y)
                    status_dict["status"].append(one_run_root_object_status.GetBinContent(ix, iy))
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
                    df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                    info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                    status_dict["label"].append(f"{info_dict['SM_label']}")
                    status_dict["tcc"].append(info_dict['tcc'])
                    status_dict["tt_ccu"].append(info_dict['tt_ccu'])
                    status_dict["x_phi"].append(x)
                    status_dict["y_eta"].append(y)
                    status_dict["status"].append(one_run_root_object_status.GetBinContent(ix, iy))
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
                    df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE- fed
                    info_dict = ECAL.fill_tcc_tt(df_x_y_p, supermodules_FED, ccu=True)
                    status_dict["label"].append(f"{info_dict['SM_label']}")
                    status_dict["tcc"].append(info_dict['tcc'])
                    status_dict["tt_ccu"].append(info_dict['tt_ccu'])
                    status_dict["x_phi"].append(x)
                    status_dict["y_eta"].append(y)
                    status_dict["status"].append(one_run_root_object_status.GetBinContent(ix, iy))


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
                    df_phi = df[df["iphi"] == x+1]
                    df_phi_eta = df_phi[df_phi["ieta"] == y+1]
                    info_dict = ECAL.fill_tcc_tt(df_phi_eta, supermodules_FED)
                    status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                    if not status_df_match.empty:
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
                        info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                        status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                        if not status_df_match.empty:
                            run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                            info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                            status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                            if not status_df_match.empty:
                                run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                                status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                if not status_df_match.empty:
                                    run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                                status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                if not status_df_match.empty:
                                    run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
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
                        df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                        info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                        status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                        if not status_df_match.empty:
                            run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                            info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                            status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                            if not status_df_match.empty:
                                run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                                status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                if not status_df_match.empty:
                                    run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_m = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                info_dict = ECAL.fill_tcc_tt(df_x_y_m, supermodules_FED, ccu=True)
                                status_df_match = status_df[(status_df["label"] == info_dict["SM_label"]) & (status_df["tcc"] == info_dict["tcc"]) & (status_df["tt_ccu"] == info_dict["tt_ccu"]) & (status_df["status"] < 3)]
                                if not status_df_match.empty:
                                    run_dict["label"].append(f"{info_dict['SM_label']} TCC{info_dict['tcc']} CCU{info_dict['tt_ccu']}")
                                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


class MLDQM(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    def process_one_run(self, run_info):
        #load the file with all the info about the ECAL channels
        channels_df = pd.read_csv("/eos/user/d/delvecch/www/PFG/ecalchannels.csv")
        #info for matching the SM with fed number
        supermodules_FED = ECAL.supermodules_FED_match
        #dictionary with single run status map
        status_dict = {"label": [], "tcc": [], "tt_ccu": [], "x_phi": [], "y_eta": [], "status": []}
        #dictionary with single run info to fill with histogram data
        run_dict = {"label": [], "value": []}

        #EB status map
        self.folder = "EcalBarrel/EBIntegrityClient/"
        self.plot_name = "EBIT channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EB", channels_df, supermodules_FED)
        #EB MLDQM hist
        self.folder = "EcalBarrel/EBOccupancyTask/"
        self.plot_name = "EBOT ML bad tower count normalized"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, status_dict, "EB", channels_df, supermodules_FED, run_dict)

        #EE- status map
        self.folder = "EcalEndcap/EEIntegrityClient/"
        self.plot_name = "EEIT EE - channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EE-", channels_df, supermodules_FED)
        #EE- MLDQM hist
        self.folder = "EcalEndcap/EEOccupancyTask/"
        self.plot_name = "EEOT ML bad tower count normalized EE -"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, status_dict, "EE-", channels_df, supermodules_FED, run_dict)

        #EE+ status map
        self.folder = "EcalEndcap/EEIntegrityClient/"
        self.plot_name = "EEIT EE + channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EE+", channels_df, supermodules_FED)
        #EE+ MLDQM hist
        self.folder = "EcalEndcap/EEOccupancyTask/"
        self.plot_name = "EEOT ML bad tower count normalized EE +"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, status_dict, "EE+", channels_df, supermodules_FED, run_dict)


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
        run_df[["detector", "sm_num", "tcc_num", "tt_ccu", "tt_num"]] = run_df["label"].str.extract(r'(EB|EE)([+-]?\d+)\s+TCC(\d+)\s+(TT|CCU)(\d+)')
        run_df["sm_num"] = run_df["sm_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df["tcc_num"] = run_df["tcc_num"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df["tt_ccu_priority"] = run_df["tt_ccu"].map({"TT": 0, "CCU": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_num", "tcc_num", "tt_ccu_priority", "tt_num"]).drop(columns=["detector_priority",
        "sm_num", "tcc_num", "tt_ccu_priority", "tt_num", "detector", "tt_ccu"])

        #filling history plot
        self.fill_history_subplots(run_df, available_runs, "MLDQM", f"{save_path}")
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


class ChannelStatus(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")

    def get_status_dict(self, run_info):
        #load the file with all the info about the ECAL channels
        channels_df = pd.read_csv(self.ecal_channels_csv_path)
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

        #EE- status map
        self.folder = "EcalEndcap/EEIntegrityClient/"
        self.plot_name = "EEIT EE - channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EE-", channels_df, supermodules_FED)

        #EE+ status map
        self.folder = "EcalEndcap/EEIntegrityClient/"
        self.plot_name = "EEIT EE + channel status map"
        one_run_root_object_status = self.get_root_object(run_info)
        read_hist_status(one_run_root_object_status, status_dict, "EE+", channels_df, supermodules_FED)

        return status_dict

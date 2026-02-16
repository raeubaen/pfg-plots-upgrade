import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import pandas as pd
import numpy as np
from ch_to_tt import ch_to_tt

from Plugin import Plugin
import ECAL
from ChannelStatus import ChannelStatus


def read_hist_EB(one_run_root_object, supermodule, EBchannels, status_dict):
    status_df = pd.DataFrame(status_dict)

    nbinsx = one_run_root_object.GetNbinsX()
    nbinsy = one_run_root_object.GetNbinsY()
    sm = int(supermodule[2:])
    if sm < 0:
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                y = int(one_run_root_object.GetYaxis().GetBinUpEdge(iy))
                status_df_match = (status_df["y_eta"] == -x) & (status_df["x_phi"] == y) & (status_df["status"] >= 3)
                if status_df_match.any(): continue
                EBchannels["label"].append(f"{supermodule} [+{y}, -{x}]")
                EBchannels["value"].append(one_run_root_object.GetBinContent(ix, iy))

    elif sm > 0:
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                x = int(one_run_root_object.GetXaxis().GetBinUpEdge(ix))
                y = int(-one_run_root_object.GetYaxis().GetBinLowEdge(iy))
                status_df_match = (status_df["y_eta"] == x) & (status_df["x_phi"] == y) & (status_df["status"] >= 3)
                if status_df_match.any(): continue

                EBchannels["label"].append(f"{supermodule} [+{y}, -{x}]")
                EBchannels["value"].append(one_run_root_object.GetBinContent(ix, iy))



def getBadHV(available_runs, run_dict_temp, run_dict):


    for run in available_runs:
        data = run_dict_temp[run]
        if not data["label"]:
            continue

        df = pd.DataFrame({
            "label": data["label"],
            "value": data["value"]
        })

        # Only EB channels
        df = df[df["label"].str.contains("EB")]
        if df.empty:
            continue

        # Extract geometry
        df[["det", "sm", "iphi", "ieta"]] = df["label"].str.extract(
            r'(EB)([+-]?\d+)\s+\[([+-]?\d+),\s*([+-]?\d+)\]'
        )
        df["sm"] = df["sm"].astype(int)
        df["iphi"] = df["iphi"].astype(int)
        df["ieta"] = df["ieta"].astype(int)
        df["absieta"] = df["ieta"].abs()

        # HV block assignment (4 per LM region)
        df["eta_block"] = (df["absieta"] - 1) // 5
        df["phi_block"] = (df["iphi"] - 1) // 10
        df["hv_block"] = df["eta_block"].astype(str) + "_" + df["phi_block"].astype(str)

        # LM region assignment (9 per SM)
        mask_strip = df["absieta"] <= 5
        df["region"] = 0
        df.loc[~mask_strip, "region"] = (
            1 + ((df.loc[~mask_strip, "absieta"] - 6) // 20) * 2 + ((df.loc[~mask_strip, "iphi"] - 1) // 10)
        )

        # Remove zero-value channels
        df_nonzero = df[df["value"] != 0].copy()
        if df_nonzero.empty:
            continue

        # Process each region separately
        for (sm, region), df_region in df_nonzero.groupby(["sm", "region"]):

            # Compute mean per HV block inside the region
            hv_group = df_region.groupby("hv_block")["value"].median()
            hv_labels = df_region.groupby("hv_block")["label"].first().values  # pick representative label

            hv_values = hv_group.values
            N = len(hv_values)
            if N < 2:
                continue  # cannot do leave-one-out with <2 HV blocks

            # Full RMS of the HV blocks
            full_rms = np.sqrt(np.mean((hv_values - hv_values.mean())**2))

            # Leave-one-out RMS
            loo_rms = np.array([
                np.sqrt(np.mean((np.delete(hv_values, i) - np.delete(hv_values, i).mean())**2))
                for i in range(N)
            ])

            # Identify HV block whose exclusion reduces RMS the most
            reduction = full_rms - loo_rms
            bad_idx = np.argmax(reduction)

            print("candidate", hv_labels[bad_idx])
            # Only flag if reduction is significant

            # Compute mean of other HV blocks (leave-one-out mean)
            mean_others = np.mean(np.delete(hv_values, bad_idx))

            # Check RMS reduction and difference threshold
            diff_fraction = abs(hv_values[bad_idx] - mean_others) / mean_others


            # Compute RMS of all channels in the region excluding the candidate bad HV block
            bad_hv_block_label = hv_group.index[bad_idx]
            region_values_excl_bad = df_region[df_region["hv_block"] != bad_hv_block_label]["value"].values
            if len(region_values_excl_bad) < 2:
                continue  # not enough channels to compute RMS

            region_rms_excl_bad = np.sqrt(df_region[df_region["hv_block"] == bad_hv_block_label]["value"].values.std()**2 + np.mean((region_values_excl_bad - region_values_excl_bad.mean())**2))

            # Significance
            significance = abs(hv_values[bad_idx] - mean_others) / region_rms_excl_bad if region_rms_excl_bad > 0 else 0

            #print("significance: ", significance)

            candidate_eta_block = int(bad_hv_block_label.split("_")[0])

            # Select all channels in the same HV eta column across the full supermodule
            hv_channels_eta_df = df[df["sm"] == sm]
            hv_channels_eta_df = hv_channels_eta_df[hv_channels_eta_df["eta_block"] == candidate_eta_block]
            hv_channels_eta_df = hv_channels_eta_df[hv_channels_eta_df["phi_block"] != int(bad_hv_block_label.split("_")[1])]
            hv_channels_eta = hv_channels_eta_df["value"].values
            #print("same eta labels:    ",  hv_channels_eta_df["label"].values)
            #print("bad candidate mean: ", hv_values[bad_idx])
            # Remove zero channels
            hv_channels_eta = hv_channels_eta[hv_channels_eta != 0]

            #print("hv_channels same eta", hv_channels_eta)
            #print("hv_channels same eta.mean", hv_channels_eta.mean())

            if len(hv_channels_eta) < 5:
                significance_local = 6
            else:
                # RMS over all 50 channels in this HV column
                rms_eta = np.sqrt(df_region[df_region["hv_block"] == bad_hv_block_label]["value"].values.std()**2 + np.mean((hv_channels_eta - hv_channels_eta.mean())**2))
                print("hv_channels same eta.rms", rms_eta)
                # Local significance: candidate HV mean vs RMS of its 50 channels
                significance_local = abs(hv_values[bad_idx] - np.median(hv_channels_eta)) / rms_eta if rms_eta > 0 else 6

            print("significance local: ", significance_local)
            if reduction[bad_idx]/full_rms > 0.5 and diff_fraction >= 0.1 and significance > 2 and significance_local > 1:
                # Get all channels belonging to the bad HV block
                hv_block_channels = df[df["hv_block"] == bad_hv_block_label]
                hv_block_channels = hv_block_channels[hv_block_channels["sm"] == sm]

                print("hv_block_channels", hv_block_channels[["iphi", "ieta"]])
                # Convert each channel to its TT number using your function
                tt_numbers = hv_block_channels.apply(
                    lambda row: ch_to_tt(row["iphi"], row["ieta"]),
                    axis=1
                )

                # Keep only the unique TT numbers (there should be 2 per HV block)
                tt_numbers = tt_numbers.drop_duplicates().tolist()

                run_dict["label"].append(f"EB{sm}, HV@TTs{tt_numbers}")
                run_dict["value"].append(hv_values[bad_idx])
                run_dict["run"].append(run)
                print(f"{sm}, {tt_numbers}")
                print("BAD HV!!")

class APDoverPN(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")


    def process_one_run(self, run_info):
        run_dict = {"label": [], "value":[]}

        status_dict = ChannelStatus(self.buildopener).get_status_dict(run_info)

        #EB
        EBsupermodules_list = ECAL.EBsupermodules_list
        for i, EBsupermodule in enumerate(EBsupermodules_list):
            self.folder = "EcalBarrel/EBLaserTask/Laser3/"
            self.plot_name = f"EBLT amplitude over PN {EBsupermodule} L3"
            EBchannels = {"label": [], "value": []}
            one_run_root_object = self.get_root_object(run_info)
            read_hist_EB(one_run_root_object, EBsupermodule, EBchannels, status_dict)
            run_dict["label"].extend(EBchannels["label"])
            run_dict["value"].extend(EBchannels["value"])

        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict)

    def create_history_plots(self, save_path):
        self.color_scale_settings(255)
        available_runs = self.get_available_runs()
        run_dict_temp = {}
        for i, run in enumerate(available_runs):
            data_one_run = self.get_data_one_run(run)
            run_dict_temp[run] = data_one_run
        available_runs_filtered = run_dict_temp
        run_dict = {"label": [], "value": [], "run": []}
        getBadHV(available_runs_filtered, run_dict_temp, run_dict)

        #ordering
        run_df = pd.DataFrame(run_dict)
        if run_df.empty:
            print("Dataframe is empty, no info to plot")
            return
#        run_df[["detector", "sm_ch", "iphi_ix", "ieta_iy"]] = run_df["label"].str.extract(r'(EB|EE)([+-]?\d+)\s+\[([+-]?\d+),\s*([+-]?\d+)\]')
#        run_df["sm_ch"] = run_df["sm_ch"].astype(int)
#        run_df["iphi_ix"] = run_df["iphi_ix"].astype(int)
#        run_df["ieta_iy"] = run_df["ieta_iy"].astype(int)
#        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
#        run_df = run_df.sort_values(by=["detector_priority", "sm_ch", "iphi_ix", "ieta_iy"]).drop(columns=["detector_priority",
#        "detector", "sm_ch", "iphi_ix", "ieta_iy"])
        df_EB = run_df.loc[run_df["label"].str.contains("EB", case=False)]

        #fillingEB history plot
        self.fill_history_subplots(df_EB, available_runs, f"HV-flagged_APDoverPN_EB", f"{save_path}", change_hist_limits=True)

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
                    print(f"Found not empty bin: ({x}, {y})")
                    df_phi = df[df["iphi"] == x+1] #+1 because the low edge belongs to the previous SM
                    df_phi_eta = df_phi[df_phi["ieta"] == y+1] #+1 because the low edge belongs to the previous SM
                    print(f"{df_phi_eta}")
                    EB_SM = next((key for key, fe in supermodules_FED.items() if fe == df_phi_eta["fed"].iloc[0]), None)
                    tt = df_phi_eta["tower"].iloc[0]
                    ccu = df_phi_eta["ccu"].iloc[0]
                    tcc = df_phi_eta["tcc"].iloc[0]
                    print(f"{EB_SM} TCC{tcc} TT{tt} CCU{ccu}")
                    print(f"{one_run_root_object.GetBinContent(ix, iy)}")
                    run_dict["tower"].append(f"{EB_SM} TCC{tcc} TT{tt} CCU{ccu}")
                    run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
    if detector == "EE-":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                    print(f"Found not empty bin: ({x}, {y})")
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    print(f"{df_x_y}")
                    if not df_x_y.empty:
                        df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                        EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                        tt = df_x_y_m["tower"].iloc[0]
                        ccu = df_x_y_m["ccu"].iloc[0]
                        tcc = df_x_y_m["tcc"].iloc[0]
                        print(f"{EEm_SM} TCC{tcc} TT{tt} CCU{ccu}")
                        print(f"{one_run_root_object.GetBinContent(ix, iy)}")
                        run_dict["tower"].append(f"{EEm_SM} TCC{tcc} TT{tt} CCU{ccu}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        print(f"empty bin found")
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                            EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                            tt = df_x_y_m["tower"].iloc[0]
                            tcc = df_x_y_m["tcc"].iloc[0]
                            run_dict["tower"].append(f"{EEm_SM} TCC{tcc} TT{tt}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                                tt = df_x_y_m["tower"].iloc[0]
                                tcc = df_x_y_m["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEm_SM} TCC{tcc} TT{tt}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_m = df_x_y[df_x_y["fed"] <= 609] #choose the EE- fed
                                EEm_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_m["fed"].iloc[0]), None)
                                tt = df_x_y_m["tower"].iloc[0]
                                tcc = df_x_y_m["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEm_SM} TCC{tcc} TT{tt}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
    if detector == "EE+":
        for iy in range(1, nbinsy+1):
            for ix in range(1, nbinsx+1):
                if one_run_root_object.GetBinContent(ix, iy) != 0:
                    x = one_run_root_object.GetXaxis().GetBinUpEdge(ix)
                    y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                    print(f"Found not empty bin: ({x}, {y})")
                    df_x = df[df["ix"] == x]
                    df_x_y = df_x[df_x["iy"] == y]
                    print(f"{df_x_y}")
                    if not df_x_y.empty:
                        df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                        EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                        tt = df_x_y_p["tower"].iloc[0]
                        ccu = df_x_y_p["ccu"].iloc[0]
                        tcc = df_x_y_p["tcc"].iloc[0]
                        print(f"{EEp_SM} TCC{tcc} TT{tt} CCU{ccu}")
                        print(f"{one_run_root_object.GetBinContent(ix, iy)}")
                        run_dict["tower"].append(f"{EEp_SM} TCC{tcc} TT{tt} CCU{ccu}")
                        run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                    else:
                        print(f"empty bin found")
                        y = one_run_root_object.GetYaxis().GetBinLowEdge(iy)
                        df_x = df[df["ix"] == x]
                        df_x_y = df_x[df_x["iy"] == y+1]
                        if not df_x_y.empty:
                            df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                            EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                            tt = df_x_y_p["tower"].iloc[0]
                            tcc = df_x_y_p["tcc"].iloc[0]
                            run_dict["tower"].append(f"{EEp_SM} TCC{tcc} TT{tt}")
                            run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                        else:
                            x = one_run_root_object.GetXaxis().GetBinLowEdge(ix)
                            df_x = df[df["ix"] == x+1]
                            df_x_y = df_x[df_x["iy"] == y+1]
                            if not df_x_y.empty:
                                df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                                tt = df_x_y_p["tower"].iloc[0]
                                tcc = df_x_y_p["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEp_SM} TCC{tcc} TT{tt}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))
                            else:
                                y = one_run_root_object.GetYaxis().GetBinUpEdge(iy)
                                df_x = df[df["ix"] == x+1]
                                df_x_y = df_x[df_x["iy"] == y]
                                df_x_y_p = df_x_y[df_x_y["fed"] >= 646] #choose the EE+ fed
                                EEp_SM = next((key for key, fe in supermodules_FED.items() if fe == df_x_y_p["fed"].iloc[0]), None)
                                tt = df_x_y_p["tower"].iloc[0]
                                tcc = df_x_y_p["tcc"].iloc[0]
                                run_dict["tower"].append(f"{EEp_SM} TCC{tcc} TT{tt}")
                                run_dict["value"].append(one_run_root_object.GetBinContent(ix, iy))


class TTF4Occupancy(Plugin):
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

        #EB
        self.folder = "EcalBarrel/EBTriggerTowerTask/"
        self.plot_name = "EBTTT TTF4 Occupancy"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EB", df, supermodules_FED, run_dict)
        
        #EE-
        self.folder = "EcalEndcap/EETriggerTowerTask/"
        self.plot_name = "EETTT TTF4 Occupancy EE -"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE-", df, supermodules_FED, run_dict)

        #EE+
        self.folder = "EcalEndcap/EETriggerTowerTask/"
        self.plot_name = "EETTT TTF4 Occupancy EE +"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, "EE+", df, supermodules_FED, run_dict)

        #unique pairs of tower and value
        unique_pairs = list(set(zip(run_dict["tower"], run_dict["value"])))
        run_dict_unique = {"tower": [pair[0] for pair in unique_pairs], "value": [pair[1] for pair in unique_pairs]}
        print(run_dict_unique)

        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, run_dict_unique)


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
        run_df[["detector", "sm_num", "tcc_num", "tt_num", "ccu_num"]] = run_df["tower"].str.extract(r'(EB|EE)([+-]?\d+)\s+TCC(\d+)\s+TT(\d+)\s+CCU(\d+)')
        run_df["sm_num"] = run_df["sm_num"].astype(int)
        run_df["tt_num"] = run_df["tt_num"].astype(int)
        run_df["ccu_num"] = run_df["ccu_num"].astype(int)
        run_df["tcc_num"] = run_df["tcc_num"].astype(int)
        run_df["detector_priority"] = run_df["detector"].map({"EB": 0, "EE": 1})
        run_df = run_df.sort_values(by=["detector_priority", "sm_num", "tcc_num", "tt_num", "ccu_num"]).drop(columns=["detector_priority",
        "sm_num", "tcc_num", "tt_num", "ccu_num", "detector"])
        print(run_df)
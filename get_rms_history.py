import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import argparse
import importlib
import json
import pandas as pd
import traceback
from pathlib import Path
from json_handler import x509_params, dqm_get_json
from cert_opener import X509CertAuth, X509CertOpen

import numpy as np

#from a csv file to a dict
def read_csv(file_path):
    df = pd.read_csv(file_path)
    data_list = df.to_dict(orient="records")
    return data_list


#read the plugins
def load_plugins(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
    return data.get("Plugins", [])


def main():
    ROOT.gROOT.SetBatch(True)

    #set the certificate and the key needed
    X509CertAuth.ssl_key_file, X509CertAuth.ssl_cert_file = x509_params()
    buildopener = urllib.request.build_opener(X509CertOpen())
    print(buildopener)

    #create parser to read arguments from command line
    parser = argparse.ArgumentParser(description="csv file to get run and dataset information")
    parser.add_argument('runlist_csvfile_path', type=str, help="Path to the runlist file")
    parser.add_argument('plot_folder', type=str, help="Path to save plots")
    parser.add_argument('ch_list', type=str, help="ch list: [{'x_phi': 0, 'y_eta': 0, 'SM': 'EB+0'},{'x_phi': 0, 'y_eta': 0, 'SM': 'EB+0'}]")
    args = parser.parse_args()

    '''
    #read the csv input file and convert into a list of dict: [{"run": 294295, "dataset": "blablabla"}, {...}, ...]
    runlist = read_csv(args.runlist_csvfile_path)
    if runlist is None:
        print("Error in reading the runlist file\nExiting from the execution of the program")

    #read the plugins
    plugins = ["RMSHistory_nocuts"]
    print(f"List of plugins: {plugins}")

    #plugins directory path
    plugins_dir = Path(__file__).parent / "plugins"
    sys.path.append(str(plugins_dir))

    #loop over plugins
    for plugin in plugins:
        print(f"Caricamento del plugin: {plugin}")
        mod = importlib.import_module(f"{plugin}")
        instance = getattr(mod, f"{plugin}")(buildopener, eval(args.ch_list))
        #loop over runs
        for item in runlist:
            run = item["run"]
            dataset = item["dataset"]
            print(f"Run number: {run}")
            #instantiate the plugins class
            try:
              instance.process_one_run(item)
            except Exception:
              print(f"Failed to process: {run} {dataset} {plugin}")
              print(traceback.format_exc())
        #create the history plot
        instance.create_history_plots(args.plot_folder)
        print("\n")
     '''
    ROOT.gROOT.LoadMacro("root_logon.C")

    df = pd.read_csv(f"{args.plot_folder}/EB_RMSHistory.csv")
    ch_list_evalled = eval(args.ch_list)
    for ch in ch_list_evalled:
      current_df = df[(df.sm_ch == int(ch["SM"].replace("EB", "").replace("EE",""))) & (df.iphi_ix == ch["x_phi"]) & (df.ieta_iy == ch["y_eta"])]
      rms_array = current_df.value.to_numpy().astype(float)
      run_array = current_df.run.to_numpy().astype(float)
      min_run_thousands = int(np.min(run_array // 1000) * 1000)
      g = ROOT.TGraph(len(rms_array), run_array - min_run_thousands, rms_array)
      g.Sort()

      x_min = ROOT.TMath.MinElement(g.GetN(), g.GetX())
      x_max = ROOT.TMath.MaxElement(g.GetN(), g.GetX())
      y_min = ROOT.TMath.MinElement(g.GetN(), g.GetY())
      y_max = ROOT.TMath.MaxElement(g.GetN(), g.GetY())

      # Add some margin
      x_pad = 0.05 * (x_max - x_min)
      y_pad = 0.1 * (y_max - y_min)

      # Create an empty histogram with a title
      ch_string = f"{ch['SM']}_{'iPhi' if 'EB' in ch['SM'] else 'x'}={ch['x_phi']}_{'iEta' if 'EB' in ch['SM'] else 'y'}{ch['y_eta']}"
      frame = ROOT.TH1F("frame", ch_string,
                        1, x_min - x_pad, x_max + x_pad)
      frame.SetMinimum(y_min - y_pad)
      frame.SetMaximum(y_max + y_pad)

      # Create canvas and draw the frame
      c = ROOT.TCanvas()
      frame.Draw()

      # Draw the graph on top
      g.Draw("PL SAME")  # or "ALP SAME" depending on your style
      frame.GetYaxis().SetTitle("RMS (DQM coll. runs) [ADC counts]")
      frame.GetXaxis().SetTitle(f"#Run - {min_run_thousands}")

      current_max = frame.GetMaximum()
      frame.GetYaxis().SetRangeUser(0.1, current_max)
      c.SaveAs(f"{args.plot_folder}/{ch_string}.pdf")
      c.SaveAs(f"{args.plot_folder}/{ch_string}.png")
      c.SaveAs(f"{args.plot_folder}/{ch_string}.root")

if __name__ == "__main__":
    main()

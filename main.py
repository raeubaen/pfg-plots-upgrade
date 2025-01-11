import os, sys, urllib.request, urllib.error, urllib.parse, http.client, json
import array
import ROOT
import argparse
import importlib
import json
import pandas as pd

from json_handler import x509_params, dqm_get_json
from cert_opener import X509CertAuth, X509CertOpen


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
    #set the certificate and the key needed
    X509CertAuth.ssl_key_file, X509CertAuth.ssl_cert_file = x509_params()
    buildopener = urllib.request.build_opener(X509CertOpen())

    #create parser to read arguments from command line
    parser = argparse.ArgumentParser(description="csv file to get run and dataset information")
    parser.add_argument('runlist_csvfile_path', type=str, help="Path to the runlist file")
    args = parser.parse_args()
    
    #read the csv input file and convert into a list of dict: [{"run": 294295, "dataset": "blablabla"}, {...}, ...]
    runlist = read_csv(args.runlist_csvfile_path)

    #read the plugins
    plugins = load_plugins("./conf.json")
    print(plugins)

    #instantiate the plugins class
    for plugin in plugins:
        print(f"Caricamento del plugin: {plugin}")
        mod = importlib.import_module(f"{plugin}")
        instance = getattr(mod, f"{plugin}")(buildopener)
        #print(instance)
        for item in runlist:
            run = item["run"]
            dataset = item["dataset"]
            print(f"Run number: {run}")
            instance.process_one_run(item)
            print("\n\n")

            
if __name__ == "__main__":
    main()

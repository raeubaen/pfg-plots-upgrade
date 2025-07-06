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


def main():

    #set the certificate and the key needed
    X509CertAuth.ssl_key_file, X509CertAuth.ssl_cert_file = x509_params()
    buildopener = urllib.request.build_opener(X509CertOpen())

    #create parser to read arguments from command line
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('run', type=int, help="run")
    args = parser.parse_args()

    plugins_dir = Path(__file__).parent / "plugins"
    sys.path.append(str(plugins_dir))
    from ChannelStatus import ChannelStatus


    status_plugin_instance = ChannelStatus(buildopener)

    status_dict = status_plugin_instance.get_status_dict({"run": args.run, "dataset": "/Global/Online/ALL/"})

    df = pd.DataFrame(status_dict)
    outfile = f"ch_status_{args.run}.csv"
    print(f"output in {outfile}")
    df.to_csv(outfile, index=None)

if __name__ == "__main__":
    main()

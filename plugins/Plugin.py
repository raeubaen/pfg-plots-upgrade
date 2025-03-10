import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json
import cppyy

from json_handler import dqm_get_json



class Plugin:
    def __init__(self, buildopener, folder=None, plot_name=None):
        self._data = {}
        self.buildopener = buildopener
        self.folder = folder  #given in the specific class
        self.plot_name = plot_name  #given in the specific class
        self.serverurl_online = " " #given in the specific class
        

    #take the json from the DQM and converting into a root object
    def get_root_object(self, run_info):
        json_str = dqm_get_json(self.buildopener, run_info["run"], run_info["dataset"], self.folder, self.plot_name)
        try:
            return ROOT.TBufferJSON.ConvertFromJSON(str(json_str))
        except cppyy.gbl.nlohmann.detail.out_of_range:
            json_object = json.loads(json_str)
            json_object["fZmax"] = 1e+10
            json_object["fZmin"] = 0
            return ROOT.TBufferJSON.ConvertFromJSON(json.dumps(json_object))

    
    #fill the _data dict with the one run data
    def fill_data_one_run(self, run_info, one_run_data):
        self._data[run_info["run"]] = one_run_data

        
    #get the one run data giving the run number
    def get_data_one_run(self, run):
        return self._data[run]

    
    #list of all the available runs
    def get_available_runs(self):
        return self._data.keys()
import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json

from Plugin import Plugin



def read_hist(one_run_root_object, run_number, fit_result, detector):
    #first fit
    range_min = -10
    range_max = 10
    gauss_ini = ROOT.TF1("gauss_ini", "gaus", -10, 10)
    gauss_ini.SetParameter(1, 0)
    gauss_ini.SetParameter(2, 1)
    one_run_root_object.Fit(gauss_ini, "R")
    #second fit
    mean_ini = gauss_ini.GetParameter(1)
    sigma_ini = gauss_ini.GetParameter(2)
    range_min = mean_ini - 3*sigma_ini
    range_max = mean_ini + 3*sigma_ini
    gauss = ROOT.TF1("gauss", "gaus", range_min, range_max)
    gauss.SetParameter(0, gauss_ini.GetParameter(0))
    gauss.SetParameter(1, gauss_ini.GetParameter(1))
    gauss.SetParameter(2, gauss_ini.GetParameter(2))
    one_run_root_object.Fit(gauss, "R")
    mean = gauss.GetParameter(1)
    mean_err = gauss.GetParError(1)
    fit_result[f"{detector}"] = {"mean": mean, "mean_error": mean_err}


def hist_config(graph, available_runs, detector, save_path):
    #canva settings
    c = ROOT.TCanvas(f"c_{detector}", "", 5120, 2880)
    c.SetGrid()
    c.SetLeftMargin(0.1)
    c.SetBottomMargin(0.25)
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(4)
    graph.SetMarkerColor(ROOT.kBlue)  
    graph.SetLineColor(ROOT.kBlue)  
    graph.SetLineWidth(2)
    graph.Draw("ALP")
    #modify the x_axis
    x_axis = graph.GetXaxis()
    x_axis.SetLimits(-1, len(available_runs))
    x_axis.SetLabelOffset(0.06)
    x_axis.SetNdivisions(len(available_runs) + 1, False)
    x_axis.ChangeLabel(1, -1, 0)
    x_axis.ChangeLabel(len(available_runs) + 2, -1, 0)
    for i, run in enumerate(available_runs):
        x_axis.ChangeLabel(i + 2, 90, -1, -1, -1, -1, str(run))
    x_axis_title = ROOT.TLatex()
    x_axis_title.SetTextSize(0.06)
    x_axis_title.SetTextFont(42)
    x_axis_title.DrawLatex(9.6, -3.7, "#bf{run}")
    #modify the y_axis
    y_axis = graph.GetYaxis()
    y_axis.SetTitle("mean [ns]")
    miny = ROOT.TMath.MinElement(graph.GetN(),graph.GetY())
    maxy = ROOT.TMath.MaxElement(graph.GetN(),graph.GetY())
    y_axis.SetLimits(miny-0.5, maxy+0.5)
    graph.SetMinimum(miny-0.5)
    graph.SetMaximum(maxy+0.5)
    y_axis.SetTitleOffset(0.7)
    #saving
    c.Modified()
    c.Update()
    c.SaveAs(f"{save_path}Timing_mean_{detector}.pdf")
    c.SaveAs(f"{save_path}Timing_mean_{detector}.png")
    c.SaveAs(f"{save_path}Timing_mean_{detector}.root")


class Timing(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="", plot_name="")

        
    #process single run to extract the mean  
    def process_one_run(self, run_info):
        #take the root object from the json
        run_number = run_info["run"]
        fit_result = {"EB": {}, "EE-": {}, "EE+": {}}
        
        #EB
        self.folder = "EcalBarrel/EBSummaryClient/"
        self.plot_name = "EBTMT timing mean 1D summary"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, run_number, fit_result, "EB")
        
        #EE-
        self.folder = "EcalEndcap/EESummaryClient/"
        self.plot_name = "EETMT EE - timing mean 1D summary"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, run_number, fit_result, "EE-")

        #EE+
        self.folder = "EcalEndcap/EESummaryClient/"
        self.plot_name = "EETMT EE + timing mean 1D summary"
        one_run_root_object = self.get_root_object(run_info)
        read_hist(one_run_root_object, run_number, fit_result, "EE+")

        #fill _data inside generic Plugin class
        self.fill_data_one_run(run_info, fit_result)
        
    
    #history plot function
    def create_history_plots(self, save_path):
        ROOT.gROOT.LoadMacro("rootlogon1.C")
        graph_EB = ROOT.TGraphErrors()
        graph_EEm = ROOT.TGraphErrors()
        graph_EEp = ROOT.TGraphErrors()
        available_runs = self.get_available_runs()
        for i, run in enumerate(available_runs):
            one_run_data = self.get_data_one_run(run)
            graph_EB.SetPoint(i, i, one_run_data["EB"]["mean"])
            graph_EB.SetPointError(i, 0, one_run_data["EB"]["mean_error"])
            graph_EEm.SetPoint(i, i, one_run_data["EE-"]["mean"])
            graph_EEm.SetPointError(i, 0, one_run_data["EE-"]["mean_error"])
            graph_EEp.SetPoint(i, i, one_run_data["EE+"]["mean"])
            graph_EEp.SetPointError(i, 0, one_run_data["EE+"]["mean_error"])
        hist_config(graph_EB, available_runs, "EB", f"{save_path}")
        hist_config(graph_EEm, available_runs, "EEm", f"{save_path}")
        hist_config(graph_EEp, available_runs, "EEp", f"{save_path}")

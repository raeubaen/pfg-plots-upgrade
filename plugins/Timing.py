import os, sys, urllib.request, urllib.error, urllib.parse, http.client
import ROOT
import json

from Plugin import Plugin



class Timing(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="EcalBarrel/EBSummaryClient/", plot_name="EBTMT timing mean 1D summary")

        
    #process single run to extract the mean and fill the _data dict  
    def process_one_run(self, run_info):
        #take the root object from the json
        one_run_root_object = self.get_root_object(run_info)
        run_number = run_info["run"]
        
        #fit function and parameters for the first fit
        xmin = one_run_root_object.GetXaxis().GetXmin()
        xmax = one_run_root_object.GetXaxis().GetXmax()
        gauss_ini = ROOT.TF1("gauss_ini", "gaus", -10, 10)
        gauss_ini.SetParameter(1, 0)
        gauss_ini.SetParameter(2, 1)
        one_run_root_object.Fit(gauss_ini, "R")

        #fit function and parameters for the second fit
        mean_ini = gauss_ini.GetParameter(1)
        sigma_ini = gauss_ini.GetParameter(2)
        range_min = mean_ini - 3*sigma_ini
        range_max = mean_ini + 3*sigma_ini
        gauss = ROOT.TF1("gauss", "gaus", range_min, range_max)
        gauss.SetParameter(0, gauss_ini.GetParameter(0))
        gauss.SetParameter(1, gauss_ini.GetParameter(1))
        gauss.SetParameter(2, gauss_ini.GetParameter(2))
        #gauss.SetRange()
        one_run_root_object.Fit(gauss, "R")

        #plot of the histogram with the fitting function
        c = ROOT.TCanvas("c", "", 800, 600)
        c.cd()
        one_run_root_object.Draw()
        gauss.SetLineColor(ROOT.kRed)
        gauss.Draw("SAME")
        c.SaveAs(f"/eos/user/d/delvecch/www/PFG/timing_run{run_number}.pdf")

        #fill the _data inside generic Plugin class with the mean
        mean = gauss.GetParameter(1)
        mean_err = gauss.GetParError(1)
        fit_result = {"mean": mean, "mean_error": mean_err}
        self.fill_data_one_run(run_info, fit_result)
        
    
    #history plot function
    def create_history_plots(self):
        ROOT.gROOT.LoadMacro("rootlogon1.C")
        #plot graphics
        graph = ROOT.TGraphErrors()
        available_runs = self.get_available_runs()
        for i, run in enumerate(available_runs):
            one_run_data = self.get_data_one_run(run)
            mean = one_run_data["mean"]
            mean_error = one_run_data["mean_error"]
            graph.SetPoint(i, i, one_run_data["mean"])
            graph.SetPointError(i, 0, one_run_data["mean_error"])
            print(f"Run {run}: {mean} +/- {mean_error}")

        #plot of the graph
        c = ROOT.TCanvas("c", "", 5120, 2880)
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
        y_axis.SetLimits(-3, 3)
        graph.SetMinimum(-3)
        graph.SetMaximum(3)
        y_axis.SetTitleOffset(0.7)

        #saving
        c.Modified()
        c.Update()
        c.SaveAs(f"/eos/user/d/delvecch/www/PFG/Timing_mean_EB.pdf")

import os, sys, urllib.request, urllib.error, urllib.parse, http.client, json
import array
import ROOT
#from ROOT import RooFit, RooRealVar, RooDataHist, RooGaussian

from Plugin import Plugin


class Timing(Plugin):
    def __init__(self, buildopener):
        Plugin.__init__(self, buildopener, folder="EcalBarrel/EBSummaryClient/", plot_name="EBTMT timing mean 1D summary")

        
    #process single run to extract the mean and fill the _data dict  
    def process_one_run(self, run_info):
        one_run_root_object = self.get_root_object(run_info)
        run_number = run_info["run"]
        
        #gaussian fit to extract the mean
        xmin = one_run_root_object.GetXaxis().GetXmin()
        print(f"x min: {xmin}")
        xmax = one_run_root_object.GetXaxis().GetXmax()
        print(f"x max: {xmax}")
        x = ROOT.RooRealVar("x", "x", xmin, xmax)
        one_run_data = ROOT.RooDataHist("one_run_data", "timing dataset one run", x, one_run_root_object)
        one_run_mean = ROOT.RooRealVar("one_run_mean", "Mean", 0, xmin, xmax)  
        one_run_sigma = ROOT.RooRealVar("one_run_sigma", "Sigma", 1, 0.01, 5)
        gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, one_run_mean, one_run_sigma)
        #x.setRange("fitRange", -25, 25)
        gauss.fitTo(one_run_data, ROOT.RooFit.Range(""))

        #print fit values
        print(f"Mean: {one_run_mean.getVal()} +/-  {one_run_mean.getError()}")
        print(f"Sigma: {one_run_sigma.getVal()} +/- {one_run_sigma.getError()}")
        
        #create frame
        frame = x.frame()
        frame.SetTitle(" ")
        frame.SetXTitle("time")
        frame.SetYTitle("Events")
        frame.GetXaxis().SetTitleOffset(0.9)
        frame.GetYaxis().SetTitleOffset(0.8)
        frame.GetXaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetTitleSize(0.05)
                
        #plot on frame
        one_run_data.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kBlack), ROOT.RooFit.LineWidth(1), ROOT.RooFit.MarkerColor(ROOT.kBlack), ROOT.RooFit.MarkerStyle(20), ROOT.RooFit.MarkerSize(4))
        gauss.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.Range(xmin, xmax))
        c = ROOT.TCanvas("c", "", 5120, 2880)
        c.SetLeftMargin(0.09)
        c.SetBottomMargin(0.12)
        frame.Draw("")
        c.SaveAs(f"/eos/user/d/delvecch/www/PFG/histogram_{run_number}.pdf") 
        print(f"histogram saved in: /eos/user/d/delvecch/www/PFG/histogram_{run_number}.pdf")

        #integral of the gauss fit
        integral_full_range = gauss.createIntegral(x, ROOT.RooFit.Range(xmin, xmax))
        area_full_range = integral_full_range.getVal()
        print(f"Area sotto la curva (range completo): {area_full_range}")
        
        #chi^2
        #chi2 = frame.chiSquare()
        #print(f"{chi2}")
        
        """
        #using ROOT and not RooFit
        xmin = one_run_root_object.GetXaxis().GetXmin()
        xmax = one_run_root_object.GetXaxis().GetXmax()
        gauss = ROOT.TF1("gauss", "gaus", xmin, xmax)
        gauss.SetParameter(1, 0)
        gauss.SetParameter(2, 1)
        one_run_root_object.Fit(gauss, "R")
        #mean = gauss.GetParameter(1)
        #mean_error = gauss.GetParError(1)
        #print(f"mean: {mean} +/- {mean.error}")
        print("DEBUG ------- fine del fit, apro la canva")
        c = ROOT.TCanvas("c", "", 800, 600)
        c.cd()
        one_run_root_object.Draw()
        gauss.SetLineColor(ROOT.kRed)
        gauss.Draw("SAME")
        c.SaveAs(f"/eos/user/d/delvecch/www/PFG/histogram_{run_number}.pdf")
        print("histogram saved in:\ /eos/user/d/delvecch/www/PFG/histogram_{run_number}.pdf")
        """

        #fill the _data inside generic Plugin class with the mean
        self.fill_data_one_run(run_info, one_run_mean.getVal())
        #print(self._data[run_info["run"]])

        
    #create the final plot after processing all the runs  
    def create_history_plots(self):
        #creo la canva e imposto la grafica del plot
        for run in self.get_available_run():
            one_run_data = self.get_one_run_data(run)
            #riempio l'istogramma
        #salvo il plot

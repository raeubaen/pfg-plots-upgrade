"""
        #using RooFit
        xmin = one_run_root_object.GetXaxis().GetXmin()
        print(f"x min: {xmin}")
        xmax = one_run_root_object.GetXaxis().GetXmax()
        print(f"x max: {xmax}")
        
        #first gaussian fit to extract the subrange of the second fit
        x = ROOT.RooRealVar("x", "x", xmin, xmax)
        one_run_data = ROOT.RooDataHist("one_run_data", "timing dataset one run", x, one_run_root_object)
        one_run_mean_ini = ROOT.RooRealVar("one_run_mean_ini", "Mean", 0, xmin, xmax)  
        one_run_sigma_ini = ROOT.RooRealVar("one_run_sigma_ini", "Sigma", 1, 0.01, 5)
        gauss_ini = ROOT.RooGaussian("gauss_ini", "Gaussian PDF", x, one_run_mean_ini, one_run_sigma_ini)
        #x.setRange("fitRange", -25, 25)
        gauss_ini.fitTo(one_run_data, ROOT.RooFit.Range(""))

        #first fit values
        print(f"First fit parameters")
        print(f"Mean: {one_run_mean_ini.getVal()} +/-  {one_run_mean_ini.getError()}")
        print(f"Sigma: {one_run_sigma_ini.getVal()} +/- {one_run_sigma_ini.getError()}")

        
        #second gaussian fit to extract the mean and mean_error
        one_run_mean_fin = ROOT.RooRealVar("one_run_mean_fin", "Mean", one_run_mean_ini.getVal(), one_run_mean_ini.getVal() - 3*one_run_sigma_ini.getVal(), one_run_mean_ini.getVal() + 3*one_run_sigma_ini.getVal())
        one_run_sigma_fin = ROOT.RooRealVar("one_run_sigma_fin", "Sigma", one_run_sigma_ini.getVal(), 0.01, 5)
        gauss_fin = ROOT.RooGaussian("gauss_fin", "Gaussian PDF", x, one_run_mean_fin, one_run_sigma_fin)
        x.setRange("fitRange", -3*one_run_sigma_ini.getVal(), 3*one_run_sigma_ini.getVal())
        gauss_fin.fitTo(one_run_data, ROOT.RooFit.Range("fitRange"))
        
        #second fit values
        print(f"Second fit parameters")
        print(f"Mean: {one_run_mean_fin.getVal()} +/-  {one_run_mean_fin.getError()}")
        print(f"Sigma: {one_run_sigma_fin.getVal()} +/- {one_run_sigma_fin.getError()}")
    
        
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
        gauss_ini.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.Range(""))
        c = ROOT.TCanvas("c", "", 5120, 2880)
        c.SetLeftMargin(0.09)
        c.SetBottomMargin(0.12)
        frame.Draw("")
        c.SaveAs(f"/eos/user/d/delvecch/www/PFG/histogram_{run_number}.pdf")
        #c.SaveAs(f"/eos/user/d/delvecch/www/PFG/histogram_{run_number}.root")
        print(f"histogram saved in: /eos/user/d/delvecch/www/PFG/histogram_{run_number}.pdf")

        #chi^2
        #chi2 = frame.chiSquare()
        #print(f"chi2 = {chi2}")
        """

import ROOT
import numpy as np


def main():
    np.random.seed(42)
    data = np.random.normal(loc = 0, scale = 1, size = 100000)
    
    x = ROOT.RooRealVar("x", "x", -5, 5)
    dataset = ROOT.RooDataSet("data", "dataset with x", ROOT.RooArgSet(x))

    for value in data:
        if -5 <= value <= 5:
            x.setVal(value)
            dataset.add(ROOT.RooArgSet(x))

    mean = ROOT.RooRealVar("mean", "mean of gaussian", 0, -10, 10)
    sigma = ROOT.RooRealVar("sigma", "sigma of gaussian", 1, 0.1, 5)
    gauss = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)

    result = gauss.fitTo(dataset, ROOT.RooFit.Save())

    result.Print()

    frame = x.frame(ROOT.RooFit.Title("Gaussian Fit"))
    dataset.plotOn(frame)
    gauss.plotOn(frame)

    c = ROOT.TCanvas("c", "", 800, 600)
    frame.Draw()
    c.SaveAs("/eos/user/d/delvecch/www/PFG/gaussian_fit.png")

    integral_gauss = gauss.createIntegral(x, ROOT.RooFit.Range(""))
    area_full_range = integral_gauss.getVal()
    print(f"Area sotto la gaussiana del fit: {area_full_range}")

if __name__ == "__main__":
    main()

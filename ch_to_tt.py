def ch_to_tt(iPhi, iEta):
    return (abs(iEta)//5)*4 + 1 + ((360 - iPhi)%20)//5

if __name__ == "__main__":
  import sys

  iphi = int(sys.argv[1])
  ieta = int(sys.argv[2])
  tt = ch_to_tt(iphi, ieta)

  print(f"iPhi {iphi} iEta {ieta} is in TT {tt}")

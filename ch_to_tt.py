def ch_to_tt(iPhi, iEta):
    if iEta > 0: iPhi = 360 - iPhi
    return ((abs(iEta)-1)//5)*4 + 1 + ((iPhi-1)%20)//5

if __name__ == "__main__":
  import sys

  iphi = int(sys.argv[1])
  ieta = int(sys.argv[2])
  tt = ch_to_tt(iphi, ieta)

  print(f"iPhi {iphi} iEta {ieta} is in TT {tt}")

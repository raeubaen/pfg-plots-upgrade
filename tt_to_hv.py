
#EB+10 TT7-8 180/190iphi 5/10 ieta cmsechv05 board12 ch01

def get_board_ch(tt, smlabel):
  sm = int(smlabel.split('EB')[-1].split('+')[-1].split('-')[-1])

  return  ( (sm+1)//2 + 9*("-" in smlabel), 8*((sm-1)%2) + 2*((tt-1)//36) + 4*(((tt-1)//2)%2), ((tt-1)%36)//4 )

if __name__ == "__main__":
  import sys

  sm = sys.argv[1]
  tt = int(sys.argv[2])
  dcs, board, ch = get_board_ch(tt, sm)

  print(f"{sys.argv[1]} TT {tt} is in: EB HV (DCS {dcs}) board {board} ch {ch}")

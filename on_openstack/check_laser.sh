source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
source omsvenv/bin/activate
cd /root/oms-api-client/get-runs-oms

python3 get-runs-oms.py --durationthr 0 --year "$(date +%Y)" --month "$(date +%-m)" --lsthr 0 --ecal | tail -n 1 > /root/last_or_current_run

cd /root

DEST="/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026/"
SERVER="rgargiul@lxplus.cern.ch"

sshpass -p Evale2.71828 scp /root/last_or_current_run "$SERVER:$DEST/"
sshpass -p Evale2.71828 ssh $SERVER "source /afs/cern.ch/work/r/rgargiul/pfg-plots-upgrade/check_laser.sh"

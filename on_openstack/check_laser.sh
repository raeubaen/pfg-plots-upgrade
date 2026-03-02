source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
source omsvenv/bin/activate
cd /root/oms-api-client/get-runs-oms

python3 get-runs-oms.py --durationthr -1 --year "$(date +%Y)" --month "$(date -d '-1 month' +%-m)" --lsthr -1 --ecal > /tmp/last_runs
python3 get-runs-oms.py --durationthr -1 --year "$(date +%Y)" --month "$(date +%-m)" --lsthr -1 --ecal >> /tmp/last_runs
cat /tmp/last_runs

cat /tmp/last_runs | tail -n 1 > /root/last_or_current_run

cd /root

DEST="/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026/"


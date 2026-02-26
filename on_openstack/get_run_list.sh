#!/bin/bash

OFFSET=$1

source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
source omsvenv/bin/activate

OUTDIR="/root/ecal_es_run_list_for_pfg"
mkdir -p "$OUTDIR"

cd /root/oms-api-client/get-runs-oms

# --- Get full list of runs for current and previous month ---
python3 get-runs-oms.py --lsthr 10 --durationthr 0 --year "$(date +%Y)" --month "$(date -d '-1 month' +%-m)" > "$OUTDIR/all_runs.txt"
python3 get-runs-oms.py --lsthr 10 --durationthr 0 --year "$(date +%Y)" --month "$(date +%-m)" >> "$OUTDIR/all_runs.txt"

filter='{if ( (($20 ~ /coll/) && (int($6) > 10)) || ( (int($6)>100) && (int($13)>20) )) {print $0}}'

# --- Select runs for yesterday ) ---
grep "ECAL" "$OUTDIR/all_runs.txt" | grep "ECAL" | grep "ES" | grep $(date -d "-1 day $OFFSET" +%d/%m/%y) | awk "$filter" > "$OUTDIR/yesterday.txt"


week_yesterday=$(date -d "+1 week -1 day $OFFSET" +%W)
yesterday=$(date -d "-1 day $OFFSET" +%d-%B)

sshpass -p Evale2.71828  scp rgargiul@lxplus.cern.ch:/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026/week${week_yesterday}/${yesterday}/runlist_for_report.txt $OUTDIR/twodaysago_server_runs.txt
grep "ECAL" "$OUTDIR/all_runs.txt" | grep "ECAL" | grep "ES" | grep $(date -d "-2 day $OFFSET" +%d/%m/%y) | awk "$filter" > "$OUTDIR/twodaysago_oms.txt"

grep -Fxv -f $OUTDIR/twodaysago_server_runs.txt $OUTDIR/twodaysago_oms.txt > $OUTDIR/runlist_for_report.txt


cat $OUTDIR/yesterday.txt >> $OUTDIR/runlist_for_report.txt

# --- Prepare list for PFG plots ---
echo "run,dataset" > "$OUTDIR/runlist_for_pfg_plots.csv"
# fix at stable beams
#grep "collision" "$OUTDIR/runlist_for_report.txt" | awk '{print $4",/Global/Online/ALL/"}' >> "$OUTDIR/runlist_for_pfg_plots.csv"
cat "$OUTDIR/runlist_for_report.txt" | awk '{print $4",/Global/Online/ALL/"}' >> "$OUTDIR/runlist_for_pfg_plots.csv"


week=$(date -d '+1 week' +%W)
day=$(date +%d-%B)


DEST="/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026/week${week}/${day}"
SERVER="rgargiul@lxplus.cern.ch"

sshpass -p Evale2.71828 ssh rgargiul@lxplus.cern.ch "mkdir -p $DEST"
sshpass -p Evale2.71828 scp "$OUTDIR/runlist_for_report.txt" "$OUTDIR/runlist_for_pfg_plots.csv" "$SERVER:$DEST/"
sshpass -p Evale2.71828 scp /root/index.php "$SERVER:$DEST/"
sshpass -p Evale2.71828 scp /root/index.php "$SERVER:$DEST/../"

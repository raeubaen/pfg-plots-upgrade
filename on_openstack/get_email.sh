#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh

# Create the HTML mail file
echo -n "" > mail.html

# Start HTML
echo "<html><body>" >> mail.html

# Greeting
echo "<p>Dear ECAL colleagues,</p>" >> mail.html

# Report date
echo "<p>Please find below the PFG daily report for <b>$(date -d "yesterday" +"%B %-d, %Y")</b></p>" >> mail.html

# List of runs header (bold)
echo "<p><b>List of runs with either ECAL or ES in global, fulfilling one of the following conditions:</b></p>" >> mail.html
echo "<ul>" >> mail.html
echo "<li>collisions run with #LS > 10</li>" >> mail.html
echo "<li>or</li>" >> mail.html
echo "<li>cosmic/circulating/commissioning runs with #LS > 100 and Duration > 20 min</li>" >> mail.html
echo "</ul>" >> mail.html

# Append run list
echo "<pre>" >> mail.html
cat /root/ecal_es_run_list_for_pfg/runlist_for_report.txt >> mail.html
echo "</pre>" >> mail.html

# Performance plots URL
week=$(date -d '+1 week' +%W)
day=$(date +%d-%B)
SITE="https://cms-ecalpfg2.web.cern.ch/PFGshifts/PERFORMANCE2026/week${week}/${day}/"
echo "<p>The performance plots can be found at <a href=\"$SITE\">$SITE</a></p>" >> mail.html

# Monitoring & calibration header (bold)
echo "<p><b>Monitoring and calibration from the MoCa group:</b></p>" >> mail.html
echo "<ul>" >> mail.html
echo "<li>pi0, last fill: $(python3 last_fill_moca.py pi0)</li>" >> mail.html
echo "<li>pulse shapes, last fill: $(python3 last_fill_moca.py pulse-shapes/fills)</li>" >> mail.html
echo "<li>ratio timing, last fill: $(python3 last_fill_moca.py timing/timing_ratio)</li>" >> mail.html
echo "<li>cc timing, last fill: $(python3 last_fill_moca.py timing/timing_cc)</li>" >> mail.html
echo "</ul>" >> mail.html

# End HTML
echo "</body></html>" >> mail.html


sshpass -p Evale2.71828 scp mail.html rgargiul@lxplus.cern.ch:/eos/user/r/rgargiul/www/

sshpass -p Evale2.71828 ssh rgargiul@lxplus.cern.ch "source /afs/cern.ch/work/r/rgargiul/pfg-plots-upgrade/send_mail.sh"


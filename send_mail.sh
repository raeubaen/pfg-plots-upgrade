#!/bin/bash

# Mail recipient
TO="ruben.gargiulo@cern.ch"
SUBJECT="PFG Daily Report - INTERNAL"

source /cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh

cat /eos/user/r/rgargiul/www/mail.html > /eos/user/r/rgargiul/www/mail_mod.html
echo "" >> /eos/user/r/rgargiul/www/mail_mod.html

python3 /afs/cern.ch/work/r/rgargiul/pfg-plots-upgrade/light_checker_parse.py >> /eos/user/r/rgargiul/www/mail_mod.html

echo "" >> /eos/user/r/rgargiul/www/mail_mod.html

echo "<p>Best regards,</p>" >> /eos/user/r/rgargiul/www/mail_mod.html
echo "<p>Ruben Gargiulo for ECAL PFG</p>" >> /eos/user/r/rgargiul/www/mail_mod.html

# Build HTML body
BODY=$(cat /eos/user/r/rgargiul/www/mail_mod.html)

# Send email via sendmail
(
echo "To: $TO"
echo "Subject: $SUBJECT"
echo "MIME-Version: 1.0"
echo "Content-Type: text/html; charset=UTF-8"
echo ""
echo "$BODY"
) | /usr/sbin/sendmail -t

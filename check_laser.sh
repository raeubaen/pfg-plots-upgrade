source /cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh

# Create the HTML mail file
echo -n "" > /eos/user/r/rgargiul/www/alarms_mail.html

# Start HTML
echo "<html><body>" >> /eos/user/r/rgargiul/www/alarms_mail.html


python3 /afs/cern.ch/work/r/rgargiul/pfg-plots-upgrade/check_laser.py "$(cat /eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026/last_or_current_run)" | grep -v DEBUG > /eos/user/r/rgargiul/www/alarms.html

cat /eos/user/r/rgargiul/www/alarms.html

if grep -q "EXCEPTION" /eos/user/r/rgargiul/www/alarms.html; then
    echo "File contains EXCEPTION"
    echo "Sending email for exception..."
    cat /eos/user/r/rgargiul/www/alarms.html >> /eos/user/r/rgargiul/www/alarms_mail.html
    echo "</body></html>" >> /eos/user/r/rgargiul/www/alarms_mail.html
    echo -n "" > /eos/user/r/rgargiul/www/alarms.html
    TO="ruben.gargiulo@cern.ch"
    SUBJECT="Laser problems - exception in monitoring"

    BODY=$(cat /eos/user/r/rgargiul/www/alarms_mail.html)

    # Send email via sendmail
    (
    echo "To: $TO"
    echo "Subject: $SUBJECT"
    echo "MIME-Version: 1.0"
    echo "Content-Type: text/html; charset=UTF-8"
    echo ""
    echo "$BODY"
    ) | /usr/sbin/sendmail -t
\
fi

if [ -f "/eos/user/r/rgargiul/www/alarms.html" ] && [ -s "/eos/user/r/rgargiul/www/alarms.html" ]; then
  echo "Sending email"
  cat /eos/user/r/rgargiul/www/alarms.html >> /eos/user/r/rgargiul/www/alarms_mail.html
  echo "</body></html>" >> /eos/user/r/rgargiul/www/alarms_mail.html
  TO="cms-ecal-runcoord@cern.ch,ruben.gargiulo@cern.ch"
  #TO="ruben.gargiulo@cern.ch"
  SUBJECT="Laser problems - functionality test (no real alarm)"

  BODY=$(cat /eos/user/r/rgargiul/www/alarms_mail.html)

  # Send email via sendmail
  (
  echo "To: $TO"
  echo "Subject: $SUBJECT"
  echo "MIME-Version: 1.0"
  echo "Content-Type: text/html; charset=UTF-8"
  echo ""
  echo "$BODY"
  ) | /usr/sbin/sendmail -t
else
  echo "Not sendin anything"
fi

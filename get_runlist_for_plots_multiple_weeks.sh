echo "weeks from $1 to $2" >&2

files=""
for w in $(seq $1 $2); do
  for f in $(ls -d /eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025/week$w/*); do
      files=$(echo $files $(ls -1 $f/runlist_for_report.txt 2>&1 | grep -v "cannot"));
  done
done


echo "run,dataset"
cat $files | grep "collision"  | awk '$6 > 100' | awk '{print $4",/Global/Online/ALL/"}' | grep -v run

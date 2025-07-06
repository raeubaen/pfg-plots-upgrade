files=""
for w in $(seq $1 $2); do
  for f in $(ls -d /eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025/week$w/*); do
      files=$(echo $files $(ls -1 $f/runlist_for_pfg_plots.csv 2>&1 | grep -v "cannot"));
  done
done

cat $files | grep -v run

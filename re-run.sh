week=$1
day=$2

cp /eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026/week$week/$day/runlist_for_pfg_plots.csv ..

rm -f ../temp_pfg_plots_folder/*

python3 main.py ../runlist_for_pfg_plots.csv ../temp_pfg_plots_folder/

eos_pfg_performance_plots_2026="/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026"
rm $eos_pfg_performance_plots_2026/week$week/$day/*.csv
rm $eos_pfg_performance_plots_2026/week$week/$day/*.pdf
rm $eos_pfg_performance_plots_2026/week$week/$day/*.png
rm $eos_pfg_performance_plots_2026/week$week/$day/*.root

/bin/cp -f ../runlist_for_pfg_plots.csv $eos_pfg_performance_plots_2026/week$week/$day/

/bin/cp -f ../temp_pfg_plots_folder/* $eos_pfg_performance_plots_2026/week$week/$day/

week=$1
day=$2

source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

mkdir ../temp_pfg_plots_folder/

rm -f ../temp_pfg_plots_folder/*

cp /eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025/week$week/$day/runlist_for_pfg_plots.csv ..

python3 main.py ../runlist_for_pfg_plots.csv ../temp_pfg_plots_folder/

eos_pfg_performance_plots_2025="/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025"
mkdir -p $eos_pfg_performance_plots_2025/week$week/$day

/bin/cp -f ../temp_pfg_plots_folder/* $eos_pfg_performance_plots_2025/week$week/$day/

/bin/cp $eos_pfg_performance_plots_2025/index.php $eos_pfg_performance_plots_2025/week$week/$day/

/bin/cp $eos_pfg_performance_plots_2025/index.php $eos_pfg_performance_plots_2025/week$week


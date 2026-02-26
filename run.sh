#!/bin/bash

week=$(date -d '+1 week' +%W)
day=$(date +%d-%B)

cd /afs/cern.ch/work/r/rgargiul/pfg-plots-upgrade

date > date_debug

source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

mkdir ../temp_pfg_plots_folder/

rm -f ../temp_pfg_plots_folder/*

cp /eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026/week$week/$day/runlist_for_pfg_plots.csv ..

python3 main.py ../runlist_for_pfg_plots.csv ../temp_pfg_plots_folder/

eos_pfg_performance_plots_2026="/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2026"
mkdir -p $eos_pfg_performance_plots_2026/week$week/$day

/bin/cp -f ../temp_pfg_plots_folder/* $eos_pfg_performance_plots_2026/week$week/$day/

/bin/cp $eos_pfg_performance_plots_2026/index.php $eos_pfg_performance_plots_2026/week$week/$day/

/bin/cp $eos_pfg_performance_plots_2026/index.php $eos_pfg_performance_plots_2026/week$week


mkdir -p $eos_pfg_performance_plots_2026/week$week/weekly_summary/
python3 week_summary.py $week $eos_pfg_performance_plots_2026/week$week/weekly_summary/
/bin/cp $eos_pfg_performance_plots_2026/index.php $eos_pfg_performance_plots_2026/week$week/weekly_summary/


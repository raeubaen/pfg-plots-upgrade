#!/bin/bash

sshpass -p Evale2.71828 ssh rgargiul@lxplus.cern.ch source /afs/cern.ch/work/r/rgargiul/pfg-plots-upgrade/run.sh
#
#source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
#
#week=$(date -d '+1 week' +%W)
#
#umount -f eos_pfg_performance_plots_2025
#sshfs rgargiul@lxplus.cern.ch:/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025 eos_pfg_performance_plots_2025  -o ssh_command="sshpass -p Evale2.71828 ssh"
#
#umount -f eos_ruben
#sshfs rgargiul@lxplus.cern.ch:/eos/user/r/rgargiul/ eos_ruben  -o ssh_command="sshpass -p Evale2.71828 ssh"
#
#mkdir -p eos_pfg_performance_plots_2025/week$week/weekly_summary/
#python3 pfg-plots-upgrade/week_summary.py $week eos_pfg_performance_plots_2025/week$week/weekly_summary/
#/bin/cp eos_pfg_performance_plots_2025/index.php eos_pfg_performance_plots_2025/week$week/weekly_summary/

#day=$(date +%d-%B)
#
#source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
#
#rm -f temp_pfg_plots_folder/*
#
#python3 pfg-plots-upgrade/main.py ~/ecal_es_run_list_for_pfg/runlist_for_pfg_plots.csv temp_pfg_plots_folder/
#
#umount -f eos_pfg_performance_plots_2025
#sshfs rgargiul@lxplus.cern.ch:/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025 eos_pfg_performance_plots_2025  -o ssh_command="sshpass -p Evale2.71828 ssh"
#
#mkdir -p eos_pfg_performance_plots_2025/week$week/$day
#
#
#/bin/cp -f temp_pfg_plots_folder/* eos_pfg_performance_plots_2025/week$week/$day/
#
#/bin/cp eos_pfg_performance_plots_2025/index.php eos_pfg_performance_plots_2025/week$week/$day/
#
#/bin/cp eos_pfg_performance_plots_2025/index.php eos_pfg_performance_plots_2025/week$week

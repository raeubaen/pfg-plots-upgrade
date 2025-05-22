on lxplus:
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
python3 main.py <runlist.csv> <output_folder>
```


A more complete script:
```
!/bin/bash

week=$(date -d '+1 week' +%W)
day=$(date +%d-%B)

source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

rm -f ../temp_pfg_plots_folder/*

cp /eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025/week$week/$day/runlist_for_pfg_plots.csv ..

python3 main.py ../runlist_for_pfg_plots.csv ../temp_pfg_plots_folder/

eos_pfg_performance_plots_2025="/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025"
mkdir -p $eos_pfg_performance_plots_2025/week$week/$day

/bin/cp -f ../temp_pfg_plots_folder/* $eos_pfg_performance_plots_2025/week$week/$day/

/bin/cp $eos_pfg_performance_plots_2025/index.php $eos_pfg_performance_plots_2025/week$week/$day/

/bin/cp $eos_pfg_performance_plots_2025/index.php $eos_pfg_performance_plots_2025/week$week
```

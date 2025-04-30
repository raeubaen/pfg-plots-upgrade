#WIP

import pandas as pd
import matplotlib.pyplot as plt
import glob
import argparse
import sys
import itertools
from collections import defaultdict
import os

def parse_range(value):
    if '-' in value:
        start, end = map(int, value.split('-'))
        return list(range(start, end + 1))
    else:
        return [int(value)]


def group_files_by_name(files):
    file_groups = defaultdict(list)
    for file in files:
        file_name = file.split("/")[-1].split(".")[0]
        file_groups[file_name].append(file)
    return file_groups


parser = argparse.ArgumentParser()
parser.add_argument("weeks", nargs='+', type=parse_range, help="List of week numbers or ranges (e.g., '1-5' or '7').")
parser.add_argument("outfolder", type=str, help="output folder for plots")

args = parser.parse_args()

weeks = list(itertools.chain(*args.weeks))

print(weeks)

filelist = []
for week in weeks:
  filelist += glob.glob(f"/eos/project/c/cms-ecalpfg2/www/PFGshifts/PERFORMANCE2025/week{week}/*/*.csv", recursive=True)

file_groups = group_files_by_name(filelist)

for group in file_groups:
  files = file_groups[group]
  df = pd.concat([pd.read_csv(file) for file in files])
  counts = pd.DataFrame({"label": df["label"].value_counts().index, "counts": df["label"].value_counts().values})
  counts = counts[counts["counts"] > 1]
  df = counts.sort_values(by="counts", ascending=False).head(50)

  fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

  ax.scatter(df.label, df.counts, color='steelblue', edgecolor='black', s=80)

  ax.set_ylabel('#runs', fontsize=12)
  plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
  plt.setp(ax.get_yticklabels(), rotation=45, ha='right')
  ax.grid(True, linestyle='--', alpha=0.6)
  plt.tight_layout()

  plt.savefig(f"{outfolder}/{group}.png", dpi=300)


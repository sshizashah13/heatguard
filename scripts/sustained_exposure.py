import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.wbgt_calculator import add_wbgt_to_df
from scripts.occupation_classifier import OCCUPATION_PROFILES, classify_all_occupations


def extreme_runs(df, key):
    flag = (df[f'risk_{key}'] == 'EXTREME').astype(int)
    group = (flag != flag.shift()).cumsum()
    runs = []
    for _, block in df.groupby(group):
        if flag.loc[block.index[0]] == 1:
            runs.append((block['time'].iloc[0], len(block)))
    return runs


if __name__ == '__main__':
    df = pd.read_csv('data/karachi_2015_heatwave.csv')
    df['time'] = pd.to_datetime(df['time'])
    df = classify_all_occupations(add_wbgt_to_df(df))

    print(df.groupby(df['time'].dt.date)['WBGT'].max().round(2).to_string(), "\n")

    rows = []
    for key, p in OCCUPATION_PROFILES.items():
        runs = extreme_runs(df, key)
        start, hours = max(runs, key=lambda r: r[1]) if runs else (None, 0)
        rows.append({'profile': p['label'],
                     'extreme_hours': int((df[f'risk_{key}'] == 'EXTREME').sum()),
                     'longest_run_h': hours, 'run_start': start})
    out = pd.DataFrame(rows).sort_values('extreme_hours', ascending=False)
    print(out.to_string(index=False))
    out.to_csv('data/sustained_exposure_2015.csv', index=False)
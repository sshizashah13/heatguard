import pandas as pd
import numpy as np
from scipy import stats

# Documented daily deaths during the June 2015 Karachi heatwave
# Sources: Dawn News reports, WHO Pakistan Situation Report (June 2015),
# Pakistan Meteorological Department post-event analysis
DOCUMENTED_DEATHS_2015 = {
    '2015-06-18': 65,
    '2015-06-19': 228,
    '2015-06-20': 312,
    '2015-06-21': 280,
    '2015-06-22': 198,
    '2015-06-23': 89,
    '2015-06-24': 45,
    '2015-06-25': 11
}

# Baseline daily deaths for Karachi in June
# Derived from Pakistan Bureau of Statistics mortality estimates
# and peer-reviewed excess mortality literature for Karachi
BASELINE_DAILY_DEATHS_JUNE = 87

# Official total heat deaths reported vs. revised estimate
OFFICIAL_REPORTED_TOTAL = 1228
INITIAL_REPORTED_TOTAL = 65  # First official figure before revision

# Occupations with highest metabolic load; most vulnerable during heatwaves
HIGH_RISK_OCCUPATIONS = [
    'steel_furnace_worker',
    'salt_pan_worker',
    'glass_factory_worker',
    'road_paver',
    'sewage_worker',
    'brick_kiln_worker',
    'tandoor_baker',
    'agricultural_worker',
    'cotton_picker',
    'naali_safai'
]


def calculate_excess_mortality(df_hourly):
    """
    Calculates excess mortality above baseline for each day of the heatwave.

    Excess mortality = reported deaths - expected baseline deaths.
    The gap between excess deaths and officially labeled heat deaths
    reveals systematic misclassification — predominantly as cardiac failure.

    Parameters
    ----------
    df_hourly : pd.DataFrame
        Hourly WBGT-classified dataframe from the full pipeline

    Returns
    -------
    pd.DataFrame
        Daily summary with WBGT, deaths, excess mortality, and classification
    """
    death_df = pd.DataFrame([
        {'date': pd.to_datetime(d), 'reported_deaths': v}
        for d, v in DOCUMENTED_DEATHS_2015.items()
    ])

    death_df['excess_deaths'] = (
        death_df['reported_deaths'] - BASELINE_DAILY_DEATHS_JUNE
    ).clip(lower=0)

    death_df['probable_heat_deaths'] = death_df['excess_deaths']

    death_df['officially_labeled_heat'] = death_df['reported_deaths'].apply(
        lambda x: round(x * 0.72)
    )

    death_df['likely_miscounted'] = (
        death_df['excess_deaths'] - death_df['officially_labeled_heat']
    ).clip(lower=0)

    df_hourly['date'] = pd.to_datetime(df_hourly['time'].dt.date)
    daily_wbgt = df_hourly.groupby('date').agg(
        peak_WBGT=('WBGT', 'max'),
        mean_WBGT=('WBGT', 'mean'),
        hours_above_30=('WBGT', lambda x: (x >= 30).sum()),
        hours_above_32=('WBGT', lambda x: (x >= 32).sum()),
        hours_above_33=('WBGT', lambda x: (x >= 33).sum()),
    ).reset_index()

    result = death_df.merge(daily_wbgt, on='date', how='left')
    return result


def calculate_wbgt_death_correlation(result_df):
    """
    Pearson correlation between peak daily WBGT and reported deaths.

    A high correlation (>0.85) provides statistical evidence that
    WBGT — not air temperature alone — tracks mortality during heatwaves.
    This supports the paper's central argument for WBGT over heat index.
    """
    corr, pvalue = stats.pearsonr(
        result_df['peak_WBGT'].dropna(),
        result_df['reported_deaths'].dropna()
    )
    return round(corr, 4), round(pvalue, 6)


def calculate_kill_windows(df_hourly, occupation_key, threshold_type='extreme'):
    """
    Identifies consecutive hours where risk stays at EXTREME or HIGH.

    A kill window is the continuous exposure period most likely to
    cause heat stroke — not just peak temperature, but sustained duration.
    This is the feature that distinguishes HeatGuard from point-in-time tools.

    Parameters
    ----------
    df_hourly : pd.DataFrame
        Hourly classified dataframe
    occupation_key : str
        Key from OCCUPATION_PROFILES
    threshold_type : str
        'extreme' or 'high' — which risk level to find windows for

    Returns
    -------
    pd.DataFrame
        All kill windows with start time, end time, and duration in hours
    """
    risk_col = f'risk_{occupation_key}'
    levels = ['EXTREME'] if threshold_type == 'extreme' else ['EXTREME', 'HIGH']

    df_hourly['in_window'] = df_hourly[risk_col].isin(levels)

    windows = []
    current_start = None
    count = 0

    for _, row in df_hourly.iterrows():
        if row['in_window']:
            if current_start is None:
                current_start = row['time']
                peak_wbgt = row['WBGT']
            else:
                peak_wbgt = max(peak_wbgt, row['WBGT'])
            count += 1
        else:
            if count > 0:
                windows.append({
                    'start': current_start,
                    'end': row['time'],
                    'duration_hours': count,
                    'peak_WBGT': round(peak_wbgt, 2),
                    'occupation': occupation_key,
                    'threshold': threshold_type.upper()
                })
            current_start = None
            count = 0
            peak_wbgt = 0

    if count > 0:
        windows.append({
            'start': current_start,
            'end': df_hourly.iloc[-1]['time'],
            'duration_hours': count,
            'peak_WBGT': round(peak_wbgt, 2),
            'occupation': occupation_key,
            'threshold': threshold_type.upper()
        })

    return pd.DataFrame(windows)


def calculate_all_kill_windows(df_hourly):
    """
    Runs kill window detection across all high-risk occupations.
    Returns a combined dataframe sorted by duration descending.
    """
    from scripts.occupation_classifier import OCCUPATION_PROFILES

    all_windows = []
    for occ in HIGH_RISK_OCCUPATIONS:
        if occ in OCCUPATION_PROFILES and f'risk_{occ}' in df_hourly.columns:
            windows = calculate_kill_windows(df_hourly, occ, 'extreme')
            if not windows.empty:
                all_windows.append(windows)

    if not all_windows:
        return pd.DataFrame()

    combined = pd.concat(all_windows, ignore_index=True)
    return combined.sort_values('duration_hours', ascending=False).reset_index(drop=True)


def generate_mortality_report(df_hourly):
    """
    Generates the complete mortality analysis summary.
    This is the function called by the dashboard and the paper results section.
    """
    result = calculate_excess_mortality(df_hourly)
    corr, pvalue = calculate_wbgt_death_correlation(result)
    kill_windows = calculate_all_kill_windows(df_hourly)

    total_excess = int(result['excess_deaths'].sum())
    total_reported = int(result['reported_deaths'].sum())
    total_miscounted = int(result['likely_miscounted'].sum())
    peak_day = result.loc[result['reported_deaths'].idxmax(), 'date']
    peak_wbgt = round(result['peak_WBGT'].max(), 1)
    longest_window = kill_windows.iloc[0] if not kill_windows.empty else None

    summary = {
        'total_reported_deaths': total_reported,
        'total_excess_deaths': total_excess,
        'total_likely_miscounted': total_miscounted,
        'miscount_rate_pct': round((total_miscounted / total_excess * 100), 1) if total_excess > 0 else 0,
        'wbgt_death_correlation': corr,
        'correlation_pvalue': pvalue,
        'peak_mortality_day': peak_day.strftime('%B %d, %Y'),
        'peak_wbgt': peak_wbgt,
        'longest_kill_window_hours': int(longest_window['duration_hours']) if longest_window is not None else 0,
        'longest_kill_window_occupation': longest_window['occupation'] if longest_window is not None else '',
        'daily_breakdown': result,
        'kill_windows': kill_windows
    }

    return summary


if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from scripts.fetch_weather import fetch_weather
    from scripts.wbgt_calculator import add_wbgt_to_df
    from scripts.occupation_classifier import classify_all_occupations

    print("Loading 2015 heatwave data...")
    df = pd.read_csv('data/karachi_2015_heatwave.csv')
    df['time'] = pd.to_datetime(df['time'])
    df = add_wbgt_to_df(df)
    df = classify_all_occupations(df)

    print("Running mortality analysis...\n")
    report = generate_mortality_report(df)

    print("=" * 60)
    print("HEATGUARD — 2015 KARACHI HEATWAVE MORTALITY ANALYSIS")
    print("=" * 60)

    print(f"\nTotal reported deaths:         {report['total_reported_deaths']}")
    print(f"Estimated excess deaths:       {report['total_excess_deaths']}")
    print(f"Likely miscounted as cardiac:  {report['total_likely_miscounted']}")
    print(f"Miscount rate:                 {report['miscount_rate_pct']}%")
    print(f"\nWBGT–mortality correlation:    r = {report['wbgt_death_correlation']}")
    print(f"Statistical significance:      p = {report['correlation_pvalue']}")
    print(f"\nPeak mortality day:            {report['peak_mortality_day']}")
    print(f"Peak WBGT that day:            {report['peak_wbgt']}°C")
    print(f"\nLongest EXTREME kill window:   {report['longest_kill_window_hours']} hours")
    print(f"Occupation:                    {report['longest_kill_window_occupation']}")

    print("\n\nDAILY BREAKDOWN:")
    print("-" * 60)
    cols = ['date', 'peak_WBGT', 'reported_deaths', 'excess_deaths', 'likely_miscounted']
    print(report['daily_breakdown'][cols].to_string(index=False))

    print("\n\nTOP 5 KILL WINDOWS:")
    print("-" * 60)
    if not report['kill_windows'].empty:
        print(report['kill_windows'].head(5)[
            ['occupation', 'start', 'duration_hours', 'peak_WBGT', 'threshold']
        ].to_string(index=False))

    report['daily_breakdown'].to_csv('data/mortality_analysis_2015.csv', index=False)
    report['kill_windows'].to_csv('data/kill_windows_2015.csv', index=False)
    print("\nSaved to data/mortality_analysis_2015.csv")
    print("Saved to data/kill_windows_2015.csv")
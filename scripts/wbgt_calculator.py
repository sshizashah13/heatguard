import numpy as np
import pandas as pd

def stull_wet_bulb(T, RH):
    Tw = (T * np.arctan(0.151977 * (RH + 8.313659)**0.5)
          + np.arctan(T + RH)
          - np.arctan(RH - 1.676331)
          + 0.00391838 * RH**1.5 * np.arctan(0.023101 * RH)
          - 4.686035)
    return Tw

def globe_temperature(T, solar_wm2, wind_ms):
    Tg = T + (0.0117 * solar_wm2) - (2.8 * wind_ms) + 2.5
    return Tg

def calculate_outdoor_wbgt(T, RH, solar_wm2, wind_ms):
    Tw = stull_wet_bulb(T, RH)
    Tg = globe_temperature(T, solar_wm2, wind_ms)
    WBGT = 0.7 * Tw + 0.2 * Tg + 0.1 * T
    return WBGT

def add_wbgt_to_df(df):
    df['wet_bulb_c'] = stull_wet_bulb(df['temp_c'], df['rh_pct'])
    df['globe_temp_c'] = globe_temperature(df['temp_c'], df['solar_wm2'], df['wind_ms'])
    df['WBGT'] = calculate_outdoor_wbgt(df['temp_c'], df['rh_pct'], df['solar_wm2'], df['wind_ms'])
    return df

if __name__ == '__main__':
    df = pd.read_csv('data/karachi_2015_heatwave.csv')
    df['time'] = pd.to_datetime(df['time'])
    df = add_wbgt_to_df(df)
    
    print("WBGT calculated successfully!")
    print(df[['time', 'temp_c', 'rh_pct', 'WBGT']].head(10))
    print(f"\nMax WBGT during 2015 heatwave: {df['WBGT'].max():.1f}°C")
    print(f"Min WBGT during 2015 heatwave: {df['WBGT'].min():.1f}°C")
    
    df.to_csv('data/karachi_2015_with_wbgt.csv', index=False)
    print("\nSaved to data/karachi_2015_with_wbgt.csv")
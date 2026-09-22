import requests
import pandas as pd

def fetch_karachi_weather(start_date=None, end_date=None):
    lat, lon = 24.8607, 67.0011

    params = {
        'latitude': lat,
        'longitude': lon,
        'hourly': 'temperature_2m,relativehumidity_2m,windspeed_10m,shortwave_radiation',
        'timezone': 'Asia/Karachi',
        'wind_speed_unit': 'ms'
    }

    if start_date:
        url = 'https://archive-api.open-meteo.com/v1/archive'
        params['start_date'] = start_date
        params['end_date'] = end_date
    else:
        url = 'https://api.open-meteo.com/v1/forecast'

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data['hourly'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.rename(columns={
        'temperature_2m': 'temp_c',
        'relativehumidity_2m': 'rh_pct',
        'windspeed_10m': 'wind_ms',
        'shortwave_radiation': 'solar_wm2'
    })
    return df

if __name__ == '__main__':
    # Live forecast
    df_live = fetch_karachi_weather()
    df_live.to_csv('data/karachi_live.csv', index=False)
    print(f"Live data: {len(df_live)} rows")
    print(df_live.head())

    # 2015 heatwave
    df_2015 = fetch_karachi_weather('2015-06-18', '2015-06-25')
    df_2015.to_csv('data/karachi_2015_heatwave.csv', index=False)
    print(f"\n2015 heatwave data: {len(df_2015)} rows")
    print(df_2015.head())
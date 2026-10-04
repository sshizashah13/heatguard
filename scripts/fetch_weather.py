import os
import requests
import pandas as pd

PAKISTAN_CITIES = {
    'Karachi':     (24.8607,  67.0011),
    'Lahore':      (31.5497,  74.3436),
    'Islamabad':   (33.6844,  73.0479),
    'Peshawar':    (34.0151,  71.5249),
    'Quetta':      (30.1798,  66.9750),
    'Multan':      (30.1575,  71.5249),
    'Faisalabad':  (31.4504,  73.1350),
    'Hyderabad':   (25.3960,  68.3578),
    'Sukkur':      (27.7052,  68.8574),
    'Larkana':     (27.5570,  68.2128),
    'Jacobabad':   (28.2769,  68.4516),
    'Sibi':        (29.5431,  67.8772),
    'Jamshoro':    (25.4305,  68.2802),
}

def fetch_weather(start_date=None, end_date=None, city='Karachi'):
    lat, lon = PAKISTAN_CITIES.get(city, PAKISTAN_CITIES['Karachi'])

    params = {
        'latitude': lat,
        'longitude': lon,
        'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation',
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
        'relative_humidity_2m': 'rh_pct',
        'wind_speed_10m': 'wind_ms',
        'shortwave_radiation': 'solar_wm2'
    })
    return df

if __name__ == '__main__':
    
    os.makedirs('data', exist_ok=True)

    # Live forecast
    df_live = fetch_weather(city='Karachi')
    df_live.to_csv('data/karachi_live.csv', index=False)
    print(f"Live data: {len(df_live)} rows")
    print(df_live.head())

    # 2015 heatwave historical archive
    df_2015 = fetch_weather('2015-06-18', '2015-06-25', city='Karachi')
    df_2015.to_csv('data/karachi_2015_heatwave.csv', index=False)
    print(f"\n2015 heatwave data: {len(df_2015)} rows")
    print(df_2015.head())
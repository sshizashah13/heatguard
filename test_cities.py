import sys
sys.path.append('.')
from scripts.fetch_weather import fetch_weather, PAKISTAN_CITIES
from scripts.wbgt_calculator import add_wbgt_to_df
from scripts.occupation_classifier import classify_risk
from datetime import datetime

for city in list(PAKISTAN_CITIES.keys()):
    try:
        df = fetch_weather(city=city)
        df = add_wbgt_to_df(df)
        nh = datetime.now().hour
        rows = df[df['time'].dt.hour == nh]
        cur = rows.iloc[0] if len(rows) else df.iloc[0]
        wbgt = float(cur['WBGT'])
        risk = classify_risk(wbgt, 'construction_laborer')
        print(f'{city}: WBGT={wbgt:.1f} Risk={risk}')
    except Exception as e:
        print(f'{city}: ERROR - {e}')
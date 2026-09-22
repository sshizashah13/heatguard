import pandas as pd

OCCUPATION_PROFILES = {
    # TRANSPORT & ROADS
    'construction_laborer': {
        'label': 'Construction Laborer',
        'metabolic_rate_W': 450,
        'thresholds': {'moderate': 25, 'high': 28, 'extreme': 32},
        'work_rest': {'moderate': (45, 15), 'high': (30, 30), 'extreme': (15, 45)}
    },
    'rickshaw_driver': {
        'label': 'Rickshaw Driver',
        'metabolic_rate_W': 280,
        'thresholds': {'moderate': 27, 'high': 30, 'extreme': 33},
        'work_rest': {'moderate': (50, 10), 'high': (35, 25), 'extreme': (20, 40)}
    },
    'truck_driver': {
        'label': 'Truck Driver',
        'metabolic_rate_W': 180,
        'thresholds': {'moderate': 28, 'high': 32, 'extreme': 35},
        'work_rest': {'moderate': (55, 5), 'high': (45, 15), 'extreme': (30, 30)}
    },
    'road_paver': {
        'label': 'Road Paver / Asphalt Layer',
        'metabolic_rate_W': 470,
        # Works directly on asphalt: surface temp hits 70-75C in Karachi summer
        # Adjusted thresholds DOWN to reflect radiant heat from surface
        'thresholds': {'moderate': 23, 'high': 26, 'extreme': 29},
        'work_rest': {'moderate': (40, 20), 'high': (20, 40), 'extreme': (10, 50)}
    },

    # STREET ECONOMY
    'street_vendor': {
        'label': 'Street Vendor (Rehri Wala)',
        'metabolic_rate_W': 200,
        'thresholds': {'moderate': 28, 'high': 31, 'extreme': 34},
        'work_rest': {'moderate': (55, 5), 'high': (45, 15), 'extreme': (30, 30)}
    },
    'delivery_rider': {
        'label': 'Motorcycle Delivery Rider',
        'metabolic_rate_W': 350,
        'thresholds': {'moderate': 26, 'high': 30, 'extreme': 34},
        'work_rest': {'moderate': (50, 10), 'high': (40, 20), 'extreme': (20, 40)}
    },
    'sabzi_mandi_seller': {
        'label': 'Fruit & Vegetable Seller (Sabzi Mandi)',
        'metabolic_rate_W': 220,
        # Outdoor market, standing on concrete, heavy lifting of crates
        'thresholds': {'moderate': 27, 'high': 30, 'extreme': 33},
        'work_rest': {'moderate': (50, 10), 'high': (40, 20), 'extreme': (20, 40)}
    },
    'shoe_shiner': {
        'label': 'Shoe Shiner / Mochi',
        'metabolic_rate_W': 160,
        # Crouching on pavement all day — ground-level heat is worse than standing
        'thresholds': {'moderate': 27, 'high': 30, 'extreme': 33},
        'work_rest': {'moderate': (55, 5), 'high': (45, 15), 'extreme': (25, 35)}
    },
    'kabari_wala': {
        'label': 'Scrap Collector (Kabari Wala)',
        'metabolic_rate_W': 320,
        # Walks 10-15km daily pushing heavy cart in direct sun
        'thresholds': {'moderate': 26, 'high': 29, 'extreme': 32},
        'work_rest': {'moderate': (45, 15), 'high': (30, 30), 'extreme': (15, 45)}
    },

    # AGRICULTURE & FISHING
    'agricultural_worker': {
        'label': 'Agricultural Worker',
        'metabolic_rate_W': 420,
        'thresholds': {'moderate': 25, 'high': 27, 'extreme': 30},
        'work_rest': {'moderate': (40, 20), 'high': (25, 35), 'extreme': (10, 50)}
    },
    'cotton_picker': {
        'label': 'Cotton Picker',
        'metabolic_rate_W': 390,
        # Sindh peak cotton season = peak heat season. Bending repeatedly all day.
        'thresholds': {'moderate': 25, 'high': 27, 'extreme': 30},
        'work_rest': {'moderate': (40, 20), 'high': (25, 35), 'extreme': (10, 50)}
    },
    'fisherman': {
        'label': 'Fisherman (Machera)',
        'metabolic_rate_W': 350,
        # Sea surface reflects solar radiation — double exposure from above and below
        'thresholds': {'moderate': 26, 'high': 29, 'extreme': 32},
        'work_rest': {'moderate': (45, 15), 'high': (30, 30), 'extreme': (15, 45)}
    },
    'salt_pan_worker': {
        'label': 'Salt Pan Worker',
        'metabolic_rate_W': 400,
        # White salt flats reflect ~80% of solar radiation — radiation from above AND below
        # Most extreme microclimate in Pakistan. Thresholds significantly lower.
        'thresholds': {'moderate': 22, 'high': 25, 'extreme': 28},
        'work_rest': {'moderate': (35, 25), 'high': (20, 40), 'extreme': (10, 50)}
    },

    # WASTE & SANITATION
    'garbage_collector': {
        'label': 'Sanitation / Garbage Collector',
        'metabolic_rate_W': 380,
        'thresholds': {'moderate': 25, 'high': 28, 'extreme': 32},
        'work_rest': {'moderate': (45, 15), 'high': (30, 30), 'extreme': (15, 45)}
    },
    'sweeper': {
        'label': 'Street Sweeper',
        'metabolic_rate_W': 300,
        # Works 5am-9am but also afternoon shifts on asphalt
        'thresholds': {'moderate': 26, 'high': 29, 'extreme': 32},
        'work_rest': {'moderate': (50, 10), 'high': (35, 25), 'extreme': (15, 45)}
    },
    'naali_safai': {
        'label': 'Open Drain Cleaner (Naali Safai Wala)',
        'metabolic_rate_W': 400,
        # Crouching in open drains — trapped radiant heat + toxic gases
        'thresholds': {'moderate': 24, 'high': 27, 'extreme': 30},
        'work_rest': {'moderate': (40, 20), 'high': (20, 40), 'extreme': (10, 50)}
    },
    'sewage_worker': {
        'label': 'Sewage / Manhole Worker',
        'metabolic_rate_W': 420,
        # Underground manholes trap heat — ambient WBGT underestimates real exposure
        'thresholds': {'moderate': 24, 'high': 26, 'extreme': 29},
        'work_rest': {'moderate': (35, 25), 'high': (20, 40), 'extreme': (10, 50)}
    },

    # INDUSTRIAL & MANUFACTURING
    'brick_kiln_worker': {
        'label': 'Brick Kiln Worker (Bhatta Mazdoor)',
        'metabolic_rate_W': 480,
        'thresholds': {'moderate': 24, 'high': 27, 'extreme': 30},
        'work_rest': {'moderate': (40, 20), 'high': (20, 40), 'extreme': (10, 50)}
    },
    'tandoor_baker': {
        'label': 'Tandoor Baker (Naan Maker)',
        'metabolic_rate_W': 430,
        # Stands over 400C clay oven for 8-10 hours. Radiant heat load is extreme.
        # Indoor but no cooling. Thresholds adjusted for radiant heat source.
        'thresholds': {'moderate': 24, 'high': 26, 'extreme': 29},
        'work_rest': {'moderate': (40, 20), 'high': (25, 35), 'extreme': (10, 50)}
    },
    'textile_mill_worker': {
        'label': 'Textile Mill Worker',
        'metabolic_rate_W': 250,
        # Indoor but humidity from steam + machinery heat — often worse than outside
        'thresholds': {'moderate': 26, 'high': 29, 'extreme': 32},
        'work_rest': {'moderate': (50, 10), 'high': (35, 25), 'extreme': (20, 40)}
    },
    'glass_factory_worker': {
        'label': 'Glass Factory Worker',
        'metabolic_rate_W': 460,
        # Works near 1400C molten glass. Extreme radiant heat even 10 feet away.
        'thresholds': {'moderate': 22, 'high': 25, 'extreme': 28},
        'work_rest': {'moderate': (35, 25), 'high': (20, 40), 'extreme': (10, 50)}
    },
    'steel_furnace_worker': {
        'label': 'Steel / Glass Furnace Worker',
        'metabolic_rate_W': 500,
        # Highest metabolic rate of any occupation in this list
        # Radiant heat from furnace means ambient WBGT massively underestimates exposure
        'thresholds': {'moderate': 22, 'high': 24, 'extreme': 27},
        'work_rest': {'moderate': (30, 30), 'high': (20, 40), 'extreme': (10, 50)}
    },
    'cement_factory_worker': {
        'label': 'Cement Factory Worker',
        'metabolic_rate_W': 350,
        # Dust + heat combination. Outdoor loading areas hit extreme temperatures.
        'thresholds': {'moderate': 25, 'high': 28, 'extreme': 31},
        'work_rest': {'moderate': (45, 15), 'high': (30, 30), 'extreme': (15, 45)}
    },
    'ice_factory_worker': {
        'label': 'Ice Factory Worker',
        'metabolic_rate_W': 300,
        # Unique thermal shock: moves between freezing cold storage and 45C loading docks
        # Risk is cardiovascular from temperature cycling, not sustained heat alone
        'thresholds': {'moderate': 26, 'high': 29, 'extreme': 32},
        'work_rest': {'moderate': (45, 15), 'high': (30, 30), 'extreme': (20, 40)}
    },
}

def classify_risk(wbgt, occupation):
    t = OCCUPATION_PROFILES[occupation]['thresholds']
    if wbgt >= t['extreme']: return 'EXTREME'
    elif wbgt >= t['high']: return 'HIGH'
    elif wbgt >= t['moderate']: return 'MODERATE'
    else: return 'SAFE'

def get_work_rest(risk, occupation):
    if risk == 'SAFE': return (60, 0)
    return OCCUPATION_PROFILES[occupation]['work_rest'].get(risk.lower(), (60, 0))

def calculate_omgi(wbgt):
    office_wbgt = 22.0
    extreme_threshold = 32.0
    if wbgt <= office_wbgt: return 1.0
    gap = (wbgt - office_wbgt) / (extreme_threshold - office_wbgt)
    return round(max(1.0, gap * 10), 1)

def classify_all_occupations(df):
    for occ in OCCUPATION_PROFILES:
        df[f'risk_{occ}'] = df['WBGT'].apply(lambda w: classify_risk(w, occ))
    df['OMGI'] = df['WBGT'].apply(calculate_omgi)
    return df

if __name__ == '__main__':
    df = pd.read_csv('data/karachi_2015_with_wbgt.csv')
    df['time'] = pd.to_datetime(df['time'])
    df = classify_all_occupations(df)

    print("Risk classification complete!\n")
    print(f"Peak OMGI score: {df['OMGI'].max()}")
    print("\nHours at EXTREME risk during 2015 heatwave (192 hours total):")
    for occ, profile in OCCUPATION_PROFILES.items():
        extreme_hours = (df[f'risk_{occ}'] == 'EXTREME').sum()
        bar = '█' * extreme_hours
        print(f"  {profile['label']:<45} {extreme_hours:>3} hrs  {bar}")

    df.to_csv('data/karachi_2015_classified.csv', index=False)
    print("\nSaved to data/karachi_2015_classified.csv")
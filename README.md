# HeatGuard

Most heat warning systems warn about the weather.  
This one warns about the person standing in it.

A construction laborer and a delivery rider on the same Karachi street corner 
at the same moment face biologically different emergencies — different metabolic 
loads, different thresholds, different survival windows. No existing system 
accounts for that. HeatGuard does.

**Live:** https://heatguard-pakistan.streamlit.app

---

## What it does

Pulls hourly weather data from Open-Meteo, computes Wet-Bulb Globe Temperature 
using the Stull (2011) formula with solar radiation correction, and classifies 
heat stress risk across 24 occupation profiles calibrated to NIOSH metabolic 
rate thresholds. It then generates occupation-specific safety guidance in English 
and Roman Urdu through a large language model — calibrated for 5th-grade literacy, 
because that's who needs to read it.

The system is retrospectively validated against the June 2015 Karachi heatwave, 
which killed 1,228 people in a single week — most of them outdoor laborers, most 
of their deaths recorded as cardiac failure.

---

## Key findings from 2015 validation

- Peak WBGT: **33.7°C** (June 20, 2015) — above EXTREME threshold for all 
  high-metabolic occupations
- Steel furnace workers remained at EXTREME risk for **92 consecutive hours**
- Peak OMGI: **11.7×** — a steel furnace worker experienced heat stress 11.7 
  times more dangerous than an office worker at the same location and moment
- WBGT–mortality correlation: **r = 0.53** (n=8 days)

---

## The OMGI

The Occupational Mortality Gap Index is an original metric introduced in this 
project. It quantifies how many times more dangerous a heat event is for an 
outdoor heavy-labor worker versus an air-conditioned office worker at the same 
GPS coordinate and time. During the 2015 Karachi peak, that number was 11.7.

---

## Occupation profiles

24 Pakistan-specific worker categories with individual WBGT thresholds 
and NIOSH work/rest schedules:

Salt pan workers · Steel furnace workers · Brick kiln workers (Bhatta Mazdoor) ·  
Tandoor bakers · Road pavers · Sewage workers · Naali safai workers ·  
Cotton pickers · Fishermen (Machera) · Rickshaw drivers · Kabari walas ·  
Construction laborers · and 12 more.

Thresholds are set lower for workers with higher metabolic rates and radiant 
heat exposure — a salt pan worker's EXTREME threshold is 28°C WBGT, not 32°C, 
because white salt flats reflect 80% of solar radiation from below as well as above.

---

## El Niño mode

WHO–WMO declared El Niño a "significant public health threat" in September 2026. 
The Climate Impact Lab projects 451,000 additional heat deaths globally through 
February 2027. When El Niño mode is toggled on, HeatGuard applies a +1.2°C 
WBGT elevation across all classifications — consistent with Climate Impact Lab 
projections of 44% more extremely hot days.

---

## Cities covered

Karachi · Lahore · Islamabad · Peshawar · Quetta · Multan ·  
Faisalabad · Hyderabad · Sukkur · Larkana · Jacobabad · Sibi . Jamshoro

Jacobabad and Sibi are among the hottest cities on earth by peak WBGT and 
regularly approach the theoretical limit of human survivability.

---

## Project structure
heatguard/
├── dashboard/
│ └── app.py # Streamlit dashboard
├── scripts/
│ ├── fetch_weather.py # Open-Meteo API, 12 Pakistan cities
│ ├── wbgt_calculator.py # Stull (2011) formula, solar correction
│ ├── occupation_classifier.py # 24 profiles, NIOSH thresholds, OMGI
│ ├── mortality_analysis.py # 2015 heatwave correlation analysis
│ └── guidance_generator.py # Gemini bilingual guidance generator
└── data/
└── karachi_2015_heatwave.csv



## Run locally

```bash
git clone https://github.com/sshizashah13/heatguard.git
cd heatguard
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Add a `.env` file with your Gemini API key:
GEMINI_API_KEY=your_key_here


---

## References

- Stull, R. (2011). Wet-Bulb Temperature from Relative Humidity and Air 
  Temperature. *Journal of Applied Meteorology and Climatology*, 50(11), 2267–2269.
- NIOSH (2016). *Criteria for a Recommended Standard: Occupational Exposure 
  to Heat and Hot Environments*. DHHS (NIOSH) Publication No. 2016-106.
- ISO 7933:2004. *Ergonomics of the thermal environment — analytical 
  determination of thermal stress*.
- WHO–WMO Joint Programme (2026). El Niño declared significant public health 
  threat. *Dawn*, September 22, 2026.
- Climate Impact Lab (2026). El Niño heat mortality projections. 
  *Dawn*, September 23, 2026.

---

## Conference

Submitted to the 1st International Conference on Smart Sustainable Infrastructure  
for Circular Economy and Resource Efficiency — MUET Jamshoro

**Author:** Shiza Shah · Department of Computer Science · MUET Jamshoro  
**LinkedIn:** [linkedin.com/in/sshizashah](https://linkedin.com/in/sshizashah)
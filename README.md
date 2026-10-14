
# HeatGuard

Most heat warning systems warn about the weather.  
This one warns about the person standing in it.

A construction laborer and a delivery rider on the same Karachi street corner at the same moment face biologically different emergencies: different metabolic loads, different exposure thresholds, and different physiological limits. No existing system accounts for these differences. HeatGuard does.

**Live:** https://heatguard-pakistan.streamlit.app

---

## What It Does

HeatGuard pulls hourly meteorological data from Open-Meteo, computes Wet-Bulb Globe Temperature (WBGT) using the Stull (2011) wet-bulb equation alongside an outdoor solar and wind weighting correction (ISO 7243:2017), and classifies thermal risk across 24 occupation profiles calibrated to NIOSH metabolic limits. 

It then generates task-specific safety guidance in English and native Urdu script (اردو) using Gemini 3.6 Flash, calibrated to approximately a fifth-grade literacy level and grounded in realistic workplace microclimates.

The system is retrospectively evaluated against documented conditions of the June 2015 Karachi heatwave, one of the deadliest thermal disasters in modern regional history.

---

## Key Findings from 2015 Validation

- **Peak WBGT:** Estimated WBGT peaked at **33.7 °C on June 22, 2015** (coinciding with the Pakistan Meteorological Department's documented severe heatwave window).
- **Occupational Differentiation:** At peak WBGT, 21 of 24 occupation profiles reached the EXTREME risk tier, whereas lower-exertion profiles (delivery riders, vendors, truck drivers) remained at HIGH risk.
- **Sustained Exposure:** Model outputs reveal a continuous **92-hour EXTREME risk window** for high-radiant steel/glass furnace workers under profile thresholds (June 19–23).
- **Peak OMGI:** Peak Occupational Mortality Gap Index reached **11.7**, quantifying an environmental heat exposure gap significantly above an indoor climate-controlled reference.

---

## Occupational Mortality Gap Index (OMGI)

The Occupational Mortality Gap Index (OMGI) is a normalized metric introduced in this project to summarize environmental heat exposure inequality. It quantifies how far ambient WBGT exceeds a climate-controlled indoor reference baseline ($W_{\text{ref}} = 22\text{ }^\circ\text{C}$):

$$
\text{OMGI} = \max\left(1, 10 \cdot \frac{\text{WBGT} - W_{\text{ref}}}{W_{\text{ext}} - W_{\text{ref}}}\right)
$$

where $W_{\text{ext}} = 32^\circ\text{C}$ corresponds to the EXTREME threshold of a heavy-labor worker. During the June 22, 2015 Karachi peak, the OMGI reached 11.7.

---

## Occupation Profiles

24 Pakistan-specific worker categories with individual WBGT thresholds and NIOSH-anchored work/rest allocations:

Salt pan workers · Steel / glass furnace workers · Brick kiln workers (Bhatta Mazdoor) · Tandoor bakers · Road pavers / asphalt layers · Sewage / manhole workers · Open drain cleaners (Naali safai wala) · Cotton pickers · Fishermen (Machera) · Rickshaw drivers · Scrap collectors (Kabari wala) · Construction laborers · and 12 more.

Thresholds are set lower for occupations with high metabolic rates or high radiant heat exposure. For example, a salt pan worker's EXTREME threshold is set to 28 °C WBGT rather than 32 °C to account for ground radiation reflected off white salt flats.

---

## El Niño Sensitivity Mode

In September 2026, the WHO–WMO Joint Programme declared the ongoing El Niño phase a "significant public health threat," with independent projections estimating substantial additional heat mortality globally through early 2027. 

When El Niño mode is toggled on, HeatGuard applies a precautionary +1.2 °C land-temperature anomaly across classifications. This sensitivity scenario is disabled in all retrospective historical validation runs.

---

## Cities Covered (13)

Karachi · Lahore · Islamabad · Peshawar · Quetta · Multan · Faisalabad · Hyderabad · Sukkur · Larkana · Jacobabad · Sibi · Jamshoro

Jacobabad and Sibi are among the hottest cities on earth by peak WBGT and regularly approach theoretical human survival limits.

---

## Project Structure

```text
heatguard/
├── dashboard/
│   └── app.py                     # Streamlit web interface
├── scripts/
│   ├── fetch_weather.py           # Open-Meteo API fetching (13 Pakistani cities)
│   ├── wbgt_calculator.py         # Stull (2011) WBGT calculation & ISO 7243 weighting
│   ├── occupation_classifier.py   # 24 profile thresholds, NIOSH schedules, OMGI
│   ├── threshold_check.py         # Profile threshold & NIOSH formula verification
│   ├── sustained_exposure.py      # Multi-day exposure run analysis script
│   └── guidance_generator.py      # Gemini structured JSON bilingual guidance engine
└── data/
    └── karachi_2015_heatwave.csv  # Historical ERA5 meteorological dataset (192 records)

```

---

## Run Locally

```bash
git clone [https://github.com/sshizashah13/heatguard.git](https://github.com/sshizashah13/heatguard.git)
cd heatguard
pip install -r requirements.txt
streamlit run dashboard/app.py

```

Add a `.env` file in the root directory with your Gemini API key:

```env
GEMINI_API_KEY=your_key_here

```

---

## References

* Stull, R. (2011). Wet-Bulb Temperature from Relative Humidity and Air Temperature. *Journal of Applied Meteorology and Climatology*, 50(11), 2267–2269.
* NIOSH (2016). *Criteria for a Recommended Standard: Occupational Exposure to Heat and Hot Environments*. DHHS (NIOSH) Publication No. 2016-106.
* ISO 7243:2017. *Ergonomics of the thermal environment — Assessment of heat stress using the WBGT (Wet Bulb Globe Temperature) index*.
* Chaudhry, Q. Z., et al. (2015). *Technical Report on Karachi Heat Wave June 2015*. Ministry of Climate Change, Government of Pakistan.
* WHO–WMO Joint Programme (2026). El Niño declared significant public health threat. *Dawn*, September 22, 2026.

---

## Conference

Submitted to the **1st International Conference on Smart Sustainable Infrastructure for Circular Economy and Resource Efficiency (SINCERE-CON 2027)** — MUET Jamshoro

**Author:** Shiza Shah · Department of Computer Science · MUET Jamshoro

**GitHub:** [github.com/sshizashah13/heatguard](https://github.com/sshizashah13/heatguard)


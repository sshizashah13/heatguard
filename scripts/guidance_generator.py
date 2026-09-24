from google import genai
from google.genai import types
import os
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

MODEL = 'models/gemini-3.6-flash'

OCCUPATION_CONTEXT = {
    'Construction Laborer': 'carrying heavy materials, working with cement and metal rods under direct sun on concrete surfaces',
    'Rickshaw Driver': 'pedaling continuously in stop-and-go traffic with no shade, body heat plus sun exposure',
    'Truck Driver': 'sitting in a hot metal cabin, loading and unloading cargo in open yards',
    'Road Paver / Asphalt Layer': 'working directly over hot tar and asphalt that reaches 70C surface temperature',
    'Street Vendor (Rehri Wala)': 'standing on hot pavement all day pushing a cart with no shade or rest area',
    'Motorcycle Delivery Rider': 'riding continuously in direct sun, making repeated stops with engine heat below',
    'Fruit & Vegetable Seller (Sabzi Mandi)': 'standing in open market lifting heavy crates of produce on concrete since dawn',
    'Shoe Shiner / Mochi': 'crouching at ground level on hot pavement where temperatures are 5-8C hotter than standing height',
    'Scrap Collector (Kabari Wala)': 'walking 10-15km pushing a heavy metal cart in direct sun with no breaks',
    'Agricultural Worker': 'bending repeatedly in open fields with no shade, full solar exposure on back and neck',
    'Cotton Picker': 'bending for hours in cotton fields during Sindh peak season, same season as peak heat',
    'Fisherman (Machera)': 'working on open water where sun reflects from below and above, doubling radiation exposure',
    'Salt Pan Worker': 'working on white salt flats that reflect 80% of sunlight, radiation hits from sky AND ground',
    'Sanitation / Garbage Collector': 'handling waste bags in direct sun, walking long distances with heavy loads',
    'Street Sweeper': 'sweeping asphalt roads where ground temperature is 20C hotter than air temperature',
    'Open Drain Cleaner (Naali Safai Wala)': 'crouching in open drains where heat and toxic gases are both trapped',
    'Sewage / Manhole Worker': 'working inside manholes where heat is trapped and there is no airflow',
    'Brick Kiln Worker (Bhatta Mazdoor)': 'working next to a kiln firing at over 1000C, carrying heavy wet bricks',
    'Tandoor Baker (Naan Maker)': 'standing over a clay tandoor oven at 400C for 8-10 hours straight',
    'Textile Mill Worker': 'working in a room full of machines generating heat and steam with poor ventilation',
    'Glass Factory Worker': 'working near molten glass at 1400C, extreme radiant heat even 10 feet away',
    'Steel / Glass Furnace Worker': 'standing in front of furnaces exceeding 1500C, the most extreme heat exposure of any occupation',
    'Cement Factory Worker': 'loading and unloading cement bags in outdoor yards, dust and heat combined',
    'Ice Factory Worker': 'moving between freezing cold storage and 45C loading docks repeatedly, thermal shock risk',
}

ACTIONABLE_INTERVENTIONS = {
    'EXTREME': {
        'outdoor': 'Stop all work. Move to shade or any indoor space immediately. Drink water now.',
        'indoor_radiant': 'Step away from heat source immediately. Go outside to cooler air. Do not return for 45 minutes.',
        'vehicle': 'Pull over in shade. Turn off engine. Get out of vehicle. Drink water immediately.',
    },
    'HIGH': {
        'outdoor': 'Find shade for 30 minutes every hour. Drink at least 1 litre of water per hour.',
        'indoor_radiant': 'Take a 25-minute break away from heat source every hour. Drink water continuously.',
        'vehicle': 'Stop in shade every 40 minutes. Get out of vehicle. Drink water.',
    },
    'MODERATE': {
        'outdoor': 'Rest in shade for 15 minutes every hour. Keep drinking water every 20 minutes.',
        'indoor_radiant': 'Take short breaks every 50 minutes. Stay hydrated.',
        'vehicle': 'Stop every 50 minutes. Step out briefly. Drink water.',
    }
}

def get_worker_category(occupation_label):
    indoor_radiant = ['Brick Kiln', 'Tandoor', 'Glass Factory', 'Steel', 'Furnace', 'Textile']
    vehicle = ['Driver', 'Rider']
    for term in indoor_radiant:
        if term in occupation_label:
            return 'indoor_radiant'
    for term in vehicle:
        if term in occupation_label:
            return 'vehicle'
    return 'outdoor'

def generate_guidance(occupation_label, risk_level, wbgt, hour_of_day):
    time_context = (
        "very early morning (pre-dawn work)" if hour_of_day < 6
        else "early morning" if hour_of_day < 9
        else "late morning" if hour_of_day < 12
        else "early afternoon (peak heat)" if hour_of_day < 15
        else "late afternoon" if hour_of_day < 18
        else "evening"
    )

    worker_context = OCCUPATION_CONTEXT.get(occupation_label, 'working outdoors in direct heat')
    category = get_worker_category(occupation_label)
    intervention = ACTIONABLE_INTERVENTIONS.get(risk_level, {}).get(category, '')

    if risk_level == 'EXTREME':
        symptom_context = "stopped sweating despite extreme heat, confusion, dizziness, or skin that feels dry and very hot"
    elif risk_level == 'HIGH':
        symptom_context = "heavy headache, feeling very weak, or heart beating unusually fast"
    else:
        symptom_context = "mild headache, feeling thirsty, or slight dizziness"

    prompt = f"""You are a heat safety expert advising informal workers in Pakistan.
Your guidance must be life-saving, specific, and immediately actionable.

WORKER SITUATION:
- Occupation: {occupation_label}
- What they are doing: {worker_context}
- Heat stress (WBGT): {wbgt:.1f} degrees Celsius
- Risk level: {risk_level}
- Time: {time_context}
- Recommended action: {intervention}
- Warning symptoms to mention: {symptom_context}

CRITICAL RULES:
1. English must sound like a concerned friend texting, not a doctor
2. Roman Urdu must sound natural to a Karachi/Sindh worker, not translated English
3. Mention their SPECIFIC work tool or situation (tandoor, rehri, asphalt, etc.)
4. If EXTREME: Roman Urdu section must start with KAAM BAND KARO FORAN
5. Give EXACT minutes for work/rest, not vague advice
6. Warning sign must be a body feeling they will recognise, not a medical term
7. Maximum 3 bullet points per language, no more
8. Roman Urdu must use Karachi street language: yaar, bhai, foran, abhi, bilkul nahi

OUTPUT FORMAT (use exactly this, no extra text before or after):
ENGLISH:
- Right now: [specific action mentioning their actual work]
- You have: [X minutes safe OR STOP IMMEDIATELY]
- Watch for: [specific body feeling in plain words]

ROMAN URDU:
- Abhi karo: [natural Urdu, not translated English]
- Aur kitna kaam: [how many minutes of work left, in natural Urdu]
- Khabardar: [one body feeling in plain Karachi street Urdu]"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=400,
            top_p=0.8,
        )
    )

    try:
        return response.text.strip()
    except Exception:
        if risk_level == 'EXTREME':
            return (
                "ENGLISH:\n"
                "• Right now: Stop work immediately and move to shade\n"
                "• You have: STOP IMMEDIATELY\n"
                "• Watch for: If you stop sweating or feel confused, call for help now\n\n"
                "ROMAN URDU:\n"
                "• Abhi karo: KAAM BAND KARO FORAN, chaon mein jao\n"
                "• Aur kitna kaam: Bilkul kaam nahi, abhi ruko\n"
                "• Khabardar: Agar pasina band ho jaye ya chakkar aaye, foran madad lo"
            )
        return "Guidance temporarily unavailable. Stay hydrated and rest in shade."


def generate_all_sample_guidance():
    from occupation_classifier import OCCUPATION_PROFILES

    test_cases = [
        ('steel_furnace_worker', 'EXTREME', 33.7, 15),
        ('salt_pan_worker', 'EXTREME', 33.7, 13),
        ('tandoor_baker', 'EXTREME', 33.7, 16),
        ('sewage_worker', 'EXTREME', 33.7, 10),
        ('road_paver', 'EXTREME', 33.7, 14),
        ('construction_laborer', 'HIGH', 30.5, 11),
        ('cotton_picker', 'HIGH', 29.8, 12),
        ('rickshaw_driver', 'MODERATE', 27.5, 9),
        ('truck_driver', 'MODERATE', 28.0, 14),
        ('fisherman', 'HIGH', 30.5, 9),
        ('kabari_wala', 'HIGH', 31.0, 13),
        ('naali_safai', 'EXTREME', 33.7, 10),
    ]

    results = []
    print("=" * 65)
    print("HEATGUARD — BILINGUAL GUIDANCE SAMPLES")
    print("=" * 65)

    for occ_key, risk, wbgt, hour in test_cases:
        label = OCCUPATION_PROFILES[occ_key]['label']
        category = get_worker_category(label)
        risk_symbol = '🔴' if risk == 'EXTREME' else '🟠' if risk == 'HIGH' else '🟡'

        print(f"\n{risk_symbol} {label}")
        print(f"   Risk: {risk} | WBGT: {wbgt}C | Time: {hour}:00 | Type: {category}")
        print("-" * 65)

        try:
            guidance = generate_guidance(label, risk, wbgt, hour)
        except Exception as e:
            print(f"   ⚠️ Error, retrying in 10 seconds... ({e})")
            time.sleep(10)
            try:
                guidance = generate_guidance(label, risk, wbgt, hour)
            except Exception:
                guidance = "Retry failed — skipping this entry"

        print(guidance)
        print("-" * 65)

        results.append({
            'occupation': label,
            'worker_category': category,
            'risk_level': risk,
            'wbgt_celsius': wbgt,
            'hour': hour,
            'guidance_english_urdu': guidance
        })

        time.sleep(5)  # prevents server overload

    df = pd.DataFrame(results)
    df.to_csv('data/sample_guidance_outputs.csv', index=False)
    print(f"\n✅ {len(results)} guidance samples saved to data/sample_guidance_outputs.csv")
    print("📸 Screenshot this entire output for your paper documentation")
    return results


def test_single():
    print("Testing Gemini API with new google-genai library...\n")
    result = generate_guidance("Tandoor Baker (Naan Maker)", "EXTREME", 33.7, 16)
    print(result)
    print("\n✅ Gemini API working correctly!")


if __name__ == '__main__':
    test_single()
    print("\n" + "=" * 65)
    print("Generating full sample set for documentation...")
    print("=" * 65 + "\n")
    generate_all_sample_guidance()
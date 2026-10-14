import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.occupation_classifier import OCCUPATION_PROFILES

print(f"{'Occupation':<44}{'M(W)':>6}{'RAL':>7}{'REL':>7}{'MOD':>5}{'HIGH':>6}{'EXT':>5}")
for key, p in OCCUPATION_PROFILES.items():
    m = p['metabolic_rate_W']
    ral = 59.9 - 14.1 * math.log10(m)
    rel = 56.7 - 11.5 * math.log10(m)
    t = p['thresholds']
    print(f"{p['label']:<44}{m:>6}{ral:>7.1f}{rel:>7.1f}{t['moderate']:>5}{t['high']:>6}{t['extreme']:>5}")
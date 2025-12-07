import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.data.repository import RoVRepository
from app.config import DB_PATH

repo = RoVRepository(DB_PATH)
items = repo.get_all_items()

# หาไอเทมที่ถูกเลือกบ่อย
print("=" * 60)
print("🔍 วิเคราะห์ไอเทมที่ระบบเลือกบ่อย")
print("=" * 60)

target_items = ['Fafnir', 'Staff of Nuul', 'Uriel']

for target in target_items:
    matching = [i for id, i in items.items() if target in i['name_en']]
    if matching:
        item = matching[0]
        print(f"\n📦 {item['name_en']} (Price: {item.get('price', 0)}g)")
        print(f"   Class: {item.get('class', 'N/A')}")
        print("   Stats:")
        print(f"     • P.ATK: {item.get('p_atk', 0)}")
        print(f"     • M.Power: {item.get('m_power', 0)}")
        print(f"     • Max HP: {item.get('max_hp', 0)}")
        print(f"     • ASPD: {item.get('aspd', 0)}%")
        print(f"     • CDR: {item.get('cdr', 0)}%")
        print(f"     • Crit Rate: {item.get('crit_rate', 0)}%")
        print(f"     • P.Pierce: {item.get('p_pierce_percent', 0)}%")
        print(f"     • M.Pierce: {item.get('m_pierce_percent', 0)}%")

print("\n" + "=" * 60)
print("📊 Learned Weights Summary")
print("=" * 60)

import json
weights_path = os.path.join(PROJECT_ROOT, 'app', 'core', 'learned_weights.json')
with open(weights_path) as f:
    weights = json.load(f)

sorted_weights = sorted(weights.items(), key=lambda x: abs(x[1]), reverse=True)

print("\nTop 5 Most Important Stats:")
for i, (stat, weight) in enumerate(sorted_weights[:5], 1):
    sign = "✅" if weight > 0 else "❌"
    print(f"{i}. {sign} {stat:<20}: {weight:>10.4f}")

print("\nBottom 5 Least Important Stats:")
for i, (stat, weight) in enumerate(sorted_weights[-5:], 1):
    sign = "✅" if weight > 0 else "❌"
    print(f"{i}. {sign} {stat:<20}: {weight:>10.4f}")

"""
สคริปต์ทดสอบระบบแนะนำไอเทมกับหลายๆ ฮีโร่
เพื่อวิเคราะห์คุณภาพของ learned weights
"""
import sys
import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.data.repository import RoVRepository
from app.config import DB_PATH
import sqlite3

# ดึง sample heroes แต่ละ role
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT code_name, name_th, primary_role, damage_type 
    FROM heroes 
    WHERE primary_role IN ('Mage', 'Marksman', 'Assassin', 'Tank', 'Fighter')
    GROUP BY primary_role
    LIMIT 10
""")
heroes = cursor.fetchall()
conn.close()

print("=" * 60)
print("🧪 ทดสอบระบบแนะนำไอเทมอัตโนมัติ")
print("=" * 60)
print("\nฮีโร่ที่จะทดสอบ:")
for h in heroes:
    print(f"  • {h[0]:<15} ({h[1]:<15}) - {h[2]:<10} [{h[3]}]")

print("\n" + "=" * 60)
print("เริ่มทดสอบ...\n")

results = []

for code_name, name_th, role, dmg_type in heroes:
    print(f"\n{'='*60}")
    print(f"🎮 Testing: {name_th} ({role})")
    print('='*60)
    
    # รันคำสั่ง
    result = subprocess.run(
        ['python', '-m', 'app.main', code_name],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    print(result.stdout)
    
    # เก็บผลลัพธ์
    results.append({
        'hero': name_th,
        'role': role,
        'damage_type': dmg_type,
        'output': result.stdout
    })

print("\n" + "=" * 60)
print("📊 สรุปผลการทดสอบ")
print("=" * 60)

# วิเคราะห์ build ที่ได้
for r in results:
    print(f"\n{r['hero']} ({r['role']} - {r['damage_type']}):")
    lines = r['output'].split('\n')
    
    # หา fitness score
    for line in lines:
        if 'Fitness Score' in line:
            print(f"  ⭐ {line.strip()}")
    
    # หา items
    items = []
    for line in lines:
        if line.strip().startswith('['):
            items.append(line.strip())
    
    if items:
        print(f"  🎒 Items: {len(items)} ชิ้น")
        # นับไอเทมที่ซ้ำ
        from collections import Counter
        item_names = [i.split(']')[1].split('(')[0].strip() for i in items]
        counts = Counter(item_names)
        for item, count in counts.most_common(3):
            print(f"     - {item}: {count}x")

print("\n" + "=" * 60)
print("✅ การทดสอบเสร็จสิ้น!")
print("=" * 60)

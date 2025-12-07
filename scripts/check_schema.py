import sqlite3
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Check heroes table data sample
print("=== Sample Hero Data ===")
print("=" * 80)
cursor = conn.cursor()
cursor.execute("SELECT * FROM heroes LIMIT 3")
rows = cursor.fetchall()
for row in rows:
    print(f"Hero: {row['code_name']}")
    print(f"  Name: {row['name_th']}")
    print(f"  Primary Role: {row['primary_role']}")
    print(f"  Secondary Role: {row['secondary_role']}")
    print(f"  Primary Lane: {row['primary_lane']}")
    print(f"  Secondary Lane: {row['secondary_lane']}")
    print(f"  Damage Type: {row['damage_type']}")
    print()

# Check unique roles and lanes
print("\n=== All Unique Roles ===")
cursor.execute("SELECT DISTINCT primary_role FROM heroes WHERE primary_role IS NOT NULL")
roles = [r[0] for r in cursor.fetchall()]
print(f"Primary Roles: {roles}")

cursor.execute("SELECT DISTINCT secondary_role FROM heroes WHERE secondary_role IS NOT NULL")
sec_roles = [r[0] for r in cursor.fetchall()]
print(f"Secondary Roles: {sec_roles}")

print("\n=== All Unique Lanes ===")
cursor.execute("SELECT DISTINCT primary_lane FROM heroes WHERE primary_lane IS NOT NULL")
lanes = [r[0] for r in cursor.fetchall()]
print(f"Primary Lanes: {lanes}")

cursor.execute("SELECT DISTINCT secondary_lane FROM heroes WHERE secondary_lane IS NOT NULL")
sec_lanes = [r[0] for r in cursor.fetchall()]
print(f"Secondary Lanes: {sec_lanes}")

conn.close()


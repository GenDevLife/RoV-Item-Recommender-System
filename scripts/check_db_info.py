import sqlite3
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

# Sample heroes
print("=" * 80)
print("SAMPLE HEROES")
print("=" * 80)
cursor.execute("SELECT * FROM heroes LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(f"\nHero: {row['code_name']}")
    print(f"  Name: {row['name_th']}")
    print(f"  Primary Role: {row['primary_role']}")
    print(f"  Secondary Role: {row['secondary_role']}")
    print(f"  Primary Lane: {row['primary_lane']}")
    print(f"  Secondary Lane: {row['secondary_lane']}")
    print(f"  Damage Type: {row['damage_type']}")

# Unique roles
print("\n" + "=" * 80)
print("UNIQUE ROLES")
print("=" * 80)
cursor.execute("SELECT DISTINCT primary_role FROM heroes WHERE primary_role IS NOT NULL ORDER BY primary_role")
print("Primary Roles:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.execute("SELECT DISTINCT secondary_role FROM heroes WHERE secondary_role IS NOT NULL ORDER BY secondary_role")
print("\nSecondary Roles:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

# Unique lanes
print("\n" + "=" * 80)
print("UNIQUE LANES")
print("=" * 80)
cursor.execute("SELECT DISTINCT primary_lane FROM heroes WHERE primary_lane IS NOT NULL ORDER BY primary_lane")
print("Primary Lanes:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.execute("SELECT DISTINCT secondary_lane FROM heroes WHERE secondary_lane IS NOT NULL ORDER BY secondary_lane")
print("\nSecondary Lanes:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()

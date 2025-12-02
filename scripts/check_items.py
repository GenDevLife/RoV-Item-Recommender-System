import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.data.repository import RoVRepository
from app.config import DB_PATH

repo = RoVRepository(DB_PATH)
items = repo.get_all_items()

print(f"Total items in database: {len(items)}")
print("\n=== Sample items ===")
for i, (item_id, data) in enumerate(list(items.items())[:5]):
    print(f"ID: {item_id}, Code: {data.get('item_code')}, Name: {data.get('name_en')}")

print("\n=== Checking I085 ===")
found = False
for item_id, data in items.items():
    if data.get('item_code') == 'I085':
        print(f"Found! ID={item_id}, Name={data.get('name_en')}")
        print(f"Stats: p_atk={data.get('p_atk')}, m_power={data.get('m_power')}")
        found = True
        break

if not found:
    print("I085 NOT FOUND in database!")
    print("\nAvailable item codes (first 10):")
    codes = [data.get('item_code') for _, data in list(items.items())[:10]]
    print(codes)

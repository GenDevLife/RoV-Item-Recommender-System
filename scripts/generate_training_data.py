import sys
import os
import random
import pandas as pd
import numpy as np

# ==========================================
# Setup Paths
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.config import DB_PATH
from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator

# ==========================================
# Configuration
# ==========================================
OUTPUT_CSV = os.path.join(PROJECT_ROOT, 'data', 'raw', 'synthetic_training_data.csv')
NUM_BUILDS = 2000  # จำนวน builds ที่จะสร้าง
NOISE_LEVEL = 0.05  # 5% noise เพื่อจำลอง real-world variance

# Ground Truth Weights (ค่าจริงที่เราต้องการให้ model เรียนรู้)
# ค่าเหล่านี้ based on domain knowledge ของเกม RoV
TRUE_WEIGHTS = {
    'p_atk': 0.15,
    'm_power': 0.15,
    'max_hp': 0.001,
    'p_def': 0.01,
    'm_def': 0.01,
    'cdr': 0.20,
    'aspd': 0.50,
    'crit_rate': 0.80,
    'p_pierce_percent': 1.20,
    'm_pierce_percent': 1.20,
    'move_speed': 0.10
}

# ==========================================
# Helper Functions
# ==========================================
def calculate_true_score(stats, weights):
    """คำนวณ score ที่แท้จริงจาก stats และ weights"""
    score = 0.0
    for stat_name, weight in weights.items():
        score += stats.get(stat_name, 0.0) * weight
    return score

def add_noise(value, noise_level):
    """เพิ่ม Gaussian noise เพื่อจำลอง variance จริง"""
    noise = np.random.normal(0, noise_level * value)
    return max(0, value + noise)  # ไม่ให้ติดลบ

def generate_random_build(all_items, num_items=6):
    """สุ่ม build แบบหลากหลาย"""
    # เลือกไอเทมแบบสุ่ม (ไม่ซ้ำกัน)
    item_ids = list(all_items.keys())
    
    # สุ่มจำนวนไอเทม 4-6 ชิ้น (บางทีไม่เต็ม 6)
    actual_num_items = random.randint(4, num_items)
    selected_items = random.sample(item_ids, actual_num_items)
    
    return selected_items

def format_item_code(item_id, all_items):
    """แปลง item_id เป็น item_code"""
    return all_items.get(item_id, {}).get('item_code', '')

# ==========================================
# Main Generator
# ==========================================
def generate_synthetic_data():
    print("🚀 Starting Synthetic Training Data Generation...")
    
    # 1. Initialize System
    try:
        repo = RoVRepository(DB_PATH)
        all_items = repo.get_all_items()
        
        print(f"📦 Loaded {len(all_items)} items")
        
        # สร้าง dummy hero สำหรับคำนวณ stats
        dummy_hero = {
            'hero_id': 'H001',
            'base_atk': 165,
            'base_def': 85,
            'base_hp': 3200,
            'damage_type': 'Physical',
            'class_name': 'Warrior'
        }
        
        evaluator = BuildEvaluator(dummy_hero, all_items)
        
    except Exception as e:
        print(f"❌ System Init Error: {e}")
        return
    
    # 2. Generate Random Builds
    print(f"🎲 Generating {NUM_BUILDS} random builds...")
    
    data_records = []
    
    for i in range(NUM_BUILDS):
        # สุ่ม build
        build_ids = generate_random_build(all_items)
        
        # คำนวณ stats
        stats = evaluator.calculate_stats(build_ids)
        
        # คำนวณ true score (ground truth)
        true_score = calculate_true_score(stats, TRUE_WEIGHTS)
        
        # เพิ่ม noise เพื่อสมจริงขึ้น
        noisy_score = add_noise(true_score, NOISE_LEVEL)
        
        # สร้าง record
        record = {
            'HeroID': dummy_hero['hero_id'],
            'Class': dummy_hero.get('class_name', 'Unknown'),
            'Lane': 'Mid',  # Placeholder
        }
        
        # เพิ่ม items (pad ด้วย empty string ถ้าไม่ครบ 6)
        for j in range(6):
            if j < len(build_ids):
                record[f'Item{j+1}'] = format_item_code(build_ids[j], all_items)
            else:
                record[f'Item{j+1}'] = ''
        
        record['TrueScore'] = round(true_score, 2)
        record['NoisyScore'] = round(noisy_score, 2)
        
        data_records.append(record)
        
        # แสดง progress
        if (i + 1) % 500 == 0:
            print(f"  ✓ Generated {i + 1}/{NUM_BUILDS} builds")
    
    # 3. Create DataFrame and Save
    df = pd.DataFrame(data_records)
    
    # เพิ่มคอลัมน์ CombatPower (alias for NoisyScore)
    df['CombatPower'] = df['NoisyScore']
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  - Total Builds: {len(df)}")
    print(f"  - Score Range: {df['NoisyScore'].min():.2f} - {df['NoisyScore'].max():.2f}")
    print(f"  - Score Mean: {df['NoisyScore'].mean():.2f}")
    print(f"  - Score Std: {df['NoisyScore'].std():.2f}")
    
    # บันทึก CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n💾 Saved to: {OUTPUT_CSV}")
    
    # แสดงตัวอย่าง
    print("\n📋 Sample Data (first 5 rows):")
    print(df.head())
    
    print("\n✅ Synthetic Data Generation Complete!")
    print(f"\n💡 Next Step: Run calibration with this data:")
    print(f"   python scripts/calibrate.py --use-synthetic")

if __name__ == "__main__":
    # ตั้ง random seed เพื่อให้ reproducible
    random.seed(42)
    np.random.seed(42)
    
    generate_synthetic_data()

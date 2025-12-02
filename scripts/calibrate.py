import sys
import os
import json
import pandas as pd
import numpy as np

# ==========================================
# 1. Setup Paths
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.config import DB_PATH
from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator

# Config Files
CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'test_fitness.csv')
OUTPUT_WEIGHTS_PATH = os.path.join(PROJECT_ROOT, 'app', 'core', 'learned_weights.json')

# Features ที่เราสนใจ (ต้องตรงกับ keys ใน calculate_stats ของ evaluator)
FEATURE_NAMES = [
    'p_atk', 'm_power', 'max_hp', 'p_def', 'm_def',
    'cdr', 'aspd', 'crit_rate', 'p_pierce_percent', 'm_pierce_percent', 'move_speed'
]

# ==========================================
# 2. Helper Functions
# ==========================================
def load_data(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ Training data not found at: {csv_path}")
    return pd.read_csv(csv_path)

def extract_features(row, evaluator, all_items):
    """แปลงข้อมูล 1 แถวเป็น Feature Array"""
    build_ids = []
    for i in range(1, 7):
        item_val = row.get(f'Item{i}')
        found_id = None
        
        # Logic การหา ID ไอเทม
        if pd.notna(item_val):
            item_code = str(item_val).strip()
            # Match by item_code (I001, I002, ...)
            for iid, data in all_items.items():
                if data.get('item_code') == item_code:
                    found_id = iid
                    break
        
        if found_id and found_id in all_items:
            build_ids.append(found_id)

    # คำนวณ Stat รวม
    stats = evaluator.calculate_stats(build_ids)
    
    # เรียงลำดับค่าตาม FEATURE_NAMES
    return [stats.get(k, 0.0) for k in FEATURE_NAMES]

# ==========================================
# 3. Math & Algorithms
# ==========================================
def ridge_regression(X, y, alpha=1.0):
    """
    คำนวณ Ridge Regression: w = (X^T X + alpha*I)^-1 X^T y
    ช่วยลดปัญหา Multicollinearity (Stat สัมพันธ์กันเอง)
    """
    n_features = X.shape[1]
    I = np.eye(n_features)
    # ป้องกัน Bias (column สุดท้าย) โดน Penalize
    I[-1, -1] = 0 
    
    # w = inv(X'X + aI) * X'y
    weights = np.linalg.inv(X.T @ X + alpha * I) @ X.T @ y
    return weights

def run_calibration():
    print("🚀 Starting Advanced Calibration...")
    
    # 1. Init System
    try:
        repo = RoVRepository(DB_PATH)
        all_items = repo.get_all_items()
        dummy_hero = {'base_atk': 0, 'base_def': 0, 'base_hp': 0, 'damage_type': 'Physical'}
        evaluator = BuildEvaluator(dummy_hero, all_items)
    except Exception as e:
        print(f"❌ System Init Error: {e}")
        return

    # 2. Load & Prepare Data
    try:
        df = load_data(CSV_PATH)
        print(f"📥 Loaded {len(df)} records.")
        
        X_raw = []
        y = []
        
        for _, row in df.iterrows():
            feats = extract_features(row, evaluator, all_items)
            X_raw.append(feats)
            y.append(row['WinRate'])
            
        X_raw = np.array(X_raw)
        y = np.array(y)
        
        # --- Step 3: Standardization (Normalize Data) ---
        # ทำให้ทุก Stat มีหน่วยเป็น "Standard Deviation" (ค่าเฉลี่ย 0, ความกว้าง 1)
        # เพื่อให้ OLS/Ridge เปรียบเทียบความสำคัญได้จริง
        mean = np.mean(X_raw, axis=0)
        std = np.std(X_raw, axis=0)
        
        # ป้องกันการหารด้วย 0 (กรณี Stat บางตัวเท่ากันหมดทั้งไฟล์)
        std[std == 0] = 1.0 
        
        X_norm = (X_raw - mean) / std
        
        # Add Bias Column (Intercept)
        ones = np.ones((X_norm.shape[0], 1))
        X_final = np.hstack([X_norm, ones])
        
    except Exception as e:
        print(f"❌ Data Error: {e}")
        import traceback; traceback.print_exc()
        return

    # 4. Train Model (Ridge Regression)
    print("🧮 Calculating Weights (Ridge Regression)...")
    try:
        # Alpha คือความแรงในการลด overfitting (ปรับได้ 0.1 - 10.0)
        weights_norm = ridge_regression(X_final, y, alpha=2.0)
        
        # 5. Analyze & Un-normalize
        # เราได้ Weight ของข้อมูล Norm มาแล้ว แต่ Evaluator เราใช้ข้อมูลดิบ
        # ต้องแปลงกลับ: w_raw = w_norm / std
        
        final_weights_raw = {}
        
        print("\n=== 📊 Feature Importance (Normalized) ===")
        print("*(ค่านี้บอกว่า Stat ไหนส่งผลต่อการชนะมากที่สุด)*")
        print("-" * 40)
        
        w_feats_norm = weights_norm[:-1] # ตัด Bias ออก
        
        # จับคู่ชื่อกับค่า
        feature_importance = list(zip(FEATURE_NAMES, w_feats_norm, std))
        # เรียงตามความสำคัญ (มากไปน้อย)
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        for name, w_norm, s in feature_importance:
            # แปลงกลับเป็น Raw Weight
            w_raw = w_norm / s
            final_weights_raw[name] = float(w_raw)
            
            # แสดงผล (โชว์ค่า Norm เพื่อดูความสำคัญ, โชว์ค่า Raw เพื่อดูค่าจริง)
            print(f"{name:<20} | Importance: {w_norm:>7.4f} | Raw Weight: {w_raw:>10.6f}")

        # Bias Calculation (ซับซ้อนหน่อยเมื่อ Un-normalize แต่เราอาจไม่ใช้ใน GA)
        bias_norm = weights_norm[-1]
        # bias_raw = bias_norm - sum((w_norm * mean) / std)
        
        # 6. Save
        with open(OUTPUT_WEIGHTS_PATH, 'w') as f:
            json.dump(final_weights_raw, f, indent=4)
            
        print("-" * 40)
        print(f"💾 Saved optimized weights to: {OUTPUT_WEIGHTS_PATH}")
        print("✅ Calibration Complete! Run 'python -m app.main' to test recommendations.")

    except Exception as e:
        print(f"❌ Calculation Error: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    run_calibration()
import sys
import os
import json
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

# ==========================================
# 1. Setup Paths
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.config import DB_PATH
from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator

# Config Files
SYNTHETIC_CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'synthetic_training_data.csv')
REAL_CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'test_fitness.csv')
OUTPUT_WEIGHTS_PATH = os.path.join(PROJECT_ROOT, 'app', 'core', 'learned_weights.json')

# Check command line arguments for data source
USE_SYNTHETIC = '--use-synthetic' in sys.argv or '--synthetic' in sys.argv
CSV_PATH = SYNTHETIC_CSV_PATH if USE_SYNTHETIC else REAL_CSV_PATH
TARGET_COLUMN = 'NoisyScore' if USE_SYNTHETIC else 'CombatPower'

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
# 3. Main Calibration Function
# ==========================================
def run_calibration():
    data_source = "Synthetic Data" if USE_SYNTHETIC else "Real Data"
    print(f"🚀 Starting Advanced Calibration with scikit-learn Ridge Regression...")
    print(f"📂 Data Source: {data_source} ({CSV_PATH})")
    print(f"🎯 Target Column: {TARGET_COLUMN}")
    
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
            y.append(row[TARGET_COLUMN])
            
        X_raw = np.array(X_raw)
        y = np.array(y)
        
        # --- Step 3: Standardization using StandardScaler ---
        # ทำให้ทุก Stat มีค่าเฉลี่ย 0 และ Variance 1 (Z-score normalization)
        # เพื่อให้ Ridge Regression เปรียบเทียบความสำคัญได้จริง
        print("📐 Applying StandardScaler for data normalization...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_raw)
        
    except Exception as e:
        print(f"❌ Data Error: {e}")
        import traceback; traceback.print_exc()
        return

    # 4. Train Model (Ridge Regression using sklearn)
    print("🧮 Training Ridge Regression Model...")
    try:
        # Alpha (regularization strength) คือความแรงในการลด overfitting
        # ค่าที่แนะนำ: 0.1-10.0 (ยิ่งสูง = ยิ่ง regularize มาก)
        alpha = 1.0
        
        ridge_model = Ridge(alpha=alpha, fit_intercept=True)
        ridge_model.fit(X_scaled, y)
        
        # 5. Extract Coefficients
        # model.coef_ ให้ coefficients สำหรับ scaled data
        # model.intercept_ ให้ bias term
        coefficients_scaled = ridge_model.coef_
        intercept = ridge_model.intercept_
        
        # 6. Un-normalize Coefficients
        # เนื่องจาก Evaluator ใช้ข้อมูลดิบ เราต้องแปลง coefficients กลับ
        # w_raw = w_scaled / scale (where scale = std)
        final_weights_raw = {}
        
        print(f"\n=== 📊 Ridge Regression Results (alpha={alpha}) ===")
        print("Feature Importance & Raw Weights")
        print("-" * 70)
        print(f"{'Feature Name':<20} | {'Coefficient':<12} | {'Raw Weight':<15}")
        print("-" * 70)
        
        # จับคู่ชื่อกับ coefficients และ unscale
        feature_importance = []
        for i, name in enumerate(FEATURE_NAMES):
            coef_scaled = coefficients_scaled[i]
            # Un-normalize: w_raw = w_scaled / std
            w_raw = coef_scaled / scaler.scale_[i]
            final_weights_raw[name] = float(w_raw)
            feature_importance.append((name, coef_scaled, w_raw))
        
        # เรียงตามความสำคัญ (absolute value ของ coefficient)
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        for name, coef, w_raw in feature_importance:
            print(f"{name:<20} | {coef:>11.6f} | {w_raw:>14.8f}")
        
        print("-" * 70)
        print(f"Intercept (bias): {intercept:.6f}")
        print("-" * 70)
        print("\n💡 Interpretation:")
        print("  - Coefficient: Feature importance on scaled data (comparable across features)")
        print("  - Raw Weight: Actual weight for use with raw stats in the Evaluator")
        print("  - Higher |coefficient| = more important feature for predicting win rate")
        
        # 7. Save Weights
        with open(OUTPUT_WEIGHTS_PATH, 'w') as f:
            json.dump(final_weights_raw, f, indent=4)
            
        print(f"\n💾 Saved optimized weights to: {OUTPUT_WEIGHTS_PATH}")
        print("✅ Calibration Complete! Run 'python -m app.main' to test recommendations.")

    except Exception as e:
        print(f"❌ Calculation Error: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    run_calibration()
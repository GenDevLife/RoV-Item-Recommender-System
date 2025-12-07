import sys
import os
import json
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

# ==========================================
# Setup Paths
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.config import DB_PATH
from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator

# Config
SYNTHETIC_CSV = os.path.join(PROJECT_ROOT, 'data', 'raw', 'synthetic_training_data.csv')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'app', 'core', 'learned_weights.json')

FEATURE_NAMES = [
    'p_atk', 'm_power', 'max_hp', 'p_def', 'm_def',
    'cdr', 'aspd', 'crit_rate', 'p_pierce_percent', 'm_pierce_percent', 'move_speed'
]

TRUE_WEIGHTS = {
    'p_atk': 0.15, 'm_power': 0.15, 'max_hp': 0.001, 'p_def': 0.01, 'm_def': 0.01,
    'cdr': 0.20, 'aspd': 0.50, 'crit_rate': 0.80, 'p_pierce_percent': 1.20,
    'm_pierce_percent': 1.20, 'move_speed': 0.10
}

def load_data(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ Data not found: {csv_path}")
    return pd.read_csv(csv_path)

def extract_features(row, evaluator, all_items):
    build_ids = []
    for i in range(1, 7):
        item_val = row.get(f'Item{i}')
        if pd.notna(item_val):
            item_code = str(item_val).strip()
            for iid, data in all_items.items():
                if data.get('item_code') == item_code:
                    build_ids.append(iid)
                    break
    stats = evaluator.calculate_stats(build_ids)
    return [stats.get(k, 0.0) for k in FEATURE_NAMES]

def calculate_weight_error(learned, true):
    """คำนวณ average error %"""
    total_error = 0
    for k, true_val in true.items():
        learned_val = learned.get(k, 0.0)
        error = abs(learned_val - true_val) / max(abs(true_val), 0.001) * 100
        total_error += error
    return total_error / len(true)

def tune_alpha():
    print("🔧 Starting Alpha Tuning for Ridge Regression...")
    
    # Load data
    try:
        repo = RoVRepository(DB_PATH)
        all_items = repo.get_all_items()
        dummy_hero = {'base_atk': 0, 'base_def': 0, 'base_hp': 0, 'damage_type': 'Physical'}
        evaluator = BuildEvaluator(dummy_hero, all_items)
    except Exception as e:
        print(f"❌ Init Error: {e}")
        return

    try:
        df = load_data(SYNTHETIC_CSV)
        print(f"📥 Loaded {len(df)} records")
        
        X_raw = []
        y = []
        for _, row in df.iterrows():
            feats = extract_features(row, evaluator, all_items)
            X_raw.append(feats)
            y.append(row['NoisyScore'])
        
        X_raw = np.array(X_raw)
        y = np.array(y)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_raw)
        
    except Exception as e:
        print(f"❌ Data Error: {e}")
        return

    # Test different alpha values
    alphas = [0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]
    
    print("\n" + "=" * 90)
    print(f"{'Alpha':>10} | {'CV Score':>10} | {'Avg Error %':>12} | {'Best Features':<40}")
    print("=" * 90)
    
    best_alpha = None
    best_error = float('inf')
    best_weights = None
    
    for alpha in alphas:
        # Train model
        ridge = Ridge(alpha=alpha, fit_intercept=True)
        ridge.fit(X_scaled, y)
        
        # Cross-validation score (R² score)
        cv_scores = cross_val_score(ridge, X_scaled, y, cv=5, scoring='r2')
        avg_cv_score = cv_scores.mean()
        
        # Extract weights
        learned_weights = {}
        for i, name in enumerate(FEATURE_NAMES):
            w_raw = ridge.coef_[i] / scaler.scale_[i]
            learned_weights[name] = float(w_raw)
        
        # Calculate error
        avg_error = calculate_weight_error(learned_weights, TRUE_WEIGHTS)
        
        # Find top 3 closest weights
        errors = {k: abs(learned_weights[k] - TRUE_WEIGHTS[k]) / max(abs(TRUE_WEIGHTS[k]), 0.001) * 100 
                  for k in TRUE_WEIGHTS.keys()}
        best_feats = sorted(errors.items(), key=lambda x: x[1])[:3]
        best_feat_str = ', '.join([f"{k}({v:.1f}%)" for k, v in best_feats])
        
        print(f"{alpha:>10.3f} | {avg_cv_score:>10.4f} | {avg_error:>11.2f}% | {best_feat_str:<40}")
        
        # Track best
        if avg_error < best_error:
            best_error = avg_error
            best_alpha = alpha
            best_weights = learned_weights
    
    print("=" * 90)
    print(f"\n🏆 BEST ALPHA: {best_alpha} (Average Error: {best_error:.2f}%)")
    
    # Save best weights
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(best_weights, f, indent=4)
    
    print(f"💾 Saved best weights to: {OUTPUT_PATH}")
    
    # Show detailed comparison
    print("\n" + "=" * 80)
    print("📊 DETAILED COMPARISON (Best Alpha)")
    print("=" * 80)
    print(f"{'Feature':<20} | {'True':>12} | {'Learned':>15} | {'Error %':>10}")
    print("-" * 80)
    
    for k, true_val in TRUE_WEIGHTS.items():
        learned_val = best_weights[k]
        error = abs(learned_val - true_val) / max(abs(true_val), 0.001) * 100
        print(f"{k:<20} | {true_val:>12.6f} | {learned_val:>15.8f} | {error:>9.2f}%")
    
    print("=" * 80)
    print("✅ Tuning Complete!")

if __name__ == "__main__":
    tune_alpha()

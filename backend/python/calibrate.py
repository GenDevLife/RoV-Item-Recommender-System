#!/usr/bin/env python3
# calibrate.py  (match main.py 2025-05-08)

import json, argparse
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

# ----- IMPORT จาก main.py -----
from main import (
    load_hero_stats, load_stat_caps,
    get_recommended_item_types, get_hero_info,
    stat_component, budget_component, skill_component,
    synergy_component, category_component, class_component, lane_component,
    get_phase_weight, BASE_BUDGET, item_data, _n
)
# ------------------------------

# ---------- config ----------
PHASE = "Late"     # Calibrate ตาม combat power late-game
RIDGE_ALPHA = 1.0  # Regularization strength
SYNERGY_BOOST = 5  # ขยายสัญญาณ synergy (ปรับได้)
# -----------------------------

COMPONENT_KEYS = [
    "stat", "budget", "skill", "synergy",
    "cat", "class", "lane",
    "cat_ATK", "cat_Def", "cat_Magic",  # cat_* 3 ค่าใน main.py
]

def build_feature_row(row):
    hero = row["HeroID"]; lane = row["Lane"]; build = [row[f"Item{i}"] for i in range(1,7)]

    hero_info = get_hero_info(hero)
    hero_info["lane"] = lane     # override ตาม csv
    caps  = load_stat_caps(hero)
    hb    = load_hero_stats(hero, {"Early":3,"Mid":9,"Late":15}[PHASE])
    rec   = get_recommended_item_types(hero)
    cat_val = len(build) 

    # ------- components (เหมือน main.py) -------
    features = {
        "stat":    stat_component(build, hb, caps, get_phase_weight(hero_info, PHASE)),
        "budget":  budget_component(sum(item_data[i]["Price"] for i in build), BASE_BUDGET[PHASE], PHASE),
        "skill":   skill_component(build, rec),
        "synergy": synergy_component(build) * SYNERGY_BOOST,  # boost
        "cat":     cat_val,
        "class":   class_component(build, hero_info),
        "lane":    lane_component(build, hero_info),
        "cat_ATK": sum(1 for i in build if item_data[i]["Class"] == "ATK"),
        "cat_Def": sum(1 for i in build if item_data[i]["Class"] == "Def"),
        "cat_Magic": sum(1 for i in build if item_data[i]["Class"] == "Magic"),
    }
    return [features[k] for k in COMPONENT_KEYS]

def calibrate(csv_path: Path, out_path: Path):
    df = pd.read_csv(csv_path)
    X_raw = [build_feature_row(r) for _,r in df.iterrows()]
    y     = df["CombatPower"].values

    scaler = StandardScaler()
    X = scaler.fit_transform(X_raw)

    model = Ridge(alpha=RIDGE_ALPHA, fit_intercept=False)
    model.fit(X, y)

    # ย้อนสเกล
    coef_std = model.coef_
    coef_real = coef_std / scaler.scale_

    new_theta = {k: float(coef_real[i]) for i,k in enumerate(COMPONENT_KEYS)}

    with open(out_path, "w") as f:
        json.dump(new_theta, f, indent=2)
    print("Updated THETA written to", out_path)
    for k,v in new_theta.items():
        print(f"{k:>10}: {v:10.3f}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="../../database/rawdata/test_fitness.csv",
                   help="CSV path with CombatPower label")
    p.add_argument("--out", default="weights.json",
                   help="Output weights JSON")
    args = p.parse_args()
    calibrate(Path(args.csv), Path(args.out))

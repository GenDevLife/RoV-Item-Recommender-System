#!/usr/bin/env python3
# calibrate.py  –  Optimise THETA weights from test_fitness.csv
# 11 May 2025 • compatible with main.py rev-C

import argparse, json, math, sys
from pathlib import Path

import pandas as pd
import numpy as np

# ────────────────────────────── IMPORT จาก main.py ─────────────────────────────
from main import (                                       # <-- main.py rev-C
    load_hero_stats,
    get_recommended_item_types, get_hero_info,
    score_stats, score_budget as budget_component,
    skill_component, synergy_component, category_component,
    class_component, lane_component, get_phase_weight,
    BASE_BUDGET, PHASE_WEIGHTS, item_data, THETA,
)

PHASE          = "Late"          # ปรับได้ Early / Mid / Late
STAT_LEVEL     = {"Early": 3, "Mid": 9, "Late": 15}[PHASE]
THETA_KEYS     = list(THETA.keys())

# ───────── helper กัน None ใน stat caps ─────────
def safe_caps(hero: str, buf: float = 0.20) -> dict[str, float]:
    """คืน hard-cap โดยแปลง None → 0 เพื่อกัน TypeError"""
    base = load_hero_stats(hero, 15)
    return {
        k.upper(): ((v or 0.0) * (1 + buf)) if (v or 0.0) > 0 else 1.0
        for k, v in base.items()
    }
# ------------------------------------------------------------------------------

def build_feature_row(row: pd.Series) -> dict[str, float]:
    hero = row["HeroID"]
    lane = row["Lane"]
    hero_info = get_hero_info(hero)
    hero_info["lane"] = lane

    # ----- เตรียมชุดไอเทม (กรองค่าว่าง / ID ไม่รู้จัก) -----
    build = [str(row[f"Item{i}"]).strip() for i in range(1, 7)
             if str(row[f"Item{i}"]).strip() in item_data]

    # สถิติพื้นฐาน / cap
    hb   = load_hero_stats(hero, STAT_LEVEL)
    caps = safe_caps(hero)

    # phase-specific weight
    w_phase = get_phase_weight(hero_info, PHASE)

    # ----- คอมโพเนนต์ของ fitness -----
    comps = {
        "stat":    score_stats(build, hb, caps, w_phase),
        "budget":  budget_component(sum(item_data[i]["Price"] for i in build),
                                    BASE_BUDGET[PHASE]),
        "skill":   skill_component(build, get_recommended_item_types(hero)),
        "synergy": synergy_component(set(build)),
        "cat":     len(build),
        "class":   class_component(build, hero_info),
        "lane":    lane_component(build, hero_info),
    }
    for cat in ["ATK", "Def", "Magic"]:
        comps[f"cat_{cat}"] = category_component(build, cat)

    # เติมศูนย์สำหรับคีย์ที่ไม่มีใน comps
    for k in THETA_KEYS:
        comps.setdefault(k, 0.0)
    return comps

# ────────────────────────────── CALIBRATION ───────────────────────────────────
def calibrate(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path)

    X_raw = [build_feature_row(r) for _, r in df.iterrows()]
    y     = df["CombatPower"].to_numpy(dtype=float)

    X = np.array([[row[k] for k in THETA_KEYS] for row in X_raw])

    # ======== linear least-squares ========
    w, *_ = np.linalg.lstsq(X, y, rcond=None)

    theta_new = {k: float(v) for k, v in zip(THETA_KEYS, w)}
    print("=== NEW THETA ===")
    for k, v in theta_new.items():
        print(f"{k:<10} = {v:10.4f}")

    # ------ write weights.json ------
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(theta_new, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] wrote {out_path}")

# ────────────────────────────── CLI ───────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Calibrate THETA from CSV")
    ap.add_argument(
        "--csv",
        default="../../database/rawdata/test_fitness.csv",             # ← ค่าเริ่มต้น
        help="CSV file with test builds (default: test_fitness.csv)"
    )
    ap.add_argument("--out", default="weights.json",
                    help="output weights.json (default: weights.json)")
    args = ap.parse_args()

    try:
        calibrate(Path(args.csv), Path(args.out))
    except Exception as e:
        print("Calibration failed:", e)
        sys.exit(1)

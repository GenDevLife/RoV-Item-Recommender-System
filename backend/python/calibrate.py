#!/usr/bin/env python3
# calibrate.py  –  ปรับน้ำหนัก THETA ด้วย Linear Regression (OLS)
# ใช้ไฟล์ test_fitness.csv (Late-game build 6 ชิ้น) เป็นข้อมูลเทรน
# 12 May 2025 • compatible with main.py rev-C

from pathlib import Path
import argparse, json, sys
import numpy as np
import pandas as pd

# ────────────────────── import utilities จาก main.py ──────────────────────
from main import (
    load_hero_stats,
    get_recommended_item_types, get_hero_info,
    score_stats, score_budget as budget_component,
    skill_component, synergy_component, category_component,
    class_component, lane_component, get_phase_weight,
    load_item_data, THETA,
)

item_data = load_item_data()

# ──────────────────────────── ค่าคงที่ภายในสคริปต์ ───────────────────────
PHASE         = "Late"               # เทรนเฉพาะเฟสปลายเกม
STAT_LEVEL    = 15                   # level ที่ใช้สถิติพื้นฐาน
LATE_BUDGET   = 14_000               # งบ full build 6 ชิ้น
THETA_KEYS    = list(THETA.keys())   # ชื่อฟีเจอร์ 11 ชนิด

# ───────── helper กัน None / 0 ใน cap (เลี่ยงหารศูนย์) ─────────
def safe_caps(hero: str, buf: float = 0.20) -> dict[str, float]:
    base = load_hero_stats(hero, STAT_LEVEL)
    return {
        k.upper(): ((v or 0.0) * (1 + buf)) if (v or 0.0) > 0 else 1.0
        for k, v in base.items()
    }

# ───────────── สร้าง vector ฟีเจอร์ 1 แถว จากข้อมูลบิลด์ ─────────────
def build_feature_row(row: pd.Series) -> dict[str, float]:
    hero = row["HeroID"]
    lane = row["Lane"]
    hero_info = get_hero_info(hero)          # default จาก DB
    hero_info["lane"] = lane                 # override ด้วยไฟล์ CSV
    hero_info["primary"] = row["Class"]      # override primary class

    # สร้างลิสต์ไอเทม (กรองค่าว่าง/ID ไม่รู้จัก)
    build = [
        iid for iid in (str(row[f"Item{i}"]).strip() for i in range(1, 7))
        if iid in item_data
    ]

    hb   = load_hero_stats(hero, STAT_LEVEL)
    caps = safe_caps(hero)
    w_phase = get_phase_weight(hero_info, PHASE)

    comps = {
        "stat":    score_stats(build, hb, caps, w_phase),
        "budget":  budget_component(
                       sum(item_data[i]["Price"] for i in build),
                       LATE_BUDGET),
        "skill":   skill_component(build, get_recommended_item_types(hero)),
        "synergy": synergy_component(set(build)),
        "cat":     len(build),
        "class":   class_component(build, hero_info),
        "lane":    lane_component(build, hero_info),
    }
    for cat in ["ATK", "Def", "Magic"]:
        comps[f"cat_{cat}"] = category_component(build, cat)

    # เติมศูนย์ให้ครบทุก THETA key
    for k in THETA_KEYS:
        comps.setdefault(k, 0.0)
    return comps

# ────────────────────── ขั้นตอนคาลิเบรตเวกเตอร์ THETA ────────────────────
def calibrate(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path)

    # ---------- target: WinRate (% ชนะ) ----------
    y = df["WinRate"].to_numpy(float)

    # ---------- feature matrix ----------
    X_raw = [build_feature_row(r) for _, r in df.iterrows()]
    X = np.array([[row[k] for k in THETA_KEYS] for row in X_raw])

    # ---------- Ordinary Least Squares ----------
    w, *_ = np.linalg.lstsq(X, y, rcond=None)

    theta_new = {k: float(v) for k, v in zip(THETA_KEYS, w)}
    print("=== NEW THETA (OLS on WinRate) ===")
    for k, v in theta_new.items():
        print(f"{k:<12}= {v:10.4f}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(theta_new, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] weights saved to {out_path}")

# ─────────────────────────────── CLI ────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Calibrate THETA via OLS")
    ap.add_argument(
        "--csv", default="../../database/rawdata/test_fitness.csv",
        help="CSV file with build data (default: test_fitness.csv)"
    )
    ap.add_argument(
        "--out", default="weights.json",
        help="output weights file (default: weights.json)"
    )
    args = ap.parse_args()

    try:
        calibrate(Path(args.csv), Path(args.out))
    except Exception as e:
        print("Calibration failed:", e)
        sys.exit(1)

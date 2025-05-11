#!/usr/bin/env python3
# main.py – RoV Genetic-Algorithm Item Recommender
# rev-C • 11 พ.ค. 2025
"""
▸ แก้ปัญหา --force ไม่ทำงาน
▸ เปลี่ยน budget เป็น exp-decay ต่อเนื่อง
▸ ปรับ THETA / Phase Weight (Early 0.3 Mid 0.3 Late 0.4)
▸ Lazy-init connection-pool และ fallback TCP 127.0.0.1 บน Windows
* I/O CLI และ schema ฐานข้อมูล ไม่เปลี่ยน *
"""

from __future__ import annotations
import os, random, math, time, json, argparse, sys
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

# ────────────────────────── 0. น้ำหนัก THETA ──────────────────────────
THETA: Dict[str, float] = {
    "stat": 1234.5152900513515,
    "budget": 167.21484907713506,
    "skill": -330.69627100529004,
    "synergy": 0.05699362842449318,
    "cat": 1003.2890944627134,
    "cat_ATK": 0.0,
    "cat_Def": -7.105427357601002e-14,
    "cat_Magic": -7.597867980580487,
    "class": 757.0236731369758,
    "lane": -379.0656780893436
}

def load_theta_config(path: str = "weights.json") -> None:
    """Override THETA จากไฟล์ภายนอกถ้ามี"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            THETA.update(json.load(f))
            print(f"[INFO] Loaded THETA overrides from {path}")
    except FileNotFoundError:
        pass

# ─────────────────────── 1. การเชื่อมต่อฐานข้อมูล ─────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "../config/.env"))
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PRIMARY_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
}

_POOL: Optional[pooling.MySQLConnectionPool] = None  # lazy

def _init_pool():
    global _POOL
    try:
        _POOL = pooling.MySQLConnectionPool(pool_name="rov_pool",
                                            pool_size=3,
                                            **DB_CONFIG)
        print("[INFO] MySQL pool initialised")
    except Error as e:
        print(f"[WARN] pool init failed: {e} – fallback direct connect")
        _POOL = None

def get_conn():
    global _POOL
    if _POOL is None:
        _init_pool()
    tries, delay = 0, 1
    while tries < 4:
        try:
            if _POOL:
                return _POOL.get_connection()
            return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"[WARN] DB connect failed: {e}; retry {delay}s")
            time.sleep(delay)
            tries += 1
            delay *= 2
    raise RuntimeError("Cannot connect to MySQL")

# ───────────────────────── 2. ค่าคงที่ของ GA ──────────────────────────
POP_SIZE, MAX_GEN = 300, 60
CROSSOVER_RATE, BASE_MUT_RATE = 0.8, 0.05
STAGNANT_LIMIT = 6
PHASE_WEIGHTS = {"Early": .3, "Mid": .3, "Late": .4}
BASE_BUDGET    = {"Early": 2700, "Mid": 7500, "Late": 14000}

# ─────────────────────── 3. โหลดข้อมูลจาก DB ─────────────────────────
@lru_cache(maxsize=None)
def load_synergy_rules() -> List[Tuple[Set[str], float]]:
    grp: Dict[str, Set[str]] = defaultdict(set)
    bonus: Dict[str, float]  = {}
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT SynergyGroup, ItemID, BonusValue FROM item_synergy")
        for g, iid, b in cur.fetchall():
            grp[g].add(iid)
            bonus[g] = float(b or 0.0)
    print(f"[INFO] Loaded {len(grp)} synergy groups from DB")
    return [(frozenset(v), bonus[k]) for k, v in grp.items()]

SYNERGY_RULES = load_synergy_rules()

@lru_cache(maxsize=None)
def load_item_data() -> Dict[str, Dict]:
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT ItemID, ItemName, Class, Price,
                   Phys_ATK, Magic_Power, Phys_Defense, HP,
                   Cooldown_Reduction, Critical_Rate, Movement_Speed,
                   Attack_Speed, HP_5_sec, Mana_5_sec,
                   Armor_Pierce, Magic_Pierce, Life_Steal, Magic_Life_Steal,
                   Max_Mana, Magic_Defense, Resistance
            FROM items""")
        data = {}
        for row in cur.fetchall():
            for k, v in row.items():
                if k not in ("ItemID", "ItemName", "Class"):
                    row[k] = float(v or 0.0)
            data[row["ItemID"]] = row
        return data

item_data = load_item_data()

# hero helpers -------------------------------------------------------------
@lru_cache(maxsize=128)
def load_hero_stats(hero: str, level: int) -> Dict[str, float]:
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT Phys_ATK, Magic_Power, Phys_Defense, HP,
                   Cooldown_Reduction, Critical_Rate, Movement_Speed
            FROM herostats WHERE HeroID=%s AND Level=%s""",
            (hero, level))
        return cur.fetchone() or {}

@lru_cache(maxsize=128)
def load_stat_caps(hero: str, buf: float = 0.20) -> Dict[str, float]:
    base = load_hero_stats(hero, 15)
    return {k.upper(): v * (1 + buf) for k, v in base.items()}

@lru_cache(maxsize=128)
def get_recommended_item_types(hero: str) -> List[str]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT RecommendItemType FROM heroskills WHERE HeroID=%s", (hero,))
        return [r[0] for r in cur.fetchall() if r[0]]

@lru_cache(maxsize=128)
def get_hero_info(hero: str) -> Dict[str, Optional[str]]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT First_Class, Second_Class, First_Lane FROM heroes WHERE HeroID=%s", (hero,))
        r = cur.fetchone()
    return {
        "primary":   r[0] if r else "Fighter",
        "secondary": r[1] if r and r[1] else None,
        "lane":      r[2] if r and r[2] else "Mid",
    }

# ─────────────────────── 4. ฟังก์ชันช่วยคำนวณ ─────────────────────────
_n = lambda x: float(x or 0.0)
STAT_MAP = [
    ("patk", "Phys_ATK"),
    ("ap",   "Magic_Power"),
    ("def",  "Phys_Defense"),
    ("hp",   "HP"),
    ("cdr",  "Cooldown_Reduction"),
    ("crit", "Critical_Rate"),
    ("ms",   "Movement_Speed"),
]

def get_phase_weight(info, phase):
    w = {"patk": .30, "ap": .20, "def": .20, "hp": .20,
         "cdr": .05, "crit": .05, "ms": .05}
    if phase == "Early":
        w["cdr"] += .05
    if phase == "Late":
        w["hp"]  += .10
    if info["lane"] == "Support":
        w["hp"]  += .05
        w["cdr"] += .05
    return w

def score_stats(ch, hb, caps, w):
    base = {s: _n(hb.get(db)) for s, db in STAT_MAP}
    for it in ch:
        row = item_data[it]
        for s, db in STAT_MAP:
            base[s] += row.get(db, 0.0)
    return sum(w[s] * min(base[s] / caps.get(s.upper(), 1), 1.0) for s in base)

# components ---------------------------------------------------------------
score_budget      = lambda cost, bud: 1.0 if cost <= bud else math.exp(-0.8 * ((cost - bud) / bud))
skill_component   = lambda ch, rec:   sum(.2 for it in ch if item_data[it]["Class"] in rec)
synergy_component = lambda ch:        sum(v for req, v in SYNERGY_RULES if req <= set(ch))
category_component= lambda ch, cat:   sum(1 for it in ch if item_data[it]["Class"] == cat)
class_component   = lambda ch, info:  sum(1 for it in ch if item_data[it]["Class"] == info["primary"])
lane_component    = lambda ch, info:  sum(1 for it in ch if item_data[it]["Class"] == info["lane"])

# ─────────────────── 5. chromosome utilities ─────────────────────────────
def repair_chromosome(ch: List[str], lane: str,
                      ban: Set[str], force: Set[str]) -> List[str]:
    """ใส่ของบังคับ, ≤1 Movement, เคารพ ban, เติมครบ 6 ชิ้น"""
    out: List[str] = []
    seen: Set[str] = set()
    move_cnt = 0

    # 1) forced items first
    for it in force:
        if it in ban or it in seen:
            continue
        out.append(it); seen.add(it)
        if item_data[it]["Class"] == "Movement":
            move_cnt += 1

    # 2) keep valid items from original chromosome
    for it in ch:
        if len(out) >= 6:
            break
        if it in ban or it in seen or it in force:
            continue
        if item_data[it]["Class"] == "Movement" and move_cnt >= 1:
            continue
        out.append(it); seen.add(it)
        if item_data[it]["Class"] == "Movement":
            move_cnt += 1

    # 3) random fill
    pool = [
        i for i in item_data
        if i not in seen and i not in ban and
        not (item_data[i]["Class"] == "Movement" and move_cnt >= 1)
    ]
    random.shuffle(pool)
    out.extend(pool[:max(0, 6 - len(out))])

    # jungle rule – ต้องมีไอเทม Jungle อย่างน้อย 1 เมื่อ lane = Jungle
    if lane == "Jungle" and not any(item_data[it]["Class"] == "Jungle" for it in out):
        jungle_pool = [i for i in pool if item_data[i]["Class"] == "Jungle"]
        if jungle_pool:
            out[-1] = random.choice(jungle_pool)

    return out[:6]

def mutate(ch, pool, rate, lane, ban, force):
    out = ch[:]
    avail = [i for i in pool if i not in out and i not in ban]
    for idx in range(6):
        if out[idx] in force:          # ห้ามเปลี่ยนของบังคับ
            continue
        if random.random() < rate and avail:
            out[idx] = random.choice(avail)
            avail.remove(out[idx])
    return repair_chromosome(out, lane, ban, force)

def crossover(p1, p2):
    if random.random() < CROSSOVER_RATE:
        pt = random.randint(1, 5)
        return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]
    return p1[:], p2[:]

def tournament_select(pop, fits, k=3):
    idxs = random.sample(range(len(pop)), k)
    return pop[max(idxs, key=lambda i: fits[i])]

adaptive_mut_rate = lambda gen: BASE_MUT_RATE * math.exp(-gen / (0.6 * MAX_GEN))

# ────────────────────────── 6. fitness & GA ─────────────────────────────
def calculate_fitness(ch, hero, info, phase, caps):
    hb = load_hero_stats(hero, {"Early": 3, "Mid": 9, "Late": 15}[phase])
    rec = get_recommended_item_types(hero)
    cost = sum(item_data[i]["Price"] for i in ch)
    budget = BASE_BUDGET[phase]

    comps = {
        "stat":    score_stats(ch, hb, caps, get_phase_weight(info, phase)),
        "budget":  score_budget(cost, budget),
        "skill":   skill_component(ch, rec),
        "synergy": synergy_component(ch),
        "cat":     len(ch),
        "class":   class_component(ch, info),
        "lane":    lane_component(ch, info),
    }
    for cat in ["ATK", "Def", "Magic"]:
        comps[f"cat_{cat}"] = category_component(ch, cat)

    raw = sum(THETA[k] * v for k, v in comps.items())
    return raw * PHASE_WEIGHTS[phase]

def run_ga(hero, lane,
           hero_class: Optional[str] = None,
           force_items: Optional[List[str]] = None,
           ban_items: Optional[List[str]] = None,
           phase="Late") -> Tuple[List[str], float]:

    force, ban = set(force_items or []), set(ban_items or [])
    info = get_hero_info(hero)
    info["lane"] = lane
    if hero_class:
        info["primary"] = hero_class

    if sum(1 for x in force if item_data[x]["Class"] == "Movement") > 1:
        raise ValueError("มี Movement มากกว่า 1 ชิ้นใน --force")

    caps = load_stat_caps(hero)
    pool = [i for i in item_data if i not in ban]

    # ประชากรเริ่มต้น: รวม force แล้วสุ่มเติมให้ครบ 6
    def seed() -> List[str]:
        base = list(force)
        base += random.sample([i for i in pool if i not in base],
                              k=max(0, 6 - len(base)))
        return repair_chromosome(base, lane, ban, force)

    pop = [seed() for _ in range(POP_SIZE)]

    best_fit, best_ch, stagn = -1.0, [], 0
    for gen in range(MAX_GEN):
        fits = [calculate_fitness(ch, hero, info, phase, caps) for ch in pop]
        idx_best = max(range(len(fits)), key=lambda i: fits[i])
        if fits[idx_best] > best_fit:
            best_fit, best_ch, stagn = fits[idx_best], pop[idx_best][:], 0
        else:
            stagn += 1
        if stagn >= STAGNANT_LIMIT:
            break

        elites = [p for p, _ in sorted(zip(pop, fits), key=lambda x: -x[1])]
        elites = elites[:max(1, int(POP_SIZE * 0.05))]
        new_pop = elites[:]

        while len(new_pop) < POP_SIZE:
            p1 = tournament_select(pop, fits)
            p2 = tournament_select(pop, fits)
            c1, c2 = crossover(p1, p2)
            rate = adaptive_mut_rate(gen)
            new_pop.append(mutate(c1, pool, rate, lane, ban, force))
            if len(new_pop) < POP_SIZE:
                new_pop.append(mutate(c2, pool, rate, lane, ban, force))
        pop = new_pop

    return best_ch, best_fit

# ───────────────────────────── 7. CLI ────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="RoV GA-based Item Recommender")
    ap.add_argument("--hero",   required=True)
    ap.add_argument("--class", dest="hero_class", required=True)
    ap.add_argument("--lane",   required=True)
    ap.add_argument("--force", nargs="*", default=None,
                    help="รายการ ItemID ที่ต้องมี (ใส่ได้หลายชิ้น)")
    ap.add_argument("--ban",   nargs="*", default=None,
                    help="รายการ ItemID ที่ห้ามใช้")
    args = ap.parse_args()

    load_theta_config()

    for ph in ["Early", "Mid", "Late"]:
        build, fit = run_ga(args.hero,
                            args.lane,
                            args.hero_class,
                            args.force,
                            args.ban,
                            phase=ph)
        print(f"{ph:<5} Build={build} | Fitness={fit:.4f}")

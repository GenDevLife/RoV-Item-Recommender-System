#!/usr/bin/env python3
# main.py – GA สำหรับแนะนำไอเทม RoV (ปรับปรุง 2025-05-08)

from __future__ import annotations
import os, random, math, time, json, argparse
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

# ─────────────────── 0. THETA ────────────────────
THETA: Dict[str, float] = {
    "stat": 1312.0514160117584,
    "budget": 3163.2636283064594,
    "skill": -334.31908690518026,
    "synergy": 0.07303236126269995,
    "cat": 527.2106047177434,
    "cat_ATK": 2.2737367544323206e-13,
    "cat_Def": 0.0,
    "cat_Magic": -19.70922175679745,
    "class": -105.12317534600265,
    "lane": -105.123175346003
}

def load_theta_config(path: str = "weights.json") -> None:
    global THETA
    try:
        with open(path) as f:
            THETA.update(json.load(f))
            print(f"[INFO] Loaded THETA from {path}")
    except FileNotFoundError:
        print("[INFO] weights.json not found, using default THETA")

# ─────────────────── 1. DB ───────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "../config/.env"))
DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     int(os.getenv("DB_PRIMARY_PORT", 3306)),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset":  "utf8mb4",
}
POOL = pooling.MySQLConnectionPool(pool_name="rov_pool", pool_size=3, **DB_CONFIG)
def get_conn() -> mysql.connector.connection_cext.CMySQLConnection:
    tries, delay = 0, 1
    while tries < 5:
        try:
            return POOL.get_connection()
        except Error as e:
            print(f"[WARN] DB connect failed: {e}, retry {delay}s")
            time.sleep(delay); tries += 1; delay *= 2
    raise RuntimeError("DB connection failed")

# ─────────────────── 2. GA constants ─────────────
POP_SIZE, MAX_GEN = 300, 60
CROSSOVER_RATE, BASE_MUT_RATE = 0.8, 0.05
STAGNANT_LIMIT  = 6
PHASE_WEIGHTS   = {"Early": .2, "Mid": .3, "Late": .5}
BASE_BUDGET     = {"Early": 2700, "Mid": 7500, "Late": 14000}
UNIQUE_SINGLE: Set[str] = set()          # ไม่ใช้แล้ว

# ─────────────────── 3. Synergy rules ────────────
@lru_cache(maxsize=None)
def load_synergy_rules() -> List[Tuple[Set[str], float]]:
    grp_map: Dict[str, Set[str]] = defaultdict(set)
    bonus_map: Dict[str, float]  = {}
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT SynergyGroup, ItemID, BonusValue FROM item_synergy")
        for grp, item, bonus in cur.fetchall():
            grp_map[grp].add(item)
            bonus_map[grp] = float(bonus or 0.0)
    rules = [(items, bonus_map[grp]) for grp, items in grp_map.items()]
    print(f"[INFO] Loaded {len(rules)} synergy groups from DB")
    return rules
SYNERGY_RULES = load_synergy_rules()

# ─────────────────── 4. data loaders ─────────────
@lru_cache(maxsize=None)
def load_item_data() -> Dict[str, Dict]:
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT ItemID, ItemName, Class, Price,
                   Phys_ATK, Magic_Power, Phys_Defense,
                   HP, Cooldown_Reduction, Critical_Rate,
                   Movement_Speed, Attack_Speed, HP_5_sec,
                   Mana_5_sec, Armor_Pierce, Magic_Pierce,
                   Life_Steal, Magic_Life_Steal,
                   Max_Mana, Magic_Defense, Resistance
            FROM items""")
        data: Dict[str, Dict] = {}
        for row in cur.fetchall():
            for k, v in row.items():
                if k not in ("ItemID", "ItemName", "Class"):
                    row[k] = float(v or 0.0)
            data[row["ItemID"]] = row
        return data
@lru_cache(maxsize=None)
def load_item_comp() -> Dict[str, List[str]]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT Composite_ItemID, BaseItemID FROM itemcomposition")
        comp: Dict[str, List[str]] = {}
        for cid, bid in cur.fetchall():
            comp.setdefault(cid, []).append(bid)
        return comp
@lru_cache(maxsize=128)
def load_hero_stats(hero_id: str, level: int) -> Dict[str, float]:
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT Phys_ATK, Magic_Power, Phys_Defense, HP,
                   Cooldown_Reduction, Critical_Rate, Movement_Speed
            FROM herostats WHERE HeroID=%s AND Level=%s""",
            (hero_id, level))
        return cur.fetchone() or {}
@lru_cache(maxsize=128)
def get_recommended_item_types(hero_id: str) -> List[str]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT RecommendItemType FROM heroskills WHERE HeroID=%s""",
            (hero_id,))
        return [r[0] for r in cur.fetchall() if r[0]]
@lru_cache(maxsize=128)
def get_hero_info(hero_id: str) -> Dict[str, Optional[str]]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT First_Class, Second_Class, First_Lane FROM heroes WHERE HeroID=%s""",
            (hero_id,))
        row = cur.fetchone()
    return {"primary": row[0], "secondary": row[1] or None, "lane": row[2] or "Mid"} if row else \
           {"primary": "Fighter", "secondary": None, "lane": "Mid"}

item_data = load_item_data()
item_comp = load_item_comp()

# ─────────────────── 5. stat caps ────────────────
def _n(x): return float(x) if x not in (None, "", "NULL") else 0.0
def load_stat_caps(hero: str, buf: float = .20) -> Dict[str, float]:
    items = item_data.values(); hero_max = load_hero_stats(hero, 15)
    def imax(col): return max(_n(r.get(col)) for r in items)
    return {
        "PATK": max(_n(hero_max.get("Phys_ATK")), imax("Phys_ATK")) * (1+buf),
        "AP":   max(_n(hero_max.get("Magic_Power")), imax("Magic_Power"))*(1+buf),
        "DEF":  max(_n(hero_max.get("Phys_Defense")), imax("Phys_Defense"))*(1+buf),
        "HP":   max(_n(hero_max.get("HP")), imax("HP"))*(1+buf),
        "MS":   max(_n(hero_max.get("Movement_Speed")), imax("Movement_Speed"))*1.1,
        "CDR":  0.40, "CRIT": 1.0,
        "AS":   imax("Attack_Speed")*(1+buf),
        "R5":   imax("HP_5_sec")*(1+buf),
        "MPR":  imax("Mana_5_sec")*(1+buf),
        "APIERCE": imax("Armor_Pierce")*(1+buf),
        "MPIERCE": imax("Magic_Pierce")*(1+buf),
        "LS":   imax("Life_Steal")*(1+buf),
        "MLS":  imax("Magic_Life_Steal")*(1+buf),
        "MANA": imax("Max_Mana")*(1+buf),
        "MDEF": imax("Magic_Defense")*(1+buf),
        "RES":  imax("Resistance")*(1+buf),
    }

# ─────────────────── 6. repair / mutation ─────────
def is_valid_chromo(ch: List[str], lane: str) -> bool:
    if sum(1 for it in ch if item_data[it]["Class"] == "Movement") > 1:
        return False
    for cid, bases in item_comp.items():
        if cid in ch and not all(b in ch for b in bases):
            return False
    return True
def repair_chromosome(ch: List[str], lane: str, ban: Set[str], force: Set[str]) -> List[str]:
    out, seen, move_cnt = [], set(), 0
    # 0) forced items
    for it in force:
        if it in item_data and it not in ban:
            if item_data[it]["Class"] == "Movement": move_cnt += 1
            out.append(it); seen.add(it)
    # 1) original genes
    for it in ch:
        if len(out) >= 6: break
        if it not in ban and it not in seen:
            if item_data[it]["Class"] == "Movement" and move_cnt >= 1: continue
            out.append(it); seen.add(it)
            if item_data[it]["Class"] == "Movement": move_cnt += 1
    # 2) random fill
    pool = [i for i in item_data if i not in ban and i not in seen]
    while len(out) < 6 and pool:
        cand = random.choice(pool); pool.remove(cand)
        if item_data[cand]["Class"] == "Movement" and move_cnt >= 1: continue
        out.append(cand); seen.add(cand)
        if item_data[cand]["Class"] == "Movement": move_cnt += 1
    # 3) jungle rule
    if lane == "Jungle" and not any(item_data[it]["Class"] == "Jungle" for it in out):
        jungle_pool = [i for i in item_data if item_data[i]["Class"] == "Jungle" and i not in ban]
        if jungle_pool: out[-1] = random.choice(jungle_pool)
    return out[:6]
def mutate(ch, pool, rate, lane, ban, force):
    out = ch[:]; avail = [i for i in pool if i not in out and i not in ban]
    for i in range(6):
        if out[i] not in force and random.random() < rate and avail:
            out[i] = random.choice(avail); avail.remove(out[i])
    return repair_chromosome(out, lane, ban, force)

# ─────────────────── 7. components ───────────────
def get_phase_weight(info, phase):
    w = {"patk":.30,"ap":.20,"def":.20,"hp":.20,"cdr":.05,"crit":.05,"ms":.05}
    if phase=="Early": w["cdr"] += .05
    if phase=="Late":  w["hp"]  += .10
    if info.get("lane")=="Support":
        w["hp"] += .05; w["cdr"] += .05
    return w
def score_stats(ch, hb, caps, w):
    total = {s:_n(hb.get(db)) for s,db in [
        ("patk","Phys_ATK"), ("ap","Magic_Power"), ("def","Phys_Defense"),
        ("hp","HP"), ("cdr","Cooldown_Reduction"), ("crit","Critical_Rate"),
        ("ms","Movement_Speed")
    ]}
    for it in ch:
        row = item_data[it]
        for s, db in [
            ("patk","Phys_ATK"), ("ap","Magic_Power"), ("def","Phys_Defense"),
            ("hp","HP"), ("cdr","Cooldown_Reduction"), ("crit","Critical_Rate"),
            ("ms","Movement_Speed")
        ]:
            total[s] += _n(row.get(db))
    return sum(w[s]*min(total[s]/caps.get(s.upper(),1),1.0) for s in total)
def score_budget(cost, budget, phase):
    if cost<=budget: return 1.0
    ratio=(cost-budget)/budget
    return 1.0-0.5*ratio if ratio<=0.1 else max(0.0,0.75-(ratio-0.1)**1.3)
stat_component   = lambda ch,hb,caps,w:   score_stats(ch,hb,caps,w)
budget_component = lambda cost,bud,ph:    score_budget(cost,bud,ph)
skill_component  = lambda ch,rec:         sum(.2 for it in ch if item_data[it]["Class"] in rec)
synergy_component= lambda ch:             sum(b for req,b in SYNERGY_RULES if req.issubset(ch))
category_component=lambda ch,cat:         sum(1 for it in ch if item_data[it]["Class"]==cat)
class_component  = lambda ch,info:        sum(1 for it in ch if item_data[it]["Class"]==info["primary"])
lane_component   = lambda ch,info:        sum(1 for it in ch if item_data[it]["Class"]==info["lane"])

# ─────────────────── 8. fitness + GA ─────────────
def calculate_fitness(ch, hero, info, phase, caps):
    hb  = load_hero_stats(hero, {"Early":3,"Mid":9,"Late":15}[phase])
    rec = get_recommended_item_types(hero)
    cost = sum(item_data[i]["Price"] for i in ch)
    budget = BASE_BUDGET[phase]*(1.1 if info["lane"]=="Jungle" and phase=="Early" else 1.0)
    comps = {
        "stat": stat_component(ch,hb,caps,get_phase_weight(info,phase)),
        "budget": budget_component(cost,budget,phase),
        "skill":  skill_component(ch,rec),
        "synergy":synergy_component(ch),
        "cat":     len(ch),                             # placeholder (คงที่ 6)
        "class":  class_component(ch,info),
        "lane":   lane_component(ch,info),
    }
    for cat in ["ATK","Def","Magic"]:
        comps[f"cat_{cat}"] = category_component(ch,cat)
    raw = sum(THETA.get(k,0.0)*v for k,v in comps.items())
    return raw*PHASE_WEIGHTS[phase]

def crossover(p1,p2):
    if random.random()<CROSSOVER_RATE:
        pt=random.randint(1,5)
        return p1[:pt]+p2[pt:], p2[:pt]+p1[pt:]
    return p1[:], p2[:]
def tournament_select(pop,fits,k=3):
    idxs=random.sample(range(len(pop)),k)
    return pop[max(idxs,key=lambda i:fits[i])]
def adaptive_mut_rate(gen): return BASE_MUT_RATE*math.exp(-gen/(0.6*MAX_GEN))

def run_ga(hero,lane,hero_class=None,force_items=None,ban_items=None,phase="Late"):
    force, ban = set(force_items or []), set(ban_items or [])
    info=get_hero_info(hero);  info["lane"]=lane
    if hero_class: info["primary"]=hero_class
    if sum(1 for it in force if item_data[it]["Class"]=="Movement")>1:
        print("[ERROR] forced >1 Movement item"); return [],-1.0
    caps=load_stat_caps(hero); pool=[i for i in item_data if i not in ban]
    pop=[repair_chromosome(random.sample(pool,6),lane,ban,force) for _ in range(POP_SIZE)]
    best_fit,best_ch=-1.0,[]
    stagn=0
    for gen in range(MAX_GEN):
        fits=[calculate_fitness(ch,hero,info,phase,caps) for ch in pop]
        idx=max(range(len(fits)),key=lambda i:fits[i])
        if fits[idx]>best_fit: best_fit,best_ch,fits_best= fits[idx],pop[idx][:],0; stagn=0
        else: stagn+=1
        if stagn>=STAGNANT_LIMIT: break
        elites=[p for p,_ in sorted(zip(pop,fits),key=lambda x:-x[1])[:max(1,int(POP_SIZE*0.05))]]
        new_pop=elites[:]
        while len(new_pop)<POP_SIZE:
            p1,p2=tournament_select(pop,fits),tournament_select(pop,fits)
            c1,c2=crossover(p1,p2)
            rate=adaptive_mut_rate(gen)
            new_pop.append(mutate(c1,pool,rate,lane,ban,force))
            if len(new_pop)<POP_SIZE:
                new_pop.append(mutate(c2,pool,rate,lane,ban,force))
        pop=new_pop
    return best_ch,best_fit

# ─────────────────── 9. CLI ──────────────────────
if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--hero", required=True); ap.add_argument("--class", dest="hero_class", required=True)
    ap.add_argument("--lane", required=True); ap.add_argument("--force", nargs="*", default=None)
    ap.add_argument("--ban",  nargs="*", default=None)
    args=ap.parse_args()
    load_theta_config()
    for ph in ["Early","Mid","Late"]:
        build,fit = run_ga(args.hero,args.lane,args.hero_class,args.force,args.ban,phase=ph)
        print(f"{ph} : Build={build} | Fitness={fit:.4f}")

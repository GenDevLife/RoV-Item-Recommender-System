from __future__ import annotations
import os
import random
import math
import time
import json
import argparse
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Set, Any
from collections import defaultdict

import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

# ---------------------------- Parameter Setting -----------------------------
THETA: Dict[str, float] = {
    'stat': 1234.5152900513515,
    'budget': 167.21484907713506,
    'skill': -330.69627100529004,
    'synergy': 0.05699362842449318,
    'cat': 1003.2890944627134,
    'cat_ATK': 0.0,
    'cat_Def': -7.105427357601002e-14,
    'cat_Magic': -7.597867980580487,
    'class': 757.0236731369758,
    'lane': -379.0656780893436,
}

GA_CONSTANTS: Dict[str, Any] = {
    'POP_SIZE': 300,
    'MAX_GEN': 60,
    'CROSSOVER_RATE': 0.8,
    'BASE_MUT_RATE': 0.05,
    'STAGNANT_LIMIT': 10,
    'PHASE_WEIGHTS': {'Early': 0.1, 'Mid': 0.3, 'Late': 0.6},
    'BASE_BUDGET': {'Early': 2700, 'Mid': 7500, 'Late': 14000},
}

def load_theta_config(path: str = 'weights.json') -> None:
    """Load and override THETA weights from an external JSON file if it exists."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            THETA.update(json.load(f))
            print(f'[INFO] Loaded THETA overrides from {path}')
    except FileNotFoundError:
        pass

# ---------------------------- Database Utilities ----------------------------
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PRIMARY_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': 'utf8mb4',
}

_CONNECTION_POOL: Optional[pooling.MySQLConnectionPool] = None

def initialize_connection_pool() -> None:
    """Initialize MySQL connection pool with lazy initialization."""
    global _CONNECTION_POOL
    try:
        _CONNECTION_POOL = pooling.MySQLConnectionPool(
            pool_name='rov_pool', pool_size=3, **DB_CONFIG
        )
        print('[INFO] MySQL pool initialized')
    except Error as e:
        print(f'[WARN] Pool init failed: {e} – falling back to direct connect')
        _CONNECTION_POOL = None

def get_connection() -> mysql.connector.connection.MySQLConnection:
    """Get a database connection, retrying with exponential backoff if needed."""
    global _CONNECTION_POOL
    if _CONNECTION_POOL is None:
        initialize_connection_pool()
    tries, delay = 0, 1
    while tries < 4:
        try:
            if _CONNECTION_POOL:
                return _CONNECTION_POOL.get_connection()
            return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f'[WARN] DB connect failed: {e}; retrying in {delay}s')
            time.sleep(delay)
            tries += 1
            delay *= 2
    raise RuntimeError('Cannot connect to MySQL')

# ---------------------------- Data Loading ----------------------------------
@lru_cache(maxsize=None)
def load_synergy_rules() -> List[Tuple[Set[str], float]]:
    """Load synergy rules from the database."""
    synergy_groups: Dict[str, Set[str]] = defaultdict(set)
    bonus_values: Dict[str, float] = {}
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SynergyGroup, ItemID, BonusValue FROM item_synergy')
        for group, item_id, bonus in cursor.fetchall():
            synergy_groups[group].add(item_id)
            bonus_values[group] = float(bonus or 0.0)
    print(f'[INFO] Loaded {len(synergy_groups)} synergy groups from DB')
    return [(frozenset(items), bonus_values[group]) for group, items in synergy_groups.items()]

SYNERGY_RULES = load_synergy_rules()

@lru_cache(maxsize=None)
def load_item_data() -> Dict[str, Dict[str, float]]:
    """Load item data from the database."""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ItemID, ItemName, Class, Price, Phys_ATK, Magic_Power,
                   Phys_Defense, HP, Cooldown_Reduction, Critical_Rate,
                   Movement_Speed, Attack_Speed, HP_5_sec, Mana_5_sec,
                   Armor_Pierce, Magic_Pierce, Life_Steal, Magic_Life_Steal,
                   Max_Mana, Magic_Defense, Resistance
            FROM items
        """)
        items = {}
        for row in cursor.fetchall():
            for key, value in row.items():
                if key not in ('ItemID', 'ItemName', 'Class'):
                    row[key] = float(value or 0.0)
            items[row['ItemID']] = row
        return items

ITEM_DATA = load_item_data()

@lru_cache(maxsize=128)
def load_hero_stats(hero: str, level: int) -> Dict[str, float]:
    """Load hero base stats at a given level."""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Phys_ATK, Magic_Power, Phys_Defense, HP,
                   Cooldown_Reduction, Critical_Rate, Movement_Speed
            FROM herostats WHERE HeroID=%s AND Level=%s
        """, (hero, level))
        return cursor.fetchone() or {}

@lru_cache(maxsize=128)
def load_stat_caps(hero: str, buffer: float = 0.20) -> Dict[str, float]:
    """Load hero stat caps with a buffer."""
    phase_levels = {'Early': 3, 'Mid': 9, 'Late': 15}
    base_stats = load_hero_stats(hero, phase_levels[phase])
    return {stat.upper(): value * (1 + buffer) for stat, value in base_stats.items()}

@lru_cache(maxsize=128)
def get_recommended_item_types(hero: str) -> List[str]:
    """Get recommended item types for a hero."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT RecommendItemType FROM heroskills WHERE HeroID=%s', (hero,))
        return [row[0] for row in cursor.fetchall() if row[0]]

def get_hero_info(hero: str) -> Dict[str, Optional[str]]:
    """คืนข้อมูลคลาสหลัก/รอง และเลนหลักรองของฮีโร่"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT First_Class, Second_Class, First_Lane, Second_Lane "
            "FROM heroes WHERE HeroID=%s",
            (hero,)
        )
        row = cur.fetchone() or (None, None, None, None)

    first_class, second_class, first_lane, second_lane = row
    # รวบเลนทั้งสอง (ถ้ามี)  ถ้าไม่มีเลยให้ Default เป็น Mid
    lanes = [l for l in (first_lane, second_lane) if l] or ["Mid"]

    return {
        "primary":    first_class   or "Fighter",
        "secondary":  second_class  or None,
        "lanes":      lanes,
        # เพื่อไม่ให้กระทบที่ใช้กันเดิม ยังคงมี field "lane" คืนเป็นเลนแรก (fallback)
        "lane":       first_lane    or second_lane or "Mid",
    }

# ---------------------------- Helper Functions ------------------------------
def safe_float(value: Any) -> float:
    """Convert a value to float, defaulting to 0.0 if None."""
    return float(value or 0.0)

STAT_MAPPING = [
    ('patk', 'Phys_ATK'),
    ('ap', 'Magic_Power'),
    ('def', 'Phys_Defense'),
    ('hp', 'HP'),
    ('cdr', 'Cooldown_Reduction'),
    ('crit', 'Critical_Rate'),
    ('ms', 'Movement_Speed'),
]

def get_phase_weight(hero_info: Dict[str, Optional[str]], phase: str) -> Dict[str, float]:
    """Calculate stat weights based on phase and lane."""
    weights = {'patk': 0.30, 'ap': 0.20, 'def': 0.20, 'hp': 0.20, 'cdr': 0.05, 'crit': 0.05, 'ms': 0.05}
    if phase == 'Early':
        weights['cdr'] += 0.05
    if phase == 'Late':
        weights['hp'] += 0.10
    if hero_info['lane'] == 'Support':
        weights['hp'] += 0.05
        weights['cdr'] += 0.05
    return weights

def score_stats(chromosome: List[str], hero_base_stats: Dict[str, float],
                stat_caps: Dict[str, float], weights: Dict[str, float]) -> float:
    """Score chromosome stats relative to caps and weights."""
    stats = {short: safe_float(hero_base_stats.get(db_name)) for short, db_name in STAT_MAPPING}
    for item_id in chromosome:
        item = ITEM_DATA[item_id]
        for short, db_name in STAT_MAPPING:
            stats[short] += item.get(db_name, 0.0)
    return sum(weights[stat] * min(stats[stat] / stat_caps.get(stat.upper(), 1), 1.0) for stat in stats)

def score_budget(total_cost: float, budget: float) -> float:
    """Score budget usage with exponential decay penalty."""
    return 1.0 if total_cost <= budget else math.exp(-0.8 * ((total_cost - budget) / budget))

def skill_component(chromosome: List[str], recommended_types: List[str]) -> float:
    """Score skill synergy based on recommended item types."""
    return sum(0.2 for item_id in chromosome if ITEM_DATA[item_id]['Class'] in recommended_types)

def synergy_component(chromosome: List[str]) -> float:
    """Score synergy bonuses from item combinations."""
    return sum(value for required_items, value in SYNERGY_RULES if required_items <= set(chromosome))

def category_component(chromosome: List[str], category: str) -> float:
    """Score items matching a specific category."""
    return sum(1 for item_id in chromosome if ITEM_DATA[item_id]['Class'] == category)

def class_component(chromosome: List[str], hero_info: Dict[str, Optional[str]]) -> float:
    """Score items matching hero's primary class."""
    return sum(1 for item_id in chromosome if ITEM_DATA[item_id]['Class'] == hero_info['primary'])

def lane_component(chromosome: List[str], hero_info: Dict[str, Optional[str]]) -> float:
    """Score items matching any of hero's lanes."""
    # ใช้ info['lanes'] (list) แทน info['lane']
    lanes = hero_info.get('lanes', [hero_info.get('lane')])
    return sum(
        1
        for item_id in chromosome
        if ITEM_DATA[item_id]['Class'] in lanes
    )


# ---------------------------- Chromosome Operations -------------------------
def repair_chromosome(chromosome: List[str], lane: str, banned_items: Set[str],
                      forced_items: Set[str]) -> List[str]:
    """Repair chromosome to enforce rules: forced items, ≤1 Movement, respect bans, exactly 6 items."""
    result = []
    seen_items = set()
    movement_count = 0

    # Add forced items first
    for item_id in forced_items:
        if item_id in banned_items or item_id in seen_items:
            continue
        result.append(item_id)
        seen_items.add(item_id)
        if ITEM_DATA[item_id]['Class'] == 'Movement':
            movement_count += 1

    # Keep valid items from original chromosome
    for item_id in chromosome:
        if len(result) >= 6:
            break
        if item_id in banned_items or item_id in seen_items or item_id in forced_items:
            continue
        if ITEM_DATA[item_id]['Class'] == 'Movement' and movement_count >= 1:
            continue
        result.append(item_id)
        seen_items.add(item_id)
        if ITEM_DATA[item_id]['Class'] == 'Movement':
            movement_count += 1

    # Fill remaining slots randomly
    available_items = [
        item_id for item_id in ITEM_DATA
        if item_id not in seen_items and item_id not in banned_items and
        not (ITEM_DATA[item_id]['Class'] == 'Movement' and movement_count >= 1)
    ]
    random.shuffle(available_items)
    result.extend(available_items[:max(0, 6 - len(result))])

    # Ensure at least one Jungle item if lane is Jungle
    if lane == 'Jungle' and not any(ITEM_DATA[item_id]['Class'] == 'Jungle' for item_id in result):
        jungle_items = [item_id for item_id in available_items if ITEM_DATA[item_id]['Class'] == 'Jungle']
        if jungle_items:
            result[-1] = random.choice(jungle_items)

    return result[:6]

# ---------------------------- Genetic Operators -----------------------------
def tournament_selection(population: List[List[str]], fitness_scores: List[float],
                         tournament_size: int = 3) -> List[str]:
    """Select a chromosome via tournament selection."""
    indices = random.sample(range(len(population)), tournament_size)
    return population[max(indices, key=lambda i: fitness_scores[i])]

def crossover(parent1: List[str], parent2: List[str]) -> Tuple[List[str], List[str]]:
    """Perform single-point crossover between two parents."""
    if random.random() < GA_CONSTANTS['CROSSOVER_RATE']:
        point = random.randint(1, 5)
        return parent1[:point] + parent2[point:], parent2[:point] + parent1[point:]
    return parent1[:], parent2[:]

def mutate(chromosome: List[str], item_pool: List[str], mutation_rate: float, lane: str,
           banned_items: Set[str], forced_items: Set[str]) -> List[str]:
    """Mutate a chromosome with given probability."""
    result = chromosome[:]
    available = [item_id for item_id in item_pool if item_id not in result and item_id not in banned_items]
    for i in range(6):
        if result[i] in forced_items:
            continue
        if random.random() < mutation_rate and available:
            result[i] = random.choice(available)
            available.remove(result[i])
    return repair_chromosome(result, lane, banned_items, forced_items)

def get_adaptive_mutation_rate(generation: int) -> float:
    """Calculate adaptive mutation rate based on generation."""
    return GA_CONSTANTS['BASE_MUT_RATE'] * math.exp(-generation / (0.6 * GA_CONSTANTS['MAX_GEN']))

# ---------------------------- Fitness Evaluation ----------------------------
def calculate_fitness(chromosome: List[str], hero: str, hero_info: Dict[str, Optional[str]],
                      phase: str, stat_caps: Dict[str, float]) -> float:
    """Calculate fitness score for a chromosome."""
    hero_base_stats = load_hero_stats(hero, {'Early': 3, 'Mid': 9, 'Late': 15}[phase])
    recommended_types = get_recommended_item_types(hero)
    total_cost = sum(ITEM_DATA[item_id]['Price'] for item_id in chromosome)
    budget = GA_CONSTANTS['BASE_BUDGET'][phase]

    components = {
        'stat': score_stats(chromosome, hero_base_stats, stat_caps, get_phase_weight(hero_info, phase)),
        'budget': score_budget(total_cost, budget),
        'skill': skill_component(chromosome, recommended_types),
        'synergy': synergy_component(chromosome),
        'cat': len(chromosome),
        'class': class_component(chromosome, hero_info),
        'lane': lane_component(chromosome, hero_info),
        'cat_ATK': category_component(chromosome, 'ATK'),
        'cat_Def': category_component(chromosome, 'Def'),
        'cat_Magic': category_component(chromosome, 'Magic'),
    }

    raw_score = sum(THETA[component] * value for component, value in components.items())
    return raw_score * GA_CONSTANTS['PHASE_WEIGHTS'][phase]

# ---------------------------- GA Main Loop ----------------------------------
def initialize_population(item_pool: List[str], lane: str, banned_items: Set[str],
                          forced_items: Set[str]) -> List[List[str]]:
    """Initialize the GA population."""
    def generate_chromosome() -> List[str]:
        base = list(forced_items)
        remaining = random.sample([item_id for item_id in item_pool if item_id not in base],
                                  k=max(0, 6 - len(base)))
        return repair_chromosome(base + remaining, lane, banned_items, forced_items)
    return [generate_chromosome() for _ in range(GA_CONSTANTS['POP_SIZE'])]

def run_ga(hero: str, lane: str, hero_class: Optional[str] = None,
           force_items: Optional[List[str]] = None, ban_items: Optional[List[str]] = None,
           phase: str = 'Late') -> Tuple[List[str], float]:
    """Run the Genetic Algorithm to find the best item build."""
    forced_items = set(force_items or [])
    banned_items = set(ban_items or [])
    hero_info = get_hero_info(hero)
    hero_info['lane'] = lane
    if hero_class:
        hero_info['primary'] = hero_class

    if sum(1 for item_id in forced_items if ITEM_DATA[item_id]['Class'] == 'Movement') > 1:
        raise ValueError('More than one Movement item in --force')

    PHASE_BUFFERS = {'Early': 0.10, 'Mid': 0.20, 'Late': 0.30}
    stat_caps = load_stat_caps(hero, buffer=PHASE_BUFFERS[phase])
    item_pool = [item_id for item_id in ITEM_DATA if item_id not in banned_items]

    # Population Initialization
    population = initialize_population(item_pool, lane, banned_items, forced_items)

    best_fitness, best_chromosome, stagnant_count = -1.0, [], 0
    for generation in range(GA_CONSTANTS['MAX_GEN']):
        # Objective Function Evaluation
        fitness_scores = [calculate_fitness(chrom, hero, hero_info, phase, stat_caps) for chrom in population]
        best_idx = max(range(len(fitness_scores)), key=lambda i: fitness_scores[i])

        # Update best solution
        if fitness_scores[best_idx] > best_fitness:
            best_fitness = fitness_scores[best_idx]
            best_chromosome = population[best_idx][:]
            stagnant_count = 0
        else:
            stagnant_count += 1
        if stagnant_count >= GA_CONSTANTS['STAGNANT_LIMIT']:
            break

        # Selection and Replacement
        elites = [chrom for chrom, _ in sorted(zip(population, fitness_scores), key=lambda x: -x[1])]
        elites = elites[:max(1, int(GA_CONSTANTS['POP_SIZE'] * 0.05))]
        new_population = elites[:]

        # Generate offspring
        while len(new_population) < GA_CONSTANTS['POP_SIZE']:
            parent1 = tournament_selection(population, fitness_scores)
            parent2 = tournament_selection(population, fitness_scores)
            child1, child2 = crossover(parent1, parent2)
            mutation_rate = get_adaptive_mutation_rate(generation)
            new_population.append(mutate(child1, item_pool, mutation_rate, lane, banned_items, forced_items))
            if len(new_population) < GA_CONSTANTS['POP_SIZE']:
                new_population.append(mutate(child2, item_pool, mutation_rate, lane, banned_items, forced_items))

        # Replacement (g = g + 1)
        population = new_population

    return best_chromosome, best_fitness

# ---------------------------- CLI -------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RoV GA-based Item Recommender')
    parser.add_argument('--hero', required=True, help='Hero ID')
    parser.add_argument('--class', dest='hero_class', required=True, help='Hero class')
    parser.add_argument('--lane', required=True, help='Lane')
    parser.add_argument('--force', nargs='*', default=None, help='Forced ItemIDs')
    parser.add_argument('--ban', nargs='*', default=None, help='Banned ItemIDs')
    args = parser.parse_args()

    load_theta_config()

    for phase in ['Early', 'Mid', 'Late']:
        build, fitness = run_ga(
            hero=args.hero,
            lane=args.lane,
            hero_class=args.hero_class,
            force_items=args.force,
            ban_items=args.ban,
            phase=phase,
        )
        print(f'{phase:<5} Build={build} | Fitness={fitness:.4f}')
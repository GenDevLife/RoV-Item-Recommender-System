from __future__ import annotations
import random
import math
import argparse
from typing import Dict, List, Tuple, Optional, Set

import config
import database
import utils
from config import THETA, GA_CONSTANTS
from database import ITEM_DATA

# ---------------------------- Helper Functions ------------------------------

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
    stats = {short: utils.safe_float(hero_base_stats.get(db_name)) for short, db_name in utils.STAT_MAPPING}
    for item_id in chromosome:
        item = ITEM_DATA[item_id]
        for short, db_name in utils.STAT_MAPPING:
            stats[short] += item.get(db_name, 0.0)
    return sum(weights[stat] * min(stats[stat] / stat_caps.get(stat.upper(), 1), 1.0) for stat in stats)

def score_budget(total_cost: float, budget: float) -> float:
    """Score budget usage with exponential decay penalty."""
    return 1.0 if total_cost <= budget else math.exp(-0.8 * ((total_cost - budget) / budget))

def skill_component(chromosome: List[str], recommended_types: List[str]) -> float:
    """Score skill synergy based on recommended item types."""
    return sum(0.2 for item_id in chromosome if ITEM_DATA[item_id]['Class'] in recommended_types)

def category_component(chromosome: List[str], category: str) -> float:
    """Score items matching a specific category."""
    return sum(1 for item_id in chromosome if ITEM_DATA[item_id]['Class'] == category)

def class_component(chromosome: List[str], hero_info: Dict[str, Optional[str]]) -> float:
    """Score items matching hero's primary class."""
    class_mapping = {
        'Fighter': ['Attack', 'Defense'],
        'Mage': ['Magic'],
        'Support': ['Support'],
        'Tank': ['Defense'],
        'Assassin': ['Attack', 'Jungle'],
        'Carry': ['Attack']
    }
    suitable_classes = class_mapping.get(hero_info['primary'], [])
    return sum(1 for item_id in chromosome if ITEM_DATA[item_id]['Class'] in suitable_classes)

def lane_component(chromosome: List[str], hero_info: Dict[str, Optional[str]]) -> float:
    """Score items matching hero's lanes based on a mapping."""
    lane_mapping = {
        'Mid': ['Magic'],
        'Support': ['Support', 'Defense'],
        'Farm': ['Jungle'],
        'Dark Slayer': ['Attack'],
        'Dragon Slayer': ['Attack']
    }
    lanes = hero_info.get('lanes', [hero_info.get('lane')])
    suitable_classes = set()
    for lane in lanes:
        suitable_classes.update(lane_mapping.get(lane, []))
    return sum(1 for item_id in chromosome if ITEM_DATA[item_id]['Class'] in suitable_classes)


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
    hero_base_stats = database.load_hero_stats(hero, {'Early': 3, 'Mid': 9, 'Late': 15}[phase])
    recommended_types = database.get_recommended_item_types(hero)
    total_cost = sum(ITEM_DATA[item_id]['Price'] for item_id in chromosome)
    budget = GA_CONSTANTS['BASE_BUDGET'][phase]

    components = {
        'stat': score_stats(chromosome, hero_base_stats, stat_caps, get_phase_weight(hero_info, phase)),
        'budget': score_budget(total_cost, budget),
        'skill': skill_component(chromosome, recommended_types),
        'cat': len(chromosome),
        'class': class_component(chromosome, hero_info),
        'lane': lane_component(chromosome, hero_info),
        'cat_ATK': category_component(chromosome, 'Attack'),
        'cat_Def': category_component(chromosome, 'Defense'),
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
    hero_info = database.get_hero_info(hero)
    hero_info['lane'] = lane
    if hero_class:
        hero_info['primary'] = hero_class

    if sum(1 for item_id in forced_items if ITEM_DATA[item_id]['Class'] == 'Movement') > 1:
        raise ValueError('More than one Movement item in --force')

    PHASE_BUFFERS = {'Early': 0.10, 'Mid': 0.20, 'Late': 0.30}
    stat_caps = database.load_stat_caps(hero, phase, buffer=PHASE_BUFFERS[phase])
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

    config.load_theta_config()

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

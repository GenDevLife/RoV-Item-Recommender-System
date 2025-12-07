"""
GA Parameter Tuning Script
ทดสอบการตั้งค่า GA ต่างๆ เพื่อหาค่าที่ดีที่สุด
"""
import sys
import os
import time
import json
from typing import Dict, List, Tuple
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator
from app.core.ga_engine import GeneticEngine
from app.config import DB_PATH, GA_SETTINGS

# =========================================
# Test Configurations
# =========================================
TEST_CONFIGS = [
    # Baseline (current settings)
    {"name": "Baseline", "POP_SIZE": 50, "MAX_GEN": 100, "MUTATION_RATE": 0.2, "ELITISM_COUNT": 2},
    
    # Test Population Size
    {"name": "Small Pop", "POP_SIZE": 20, "MAX_GEN": 100, "MUTATION_RATE": 0.2, "ELITISM_COUNT": 2},
    {"name": "Large Pop", "POP_SIZE": 100, "MAX_GEN": 100, "MUTATION_RATE": 0.2, "ELITISM_COUNT": 2},
    
    # Test Generations
    {"name": "Quick (50 gen)", "POP_SIZE": 50, "MAX_GEN": 50, "MUTATION_RATE": 0.2, "ELITISM_COUNT": 2},
    {"name": "Deep (200 gen)", "POP_SIZE": 50, "MAX_GEN": 200, "MUTATION_RATE": 0.2, "ELITISM_COUNT": 2},
    
    # Test Mutation Rate
    {"name": "Low Mutation", "POP_SIZE": 50, "MAX_GEN": 100, "MUTATION_RATE": 0.1, "ELITISM_COUNT": 2},
    {"name": "High Mutation", "POP_SIZE": 50, "MAX_GEN": 100, "MUTATION_RATE": 0.3, "ELITISM_COUNT": 2},
    {"name": "Very High Mutation", "POP_SIZE": 50, "MAX_GEN": 100, "MUTATION_RATE": 0.5, "ELITISM_COUNT": 2},
    
    # Test Elitism
    {"name": "No Elitism", "POP_SIZE": 50, "MAX_GEN": 100, "MUTATION_RATE": 0.2, "ELITISM_COUNT": 0},
    {"name": "High Elitism", "POP_SIZE": 50, "MAX_GEN": 100, "MUTATION_RATE": 0.2, "ELITISM_COUNT": 5},
    
    # Optimized Combinations
    {"name": "Fast & Furious", "POP_SIZE": 30, "MAX_GEN": 50, "MUTATION_RATE": 0.3, "ELITISM_COUNT": 3},
    {"name": "Slow & Steady", "POP_SIZE": 80, "MAX_GEN": 150, "MUTATION_RATE": 0.15, "ELITISM_COUNT": 4},
]

# Test Heroes (different roles)
TEST_HEROES = ["valhein", "tachi", "yue"]
RUNS_PER_CONFIG = 3  # รันหลายครั้งเพื่อหาค่าเฉลี่ย

# =========================================
# Helper Functions
# =========================================
def run_ga_with_config(hero_data, all_items, valid_items, config: Dict) -> Tuple[float, float, List[int]]:
    """รัน GA ด้วย config ที่กำหนด"""
    # Override GA_SETTINGS temporarily
    original_settings = GA_SETTINGS.copy()
    
    GA_SETTINGS['POP_SIZE'] = config['POP_SIZE']
    GA_SETTINGS['MAX_GEN'] = config['MAX_GEN']
    GA_SETTINGS['MUTATION_RATE'] = config['MUTATION_RATE']
    GA_SETTINGS['ELITISM_COUNT'] = config['ELITISM_COUNT']
    
    # Run GA
    evaluator = BuildEvaluator(hero_data, all_items)
    engine = GeneticEngine(evaluator, valid_items)
    
    start_time = time.time()
    best_build, fitness = engine.run()
    elapsed_time = time.time() - start_time
    
    # Restore original settings
    for key, value in original_settings.items():
        GA_SETTINGS[key] = value
    
    return fitness, elapsed_time, best_build

# =========================================
# Main Tuning Process
# =========================================
def tune_ga_parameters():
    print("🔧 GA Parameter Tuning Started")
    print("=" * 80)
    
    # Load data
    repo = RoVRepository(DB_PATH)
    all_items = repo.get_all_items()
    valid_items = [k for k, v in all_items.items() if v.get('tier') == 3]
    
    print(f"📦 Loaded {len(all_items)} items ({len(valid_items)} Tier 3)")
    print(f"🎮 Testing {len(TEST_CONFIGS)} configurations")
    print(f"🧪 {RUNS_PER_CONFIG} runs per config × {len(TEST_HEROES)} heroes")
    print(f"⏱️  Total runs: {len(TEST_CONFIGS) * RUNS_PER_CONFIG * len(TEST_HEROES)}")
    print("=" * 80)
    
    results = []
    
    for config_idx, config in enumerate(TEST_CONFIGS, 1):
        print(f"\n[{config_idx}/{len(TEST_CONFIGS)}] Testing: {config['name']}")
        print(f"  Settings: Pop={config['POP_SIZE']}, Gen={config['MAX_GEN']}, " +
              f"Mut={config['MUTATION_RATE']}, Elite={config['ELITISM_COUNT']}")
        
        config_results = {
            'config_name': config['name'],
            'pop_size': config['POP_SIZE'],
            'max_gen': config['MAX_GEN'],
            'mutation_rate': config['MUTATION_RATE'],
            'elitism_count': config['ELITISM_COUNT'],
            'fitness_scores': [],
            'execution_times': []
        }
        
        for hero_name in TEST_HEROES:
            hero_data = repo.get_hero_data(hero_name)
            
            for run in range(RUNS_PER_CONFIG):
                fitness, exec_time, build = run_ga_with_config(
                    hero_data, all_items, valid_items, config
                )
                
                config_results['fitness_scores'].append(fitness)
                config_results['execution_times'].append(exec_time)
                
                print(f"    {hero_name} run {run+1}: Fitness={fitness:.2f}, Time={exec_time:.2f}s")
        
        # Calculate statistics
        import numpy as np
        config_results['avg_fitness'] = np.mean(config_results['fitness_scores'])
        config_results['std_fitness'] = np.std(config_results['fitness_scores'])
        config_results['avg_time'] = np.mean(config_results['execution_times'])
        config_results['std_time'] = np.std(config_results['execution_times'])
        
        results.append(config_results)
        
        print(f"  ✓ Avg Fitness: {config_results['avg_fitness']:.2f} (±{config_results['std_fitness']:.2f})")
        print(f"  ✓ Avg Time: {config_results['avg_time']:.2f}s (±{config_results['std_time']:.2f})")
    
    # =========================================
    # Analysis & Reporting
    # =========================================
    print("\n" + "=" * 80)
    print("📊 RESULTS SUMMARY")
    print("=" * 80)
    
    # Create DataFrame for easier analysis
    df = pd.DataFrame([{
        'Config': r['config_name'],
        'Pop Size': r['pop_size'],
        'Generations': r['max_gen'],
        'Mutation': r['mutation_rate'],
        'Elitism': r['elitism_count'],
        'Avg Fitness': r['avg_fitness'],
        'Std Fitness': r['std_fitness'],
        'Avg Time (s)': r['avg_time'],
        'Std Time (s)': r['std_time']
    } for r in results])
    
    # Sort by fitness (descending)
    df_sorted = df.sort_values('Avg Fitness', ascending=False)
    
    print("\n🏆 TOP 5 CONFIGURATIONS (by Fitness):")
    print("-" * 80)
    print(df_sorted.head(5).to_string(index=False))
    
    print("\n⚡ TOP 5 FASTEST CONFIGURATIONS (by Time):")
    print("-" * 80)
    df_fastest = df.sort_values('Avg Time (s)')
    print(df_fastest.head(5).to_string(index=False))
    
    # Find best balance (high fitness, low time)
    df['Efficiency'] = df['Avg Fitness'] / df['Avg Time (s)']
    df_efficient = df.sort_values('Efficiency', ascending=False)
    
    print("\n⚖️  BEST EFFICIENCY (Fitness/Time):")
    print("-" * 80)
    print(df_efficient.head(5).to_string(index=False))
    
    # Save results
    output_file = os.path.join(PROJECT_ROOT, 'results', 'ga_tuning_results.csv')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")
    
    # Save detailed JSON
    json_file = os.path.join(PROJECT_ROOT, 'results', 'ga_tuning_detailed.json')
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"💾 Detailed results saved to: {json_file}")
    
    # Recommendation
    best_config = df_sorted.iloc[0]
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATION:")
    print("=" * 80)
    print(f"Best Overall Configuration: {best_config['Config']}")
    print(f"  - Population Size: {int(best_config['Pop Size'])}")
    print(f"  - Generations: {int(best_config['Generations'])}")
    print(f"  - Mutation Rate: {best_config['Mutation']}")
    print(f"  - Elitism Count: {int(best_config['Elitism'])}")
    print(f"  - Expected Fitness: {best_config['Avg Fitness']:.2f}")
    print(f"  - Expected Time: {best_config['Avg Time (s)']:.2f}s")
    
    print("\n✅ Tuning Complete!")

if __name__ == "__main__":
    import numpy as np  # Import here to avoid issues if not installed
    tune_ga_parameters()

"""
Compare GA Profiles (Default, Fast, Quality)
แสดงความแตกต่างของแต่ละ profile
"""
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator
from app.core.ga_engine import GeneticEngine
from app.config import DB_PATH, GA_SETTINGS_FAST, GA_SETTINGS, GA_SETTINGS_QUALITY

# Test configurations
PROFILES = {
    "Default (Balanced)": GA_SETTINGS,
    "Fast (Production)": GA_SETTINGS_FAST,
    "Quality (Research)": GA_SETTINGS_QUALITY
}

TEST_HEROES = ["valhein", "tachi", "yue"]
RUNS = 5

def test_profile(profile_name, settings, hero_data, all_items, valid_items):
    """ทดสอบ profile หนึ่งตัว"""
    results = []
    
    print(f"\n{'='*60}")
    print(f"Testing: {profile_name}")
    print(f"Settings: Pop={settings['POP_SIZE']}, Gen={settings['MAX_GEN']}, " +
          f"Mut={settings['MUTATION_RATE']}, Elite={settings['ELITISM_COUNT']}")
    print(f"{'='*60}")
    
    for hero_name in TEST_HEROES:
        hero = repo.get_hero_data(hero_name)
        
        run_fitness = []
        run_times = []
        
        for run in range(RUNS):
            # Override GA_SETTINGS
            from app import config
            original = config.GA_SETTINGS.copy()
            config.GA_SETTINGS.update(settings)
            
            evaluator = BuildEvaluator(hero, all_items)
            engine = GeneticEngine(evaluator, valid_items)
            
            start = time.time()
            build, fitness = engine.run()
            elapsed = time.time() - start
            
            run_fitness.append(fitness)
            run_times.append(elapsed)
            
            # Restore
            config.GA_SETTINGS.update(original)
        
        avg_fitness = sum(run_fitness) / len(run_fitness)
        avg_time = sum(run_times) / len(run_times)
        
        print(f"  {hero_name:10s}: Fitness={avg_fitness:6.2f}, Time={avg_time:.3f}s")
        
        results.append({
            'hero': hero_name,
            'avg_fitness': avg_fitness,
            'avg_time': avg_time
        })
    
    overall_fitness = sum(r['avg_fitness'] for r in results) / len(results)
    overall_time = sum(r['avg_time'] for r in results) / len(results)
    
    print(f"\n  📊 Overall: Fitness={overall_fitness:.2f}, Time={overall_time:.3f}s")
    
    return overall_fitness, overall_time

if __name__ == "__main__":
    print("🔍 GA Profile Comparison")
    print("="*70)
    
    # Load data
    repo = RoVRepository(DB_PATH)
    all_items = repo.get_all_items()
    valid_items = [k for k, v in all_items.items() if v.get('tier') == 3]
    
    print(f"📦 Loaded {len(all_items)} items ({len(valid_items)} Tier 3)")
    print(f"🧪 Testing {len(PROFILES)} profiles × {len(TEST_HEROES)} heroes × {RUNS} runs")
    
    comparison = {}
    
    for profile_name, settings in PROFILES.items():
        fitness, time_taken = test_profile(
            profile_name, settings, None, all_items, valid_items
        )
        comparison[profile_name] = {
            'fitness': fitness,
            'time': time_taken
        }
    
    # Final comparison
    print("\n" + "="*70)
    print("📊 FINAL COMPARISON")
    print("="*70)
    
    baseline = comparison["Default (Balanced)"]
    
    for profile_name, results in comparison.items():
        fitness_diff = ((results['fitness'] - baseline['fitness']) / baseline['fitness']) * 100
        time_ratio = baseline['time'] / results['time']
        
        print(f"\n{profile_name}:")
        print(f"  Fitness: {results['fitness']:.2f} ({fitness_diff:+.2f}% vs Baseline)")
        print(f"  Time:    {results['time']:.3f}s ({time_ratio:.2f}x)")
        print(f"  Efficiency: {results['fitness'] / results['time']:.0f}")
    
    # Recommendation
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS:")
    print("="*70)
    print("🚀 Fast Profile: Best for real-time web apps, mobile apps")
    print("⚖️  Default Profile: Good balance for general use")
    print("🔬 Quality Profile: Best for research, offline analysis")
    print("\nChange profile in app/config.py: GA_PROFILE = 'fast' | 'default' | 'quality'")

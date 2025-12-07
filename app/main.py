# main.py - CLI หลักสำหรับระบบแนะนำไอเทม RoV
import sys
import os
import time
from typing import List, Dict, Tuple
import pandas as pd
from tqdm import tqdm
import questionary
from questionary import Style

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.config import DB_PATH, get_ga_settings
from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator
from app.core.ga_engine import GeneticEngine
from app.utils.logger import logger

# Style สำหรับ questionary menu
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])

class RoVRecommender:
    """คลาสหลักสำหรับระบบแนะนำไอเทม"""
    
    def __init__(self):
        logger.info("Initializing RoV Item Recommender...")
        try:
            self.repo = RoVRepository(DB_PATH)
            self.all_items = self.repo.get_all_items()
            self.valid_items = [k for k, v in self.all_items.items() if v.get('tier') == 3]
            logger.info(f"Loaded {len(self.all_items)} items ({len(self.valid_items)} Tier 3)")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
    
    def get_recommendation(self, hero_code: str, role: str = None, lane: str = None, 
                          ga_profile: str = "medium") -> Tuple[List[int], float, Dict]:
        """สร้าง build recommendation สำหรับ hero"""
        hero_data = self.repo.get_hero_data(hero_code)
        if not hero_data:
            raise ValueError(f"Hero '{hero_code}' not found")
        
        if role:
            hero_data['selected_role'] = role
        if lane:
            hero_data['selected_lane'] = lane
            
        ga_settings = get_ga_settings(ga_profile)
        evaluator = BuildEvaluator(hero_data, self.all_items)
        engine = GeneticEngine(evaluator, self.valid_items, ga_settings)
        build, score = engine.run()
        return build, score, hero_data
    
    def format_build_output(self, build: List[int], hero_data: Dict, score: float, 
                           role: str = None, lane: str = None, ga_profile: str = None) -> str:
        """แสดงผล build ในรูปแบบที่อ่านง่าย"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"Recommended Build for {hero_data.get('name_en', hero_data['code_name'])}")
        lines.append(f"Score: {score:.2f}")
        lines.append(f"Role: {role or hero_data.get('primary_role', '-')}")
        lines.append(f"Lane: {lane or hero_data.get('primary_lane', '-')}")
        lines.append(f"Damage Type: {hero_data.get('damage_type', '-')}")
        lines.append("=" * 70)
        
        total_cost = 0
        for i, item_id in enumerate(build, 1):
            item = self.all_items[item_id]
            lines.append(f"[{i}] {item['name_en']:<30} ({item['price']:>5}g)")
            total_cost += item['price']
            
        lines.append("-" * 70)
        lines.append(f"Total Cost: {total_cost}g")
        
        evaluator = BuildEvaluator(hero_data, self.all_items)
        stats = evaluator.calculate_stats(build)
        lines.append(f"Stats: AD={stats['p_atk']:.0f}, AP={stats['m_power']:.0f}, "
                    f"HP={stats['max_hp']:.0f}, CDR={stats['cdr']*100:.0f}%")
        
        if ga_profile:
            lines.append(f"Mode: {ga_profile.upper()}")
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def get_hero_role_lane_combinations(self, hero_code: str) -> List[Tuple[str, str]]:
        """ดึง combinations ของ role x lane ที่เป็นไปได้สำหรับ hero"""
        hero_data = self.repo.get_hero_data(hero_code)
        if not hero_data:
            return []
            
        roles = []
        lanes = []
        
        if hero_data.get('primary_role'):
            roles.append(hero_data['primary_role'].strip())
        if hero_data.get('secondary_role'):
            roles.append(hero_data['secondary_role'].strip())
        if hero_data.get('primary_lane'):
            lanes.append(hero_data['primary_lane'].strip())
        if hero_data.get('secondary_lane'):
            lanes.append(hero_data['secondary_lane'].strip())
            
        return [(r, l) for r in roles for l in lanes]
    
    def analyze_all_heroes(self, ga_profile: str = "expert", 
                          output_file: str = "all_heroes_analysis.csv"):
        """วิเคราะห์ทุก hero และบันทึกลง CSV"""
        print(f"\nStarting analysis ({ga_profile.upper()} mode)...")
        
        try:
            hero_list = self.repo.get_hero_list()
            print(f"Found {len(hero_list)} heroes")
        except Exception as e:
            print(f"Error loading heroes: {e}")
            return
        
        # นับจำนวน combinations ทั้งหมด
        total_combinations = 0
        hero_combinations = {}
        for hero_code in hero_list:
            combos = self.get_hero_role_lane_combinations(hero_code)
            if combos:
                hero_combinations[hero_code] = combos
                total_combinations += len(combos)
        
        print(f"Total combinations: {total_combinations}\n")
        results = []
        
        pbar = tqdm(total=total_combinations, desc=f"Analyzing", unit="combo", 
                   ncols=100, file=sys.stdout, dynamic_ncols=False, leave=True)
        
        for hero_code, combinations in hero_combinations.items():
            for role, lane in combinations:
                try:
                    start_time = time.time()
                    build, score, hero_data = self.get_recommendation(hero_code, role, lane, ga_profile)
                    elapsed = time.time() - start_time
                    
                    evaluator = BuildEvaluator(hero_data, self.all_items)
                    stats = evaluator.calculate_stats(build)
                    items_list = [self.all_items[iid]['name_en'] for iid in build]
                    total_cost = sum(self.all_items[iid]['price'] for iid in build)
                    
                    result = {
                        'hero_code': hero_code,
                        'hero_name': hero_data.get('name_en', hero_code),
                        'role': role,
                        'lane': lane,
                        'damage_type': hero_data.get('damage_type', '-'),
                        'fitness_score': round(score, 2),
                        'ga_profile': ga_profile,
                        'item_1': items_list[0] if len(items_list) > 0 else '',
                        'item_2': items_list[1] if len(items_list) > 1 else '',
                        'item_3': items_list[2] if len(items_list) > 2 else '',
                        'item_4': items_list[3] if len(items_list) > 3 else '',
                        'item_5': items_list[4] if len(items_list) > 4 else '',
                        'item_6': items_list[5] if len(items_list) > 5 else '',
                        'total_cost': total_cost,
                        'final_p_atk': round(stats['p_atk'], 0),
                        'final_m_power': round(stats['m_power'], 0),
                        'final_hp': round(stats['max_hp'], 0),
                        'final_cdr': round(stats['cdr'] * 100, 1),
                        'time_ms': round(elapsed * 1000, 2)
                    }
                    results.append(result)
                    pbar.set_postfix_str(f"{hero_code[:6]}|{score:.0f}")
                    
                except Exception as e:
                    tqdm.write(f"Failed: {hero_code} ({role}/{lane})")
                    results.append({
                        'hero_code': hero_code, 'hero_name': hero_code,
                        'role': role, 'lane': lane, 'error': str(e)
                    })
                pbar.update(1)
        
        pbar.close()
        
        # บันทึกผล
        df = pd.DataFrame(results)
        output_path = os.path.join(PROJECT_ROOT, output_file)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"\nDone! Saved to: {output_path}")
        successful = len([r for r in results if 'error' not in r])
        print(f"Analyzed: {successful}/{total_combinations}")
        
        if results:
            ok = [r for r in results if 'error' not in r]
            if ok:
                avg_score = sum(r['fitness_score'] for r in ok) / len(ok)
                avg_time = sum(r['time_ms'] for r in ok) / len(ok)
                total_time = sum(r['time_ms'] for r in ok) / 1000
                print(f"\nSummary:")
                print(f"  Avg Score: {avg_score:.2f}")
                print(f"  Avg Time: {avg_time:.2f}ms")
                print(f"  Total Time: {total_time:.2f}s")
    
    def select_hero_mode(self):
        """โหมดเลือก hero เดี่ยว"""
        print("\n" + "=" * 70)
        print("Select Hero Mode")
        print("=" * 70)
        
        try:
            hero_list = self.repo.get_hero_list()
        except Exception as e:
            logger.error(f"Failed to load heroes: {e}")
            return
        
        hero_code = questionary.select("Select hero:", 
                                       choices=sorted(hero_list), 
                                       style=custom_style).ask()
        if not hero_code:
            return
        
        hero_data = self.repo.get_hero_data(hero_code)
        if not hero_data:
            print(f"Hero '{hero_code}' not found")
            return
        
        # เลือก role
        roles = []
        if hero_data.get('primary_role'):
            roles.append(hero_data['primary_role'].strip())
        if hero_data.get('secondary_role'):
            sec = hero_data['secondary_role'].strip()
            if sec not in roles:
                roles.append(sec)
        
        if not roles:
            print(f"No roles for {hero_code}")
            return
        
        selected_role = questionary.select(
            f"Select Role for {hero_data.get('name_en', hero_code)}:",
            choices=roles, style=custom_style
        ).ask()
        if not selected_role:
            return
        
        # เลือก lane
        lanes = []
        if hero_data.get('primary_lane'):
            lanes.append(hero_data['primary_lane'].strip())
        if hero_data.get('secondary_lane'):
            sec = hero_data['secondary_lane'].strip()
            if sec not in lanes:
                lanes.append(sec)
        
        if not lanes:
            print(f"No lanes for {hero_code}")
            return
        
        selected_lane = questionary.select(
            f"Select Lane for {hero_data.get('name_en', hero_code)}:",
            choices=lanes, style=custom_style
        ).ask()
        if not selected_lane:
            return
        
        # เลือก AI mode
        ga_choice = questionary.select("Select AI Mode:", choices=[
            "Fast (50 gen)",
            "Medium (100 gen) *DEFAULT*",
            "Expert (150 gen)"
        ], style=custom_style, default="Medium (100 gen) *DEFAULT*").ask()
        
        if not ga_choice:
            return
        
        profile_map = {
            "Fast (50 gen)": "fast",
            "Medium (100 gen) *DEFAULT*": "medium",
            "Expert (150 gen)": "expert"
        }
        selected_profile = profile_map[ga_choice]
        print(f"\nCalculating... ({selected_profile.upper()} mode)")
        
        try:
            start_time = time.time()
            build, score, hero_data = self.get_recommendation(
                hero_code, selected_role, selected_lane, selected_profile
            )
            elapsed = time.time() - start_time
            print("\n" + self.format_build_output(
                build, hero_data, score, selected_role, selected_lane, selected_profile
            ))
            print(f"\nTime: {elapsed*1000:.2f}ms")
        except Exception as e:
            logger.error(f"Failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    print("\n" + "=" * 50)
    print("   RoV Item Recommender System")
    print("   Powered by Genetic Algorithm")
    print("=" * 50 + "\n")
    
    try:
        app = RoVRecommender()
    except Exception as e:
        logger.error(f"Init failed: {e}")
        sys.exit(1)
    
    mode = questionary.select("Choose mode:", choices=[
        "All Heroes (batch analysis)",
        "Select Hero (single hero)",
        "Exit"
    ], style=custom_style).ask()
    
    if not mode or mode == "Exit":
        print("\nBye!\n")
        return
    
    if mode.startswith("All"):
        print("\n" + "=" * 50)
        print("ALL HEROES MODE")
        print("=" * 50)
        print("Analyze all heroes with all role-lane combinations.")
        print("Using EXPERT mode for best quality.\n")
        
        confirm = questionary.confirm("Continue?", default=True, style=custom_style).ask()
        if confirm:
            output_file = questionary.text(
                "Output filename:", 
                default="all_heroes_analysis.csv",
                style=custom_style
            ).ask()
            if output_file:
                app.analyze_all_heroes("expert", output_file)
    
    elif mode.startswith("Select"):
        while True:
            app.select_hero_mode()
            again = questionary.confirm("Analyze another?", default=False, 
                                       style=custom_style).ask()
            if not again:
                print("\nBye!\n")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
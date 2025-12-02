# app/main.py
import argparse
import sys
import os
from app.config import DB_PATH
from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator
from app.core.ga_engine import GeneticEngine

def main():
    parser = argparse.ArgumentParser(description="RoV AI Item Recommender (CLI)")
    parser.add_argument("hero", type=str, help="Hero Name (e.g. Valhein)")
    parser.add_argument("--db", type=str, default=DB_PATH, help="Path to SQLite DB")
    args = parser.parse_args()

    print(f"🔄 Loading Database: {args.db}...")
    try:
        repo = RoVRepository(args.db)
        all_items = repo.get_all_items()
        hero_data = repo.get_hero_data(args.hero)
        
        if not hero_data:
            print(f"❌ Hero '{args.hero}' not found.")
            return

        print(f"✅ Hero Found: {hero_data['code_name']} (Role: {hero_data['primary_role']})")
        print("🤖 AI is thinking... (Running GA)")

        # เตรียม Engine
        evaluator = BuildEvaluator(hero_data, all_items)
        # กรองเฉพาะของ Tier 3 มาสุ่ม (เพื่อความเร็วและสมจริง)
        valid_items = [k for k, v in all_items.items() if v.get('tier') == 3]
        
        engine = GeneticEngine(evaluator, valid_items)
        
        # Run GA
        best_build, score = engine.run()
        
        print("\n" + "="*40)
        print(f"🏆 Recommended Build for {hero_data['code_name']}")
        print(f"⭐ Fitness Score: {score:.2f}")
        print("="*40)
        
        total_price = 0
        for i, item_id in enumerate(best_build, 1):
            item = all_items[item_id]
            print(f"[{i}] {item['name_en']} ({item['price']}g)")
            total_price += item['price']
            
        print("-" * 40)
        print(f"💰 Total Cost: {total_price}g")
        
        # แสดง Stat สรุป (Optional)
        final_stats = evaluator.calculate_stats(best_build)
        print(f"📊 Final Stats: AD={final_stats['p_atk']:.0f}, AP={final_stats['m_power']:.0f}, HP={final_stats['max_hp']:.0f}, CDR={final_stats['cdr']*100:.0f}%")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
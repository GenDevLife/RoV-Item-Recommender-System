# app/core/evaluator.py
import random
import json
import os
from typing import List, Dict, Tuple
from app.config import STATS_CAPS, PENALTIES
from app.core.passive_manager import PassiveManager

class BuildEvaluator:
    def __init__(self, hero_data: Dict, all_items: Dict[int, Dict]):
        self.hero = hero_data
        self.all_items = all_items
        self.passive_manager = PassiveManager()
        
        # โหลด Learned Weights จาก Calibration (ถ้ามี)
        self.weights = self._load_weights(hero_data.get('damage_type', 'Physical'))

    def _load_weights(self, damage_type: str) -> Dict[str, float]:
        """โหลด Weights จาก learned_weights.json หรือใช้ default"""
        weights_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'core', 
            'learned_weights.json'
        )
        
        # ลองโหลดจากไฟล์ก่อน
        if os.path.exists(weights_path):
            try:
                with open(weights_path, 'r') as f:
                    learned = json.load(f)
                    print(f"✅ Loaded learned weights from calibration")
                    # Map learned weights ให้ตรงกับ key ที่ใช้ใน get_fitness
                    return {
                        'p_atk': learned.get('p_atk', 0),
                        'ap': learned.get('m_power', 0),  # m_power -> ap
                        'hp': learned.get('max_hp', 0),
                        'p_def': learned.get('p_def', 0),
                        'cdr': learned.get('cdr', 0),
                        'aspd': learned.get('aspd', 0),
                        'crit': learned.get('crit_rate', 0),  # crit_rate -> crit
                        'p_pierce': learned.get('p_pierce_percent', 0),
                        'm_pierce': learned.get('m_pierce_percent', 0),
                        'move_speed': learned.get('move_speed', 0)
                    }
            except Exception as e:
                print(f"⚠️ Error loading weights: {e}, using default")
        
        # Fallback: ใช้ weights แบบเก่าตาม role
        print(f"📌 Using default role-based weights for {damage_type}")
        return self._get_role_weights(damage_type)

    def _get_role_weights(self, damage_type: str) -> Dict[str, float]:
        """กำหนดน้ำหนักคะแนนตามประเภทดาเมจ (Logic พื้นฐาน - Fallback)"""
        if damage_type == 'Magic':
            return {
                'ap': 1.0, 'hp': 0.1, 'cdr': 50.0, 
                'm_pierce': 0.5, 'move_speed': 0.05,
                'p_atk': 0.0 # เมจไม่เอาดาเมจกายภาพ
            }
        else: # Physical / True / Hybrid
            return {
                'p_atk': 1.0, 'aspd': 20.0, 'crit': 50.0, 
                'hp': 0.1, 'p_pierce': 0.5, 'move_speed': 0.05,
                'ap': 0.0
            }

    def calculate_stats(self, chromosome: List[int]) -> Dict[str, float]:
        """รวม Stat ของ Hero + Items 6 ชิ้น"""
        # จัดการกับ None values จาก database โดยใช้ค่า default
        stats = {
            "p_atk": self.hero.get('base_atk') or 100,  # Default ถ้า None
            "p_def": self.hero.get('base_def') or 50,
            "max_hp": self.hero.get('base_hp') or 3000,
            "m_power": 0.0,
            "cdr": 0.0,
            "aspd": 0.0,
            "crit_rate": 0.0,
            "move_speed": 350.0, # Base Speed สมมติ
            "p_pierce_percent": 0.0,
            "m_pierce_percent": 0.0
        }

        for item_id in chromosome:
            item = self.all_items.get(item_id)
            if not item: continue
            
            # บวก Stat พื้นฐาน (ยังไม่รวม Unique Passive Stat เพราะซับซ้อน ไว้เวอร์ชั่นหน้า)
            stats["p_atk"] += item.get("p_atk", 0)
            stats["m_power"] += item.get("m_power", 0)
            stats["p_def"] += item.get("p_def", 0)
            stats["max_hp"] += item.get("max_hp", 0)
            stats["cdr"] += item.get("cdr", 0)
            stats["aspd"] += item.get("aspd", 0)
            stats["crit_rate"] += item.get("crit_rate", 0)
            stats["move_speed"] += item.get("move_speed", 0)
            
            # Handle Pierce % (เอาค่าสูงสุดอันเดียว - Logic อย่างง่าย)
            stats["p_pierce_percent"] = max(stats["p_pierce_percent"], item.get("p_pierce_percent", 0))
            stats["m_pierce_percent"] = max(stats["m_pierce_percent"], item.get("m_pierce_percent", 0))

        return stats

    def get_fitness(self, chromosome: List[int]) -> float:
        """
        คำนวณคะแนนความเก่ง (Fitness Score)
        Score = (Stats * Weights) - Penalties
        """
        score = 0.0
        item_objects = [self.all_items[i] for i in chromosome if i in self.all_items]
        
        # 1. 🛑 Check Penalties (กฎเหล็ก & Passive ซ้ำ)
        passive_penalty, _ = self.passive_manager.check_passive_conflicts(item_objects)
        score += passive_penalty
        
        # Check Restrictions (Boots, Jungle)
        boots_count = 0
        for item in item_objects:
            if 'limit_one_boots' in item.get('restrictions', []):
                boots_count += 1
            # (เพิ่ม Logic เช็คของป่าตรงนี้ได้ในอนาคต)
            
        if boots_count > 1:
            score += PENALTIES['boots_limit'] * (boots_count - 1)

        # 2. 🧮 Calculate Score from Stats
        stats = self.calculate_stats(chromosome)
        
        # Apply Caps (ตัดส่วนเกินทิ้ง)
        effective_cdr = min(stats['cdr'], STATS_CAPS['cdr'])
        effective_crit = min(stats['crit_rate'], STATS_CAPS['crit_rate'])
        effective_aspd = min(stats['aspd'], STATS_CAPS['aspd'])
        
        # Weighted Sum (ใช้ learned weights หรือ default weights)
        score += stats['p_atk'] * self.weights.get('p_atk', 0)
        score += stats['m_power'] * self.weights.get('ap', 0)
        score += stats['max_hp'] * self.weights.get('hp', 0)
        score += effective_cdr * self.weights.get('cdr', 0)
        score += effective_aspd * self.weights.get('aspd', 0)
        score += effective_crit * self.weights.get('crit', 0)
        score += stats['p_pierce_percent'] * 100 * self.weights.get('p_pierce', 0)
        score += stats['m_pierce_percent'] * 100 * self.weights.get('m_pierce', 0)
        
        return score
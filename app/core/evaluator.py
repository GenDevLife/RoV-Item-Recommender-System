# evaluator.py - ประเมินคุณภาพของชุดไอเทม
import json
import os
from typing import List, Dict
from app.config import STATS_CAPS, PENALTIES
from app.core.passive_manager import PassiveManager

class BuildEvaluator:
    """คลาสสำหรับประเมินว่าชุดไอเทมดีแค่ไหนสำหรับ hero นั้นๆ"""
    
    def __init__(self, hero_data: Dict, all_items: Dict[int, Dict]):
        self.hero = hero_data
        self.all_items = all_items
        self.passive_manager = PassiveManager()
        self.weights = self._load_weights(hero_data.get('damage_type', 'Physical'))

    def _load_weights(self, damage_type: str) -> Dict[str, float]:
        """โหลด weights จากไฟล์ที่ calibrate ไว้"""
        weights_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'core', 'learned_weights.json'
        )
        
        if os.path.exists(weights_path):
            try:
                with open(weights_path, 'r') as f:
                    learned = json.load(f)
                    print(f"✅ Loaded learned weights from calibration")
                    return {
                        'p_atk': learned.get('p_atk', 0),
                        'ap': learned.get('m_power', 0),
                        'hp': learned.get('max_hp', 0),
                        'p_def': learned.get('p_def', 0),
                        'cdr': learned.get('cdr', 0),
                        'aspd': learned.get('aspd', 0),
                        'crit': learned.get('crit_rate', 0),
                        'p_pierce': learned.get('p_pierce_percent', 0),
                        'm_pierce': learned.get('m_pierce_percent', 0),
                        'move_speed': learned.get('move_speed', 0)
                    }
            except Exception as e:
                print(f"[WARN] โหลด weights ไม่ได้: {e}")
        
        print(f"[INFO] ใช้ default weights สำหรับ {damage_type}")
        return self._get_role_weights(damage_type)

    def _get_role_weights(self, damage_type: str) -> Dict[str, float]:
        """weights เริ่มต้นตามประเภทดาเมจ"""
        if damage_type == 'Magic':
            return {
                'ap': 1.0, 'hp': 0.1, 'cdr': 50.0, 
                'm_pierce': 0.5, 'move_speed': 0.05, 'p_atk': 0.0
            }
        else:
            return {
                'p_atk': 1.0, 'aspd': 20.0, 'crit': 50.0, 
                'hp': 0.1, 'p_pierce': 0.5, 'move_speed': 0.05, 'ap': 0.0
            }

    def calculate_stats(self, chromosome: List[int]) -> Dict[str, float]:
        """รวม stat ของ hero กับ items ทั้งหมด"""
        stats = {
            "p_atk": self.hero.get('base_atk') or 100,
            "p_def": self.hero.get('base_def') or 50,
            "max_hp": self.hero.get('base_hp') or 3000,
            "m_power": 0.0,
            "cdr": 0.0,
            "aspd": 0.0,
            "crit_rate": 0.0,
            "move_speed": 350.0,
            "p_pierce_percent": 0.0,
            "m_pierce_percent": 0.0
        }

        for item_id in chromosome:
            item = self.all_items.get(item_id)
            if not item: 
                continue
            
            stats["p_atk"] += item.get("p_atk", 0)
            stats["m_power"] += item.get("m_power", 0)
            stats["p_def"] += item.get("p_def", 0)
            stats["max_hp"] += item.get("max_hp", 0)
            stats["cdr"] += item.get("cdr", 0)
            stats["aspd"] += item.get("aspd", 0)
            stats["crit_rate"] += item.get("crit_rate", 0)
            stats["move_speed"] += item.get("move_speed", 0)
            stats["p_pierce_percent"] = max(stats["p_pierce_percent"], item.get("p_pierce_percent", 0))
            stats["m_pierce_percent"] = max(stats["m_pierce_percent"], item.get("m_pierce_percent", 0))

        return stats

    def get_fitness(self, chromosome: List[int]) -> float:
        """คำนวณคะแนน fitness ของ build"""
        score = 0.0
        item_objects = [self.all_items[i] for i in chromosome if i in self.all_items]
        
        # ตรวจสอบ penalty จาก passive ซ้ำ
        passive_penalty, _ = self.passive_manager.check_passive_conflicts(item_objects)
        score += passive_penalty
        
        # เช็ครองเท้าซ้ำ
        boots_count = sum(1 for item in item_objects 
                        if 'limit_one_boots' in item.get('restrictions', []))
        if boots_count > 1:
            score += PENALTIES['boots_limit'] * (boots_count - 1)

        # คำนวณคะแนนจาก stats
        stats = self.calculate_stats(chromosome)
        
        # ตัด stats ที่เกิน cap
        effective_cdr = min(stats['cdr'], STATS_CAPS['cdr'])
        effective_crit = min(stats['crit_rate'], STATS_CAPS['crit_rate'])
        effective_aspd = min(stats['aspd'], STATS_CAPS['aspd'])
        
        # รวมคะแนนตาม weights
        score += stats['p_atk'] * self.weights.get('p_atk', 0)
        score += stats['m_power'] * self.weights.get('ap', 0)
        score += stats['max_hp'] * self.weights.get('hp', 0)
        score += effective_cdr * self.weights.get('cdr', 0)
        score += effective_aspd * self.weights.get('aspd', 0)
        score += effective_crit * self.weights.get('crit', 0)
        score += stats['p_pierce_percent'] * 100 * self.weights.get('p_pierce', 0)
        score += stats['m_pierce_percent'] * 100 * self.weights.get('m_pierce', 0)
        
        return score
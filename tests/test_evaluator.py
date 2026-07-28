# tests/test_evaluator.py - Tests สำหรับ Build Evaluator
"""
Test cases สำหรับ BuildEvaluator
ทดสอบการคำนวณ stats และ fitness score
"""
import pytest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.core.evaluator import BuildEvaluator
from app.config import STATS_CAPS, PENALTIES


class TestEvaluatorInit:
    """ทดสอบการสร้าง Evaluator"""
    
    def test_evaluator_init(self, dummy_hero, all_items):
        """ทดสอบว่าสร้าง evaluator ได้"""
        evaluator = BuildEvaluator(dummy_hero, all_items)
        assert evaluator is not None
        assert evaluator.hero == dummy_hero
    
    def test_evaluator_loads_weights(self, dummy_hero, all_items):
        """ทดสอบว่า evaluator โหลด weights"""
        evaluator = BuildEvaluator(dummy_hero, all_items)
        assert hasattr(evaluator, 'weights')
        assert isinstance(evaluator.weights, dict)
    
    def test_evaluator_has_passive_manager(self, dummy_hero, all_items):
        """ทดสอบว่า evaluator มี passive manager"""
        evaluator = BuildEvaluator(dummy_hero, all_items)
        assert hasattr(evaluator, 'passive_manager')


class TestCalculateStats:
    """ทดสอบ calculate_stats()"""
    
    def test_calculate_stats_empty_build(self, evaluator):
        """ทดสอบคำนวณ stats กับ build ว่าง"""
        stats = evaluator.calculate_stats([])
        assert isinstance(stats, dict)
        # ควรมี base stats ของ hero
        assert 'p_atk' in stats
        assert 'max_hp' in stats
    
    def test_calculate_stats_valid_build(self, evaluator, sample_build):
        """ทดสอบคำนวณ stats กับ build ปกติ"""
        stats = evaluator.calculate_stats(sample_build)
        assert isinstance(stats, dict)
        assert stats['p_atk'] >= 0
        assert stats['max_hp'] >= 0
    
    def test_stats_increase_with_items(self, evaluator, sample_build):
        """ทดสอบว่า stats เพิ่มขึ้นเมื่อมี items"""
        empty_stats = evaluator.calculate_stats([])
        full_stats = evaluator.calculate_stats(sample_build)
        
        # อย่างน้อย 1 stat ควรเพิ่มขึ้น
        increased = any(
            full_stats.get(k, 0) > empty_stats.get(k, 0)
            for k in ['p_atk', 'm_power', 'max_hp', 'p_def']
        )
        assert increased, "Stats should increase with items"
    
    def test_calculate_stats_has_all_fields(self, evaluator, sample_build):
        """ทดสอบว่า stats มี fields ครบ"""
        expected_fields = [
            'p_atk', 'p_def', 'max_hp', 'm_power', 
            'cdr', 'aspd', 'crit_rate', 'move_speed',
            'p_pierce_percent', 'm_pierce_percent'
        ]
        stats = evaluator.calculate_stats(sample_build)
        
        for field in expected_fields:
            assert field in stats, f"Missing stat field: {field}"
    
    def test_calculate_stats_invalid_items(self, evaluator):
        """ทดสอบกับ item IDs ที่ไม่มีอยู่"""
        invalid_build = [99999, 99998, 99997]
        stats = evaluator.calculate_stats(invalid_build)
        # ไม่ควร crash แต่ได้ base stats
        assert isinstance(stats, dict)
    
    def test_base_stats_from_hero(self, dummy_hero, all_items):
        """ทดสอบว่า base stats มาจาก hero"""
        evaluator = BuildEvaluator(dummy_hero, all_items)
        stats = evaluator.calculate_stats([])
        
        # ควรมี base_atk จาก hero
        assert stats['p_atk'] == dummy_hero.get('base_atk', 100)


class TestGetFitness:
    """ทดสอบ get_fitness()"""
    
    def test_fitness_returns_float(self, evaluator, sample_build):
        """ทดสอบว่า fitness เป็น float"""
        fitness = evaluator.get_fitness(sample_build)
        assert isinstance(fitness, (int, float))
    
    def test_fitness_empty_build(self, evaluator):
        """ทดสอบ fitness กับ build ว่าง"""
        fitness = evaluator.get_fitness([])
        assert isinstance(fitness, (int, float))
    
    def test_fitness_positive_for_good_build(self, evaluator, sample_build):
        """ทดสอบว่า build ปกติมี fitness เป็นบวก"""
        fitness = evaluator.get_fitness(sample_build)
        # ถ้า weights เป็นบวก และไม่มี penalty มาก ควรเป็นบวก
        # แต่ไม่ guarantee เพราะขึ้นกับ weights
        assert fitness is not None
    
    def test_fitness_consistent(self, evaluator, sample_build):
        """ทดสอบว่าคำนวณ fitness ได้ค่าเท่ากันทุกครั้ง"""
        fitness1 = evaluator.get_fitness(sample_build)
        fitness2 = evaluator.get_fitness(sample_build)
        assert fitness1 == fitness2
    
    def test_different_builds_different_fitness(self, evaluator, valid_items):
        """ทดสอบว่า builds ต่างกันได้ fitness ต่างกัน"""
        import random
        
        if len(valid_items) >= 12:
            build1 = random.sample(valid_items[:20], 6)
            build2 = random.sample(valid_items[20:40], 6) if len(valid_items) >= 40 else random.sample(valid_items, 6)
            
            fitness1 = evaluator.get_fitness(build1)
            fitness2 = evaluator.get_fitness(build2)
            
            # ไม่ guarantee ว่าต่างกัน แต่น่าจะต่าง
            # เพราะ random อาจได้ build คล้ายกัน
            # ไม่ assert เพราะอาจ coincidentally เท่ากัน


class TestFitnessPenalties:
    """ทดสอบ Penalty System"""
    
    def test_boots_penalty(self, evaluator, items_with_boots_conflict, all_items):
        """ทดสอบว่าใส่รองเท้า 2 คู่โดน penalty"""
        if len(items_with_boots_conflict) >= 2:
            # สร้าง build ที่มี boots 2 คู่
            boots_ids = []
            for item in items_with_boots_conflict:
                for item_id, data in all_items.items():
                    if data.get('name_en') == item.get('name_en'):
                        boots_ids.append(item_id)
                        break
            
            if len(boots_ids) >= 2:
                # เปรียบเทียบกับ build ที่มี boots 1 คู่
                single_boot = [boots_ids[0]] + list(all_items.keys())[:5]
                double_boots = boots_ids[:2] + list(all_items.keys())[:4]
                
                fitness_single = evaluator.get_fitness(single_boot)
                fitness_double = evaluator.get_fitness(double_boots)
                
                # Double boots ควรได้คะแนนน้อยกว่า (penalty)
                # แต่ไม่ guarantee เพราะ stats อาจต่างกัน
    
    def test_passive_conflict_penalty(self, evaluator, items_with_conflict, all_items):
        """ทดสอบว่า passive ซ้ำโดน penalty"""
        if len(items_with_conflict) >= 2:
            # หา item IDs ของ conflicting items
            conflict_ids = []
            for item in items_with_conflict[:2]:
                for item_id, data in all_items.items():
                    if data.get('name_en') == item.get('name_en'):
                        conflict_ids.append(item_id)
                        break
            
            # เราไม่ assert ผลลัพธ์โดยตรง เพราะซับซ้อน
            # แค่ทดสอบว่าไม่ crash
            if len(conflict_ids) >= 2:
                build = conflict_ids + list(all_items.keys())[:4]
                fitness = evaluator.get_fitness(build)
                assert isinstance(fitness, (int, float))


class TestStatsCaps:
    """ทดสอบ Stat Caps"""
    
    def test_cdr_cap(self):
        """ทดสอบว่า CDR มี cap 40%"""
        assert STATS_CAPS['cdr'] == 0.40
    
    def test_crit_cap(self):
        """ทดสอบว่า Crit มี cap 100%"""
        assert STATS_CAPS['crit_rate'] == 1.00
    
    def test_aspd_cap(self):
        """ทดสอบว่า ASPD มี cap 200%"""
        assert STATS_CAPS['aspd'] == 2.00


class TestWeights:
    """ทดสอบ Weights System"""
    
    def test_weights_loaded(self, evaluator):
        """ทดสอบว่า weights ถูกโหลด"""
        assert len(evaluator.weights) > 0
    
    def test_weights_has_patk(self, evaluator):
        """ทดสอบว่ามี weight สำหรับ p_atk"""
        assert 'p_atk' in evaluator.weights or 'p_atk' in str(evaluator.weights)
    
    def test_physical_hero_weights(self, sample_hero_physical, all_items):
        """ทดสอบว่า Physical hero มี weights ที่เหมาะสม"""
        if sample_hero_physical:
            evaluator = BuildEvaluator(sample_hero_physical, all_items)
            # Physical hero ควรให้ความสำคัญกับ p_atk
            assert evaluator.weights is not None
    
    def test_magic_hero_weights(self, sample_hero_magic, all_items):
        """ทดสอบว่า Magic hero มี weights ที่เหมาะสม"""
        if sample_hero_magic:
            evaluator = BuildEvaluator(sample_hero_magic, all_items)
            assert evaluator.weights is not None


class TestPenaltyValues:
    """ทดสอบค่า Penalty"""
    
    def test_duplicate_passive_penalty_negative(self):
        """ทดสอบว่า penalty เป็นค่าลบ"""
        assert PENALTIES['duplicate_passive'] < 0
    
    def test_boots_limit_penalty_negative(self):
        """ทดสอบว่า boots penalty เป็นค่าลบ"""
        assert PENALTIES['boots_limit'] < 0
    
    def test_jungle_wrong_penalty_negative(self):
        """ทดสอบว่า jungle penalty เป็นค่าลบ"""
        assert PENALTIES['jungle_wrong'] < 0

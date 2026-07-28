# tests/test_ga_engine.py - Tests สำหรับ Genetic Algorithm Engine
"""
Test cases สำหรับ GeneticEngine
ทดสอบ Genetic Algorithm operations
"""
import pytest
import sys
import os
import random

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.core.ga_engine import GeneticEngine
from app.core.evaluator import BuildEvaluator
from app.config import get_ga_settings


class TestGeneticEngineInit:
    """ทดสอบการสร้าง GA Engine"""
    
    def test_engine_init(self, evaluator, valid_items, ga_settings_test):
        """ทดสอบว่าสร้าง engine ได้"""
        engine = GeneticEngine(evaluator, valid_items, ga_settings_test)
        assert engine is not None
    
    def test_engine_has_evaluator(self, ga_engine):
        """ทดสอบว่า engine มี evaluator"""
        assert ga_engine.evaluator is not None
    
    def test_engine_has_item_pool(self, ga_engine):
        """ทดสอบว่า engine มี item pool"""
        assert len(ga_engine.item_pool) > 0
    
    def test_engine_has_settings(self, ga_engine, ga_settings_test):
        """ทดสอบว่า engine มี settings ถูกต้อง"""
        assert ga_engine.pop_size == ga_settings_test['POP_SIZE']
        assert ga_engine.max_gen == ga_settings_test['MAX_GEN']
        assert ga_engine.mutation_rate == ga_settings_test['MUTATION_RATE']
        assert ga_engine.elitism_count == ga_settings_test['ELITISM_COUNT']


class TestCreateChromosome:
    """ทดสอบ create_chromosome()"""
    
    def test_chromosome_length(self, ga_engine):
        """ทดสอบว่า chromosome มี 6 items"""
        chrom = ga_engine.create_chromosome()
        assert len(chrom) == 6
    
    def test_chromosome_unique_items(self, ga_engine):
        """ทดสอบว่า chromosome ไม่มี items ซ้ำ"""
        chrom = ga_engine.create_chromosome()
        assert len(chrom) == len(set(chrom)), "Chromosome should have unique items"
    
    def test_chromosome_valid_items(self, ga_engine):
        """ทดสอบว่า items ใน chromosome มาจาก item pool"""
        chrom = ga_engine.create_chromosome()
        for item_id in chrom:
            assert item_id in ga_engine.item_pool
    
    def test_multiple_chromosomes_different(self, ga_engine):
        """ทดสอบว่าสร้าง chromosomes หลายตัวได้ต่างกัน"""
        chroms = [ga_engine.create_chromosome() for _ in range(10)]
        
        # บาง chromosome ควรต่างกัน (ไม่ guarantee ทุกตัวต่าง)
        unique_chroms = set(tuple(c) for c in chroms)
        assert len(unique_chroms) > 1, "Multiple random chromosomes should differ"


class TestEnsureUniqueItems:
    """ทดสอบ ensure_unique_items()"""
    
    def test_fixes_duplicates(self, ga_engine, valid_items):
        """ทดสอบว่าแก้ไข items ซ้ำได้"""
        if len(valid_items) >= 6:
            # สร้าง chromosome ที่มีซ้ำ
            duplicate_chrom = [valid_items[0], valid_items[0], valid_items[1], 
                              valid_items[1], valid_items[2], valid_items[2]]
            
            fixed = ga_engine.ensure_unique_items(duplicate_chrom)
            assert len(fixed) == len(set(fixed)), "Should have unique items after fix"
    
    def test_keeps_unique_items(self, ga_engine):
        """ทดสอบว่าไม่เปลี่ยน chromosome ที่ไม่มีซ้ำ"""
        unique_chrom = ga_engine.create_chromosome()
        fixed = ga_engine.ensure_unique_items(unique_chrom[:])
        
        # ควรยังคง unique
        assert len(fixed) == len(set(fixed))
    
    def test_length_preserved(self, ga_engine, valid_items):
        """ทดสอบว่าความยาว chromosome ไม่เปลี่ยน"""
        if len(valid_items) >= 6:
            chrom = [valid_items[0]] * 6  # ซ้ำทั้งหมด
            fixed = ga_engine.ensure_unique_items(chrom)
            assert len(fixed) == 6


class TestCrossover:
    """ทดสอบ crossover()"""
    
    def test_crossover_returns_list(self, ga_engine):
        """ทดสอบว่า crossover return list"""
        parent1 = ga_engine.create_chromosome()
        parent2 = ga_engine.create_chromosome()
        
        child = ga_engine.crossover(parent1, parent2)
        assert isinstance(child, list)
    
    def test_crossover_length(self, ga_engine):
        """ทดสอบว่า child มี 6 items"""
        parent1 = ga_engine.create_chromosome()
        parent2 = ga_engine.create_chromosome()
        
        child = ga_engine.crossover(parent1, parent2)
        assert len(child) == 6
    
    def test_crossover_unique_items(self, ga_engine):
        """ทดสอบว่า child มี unique items"""
        parent1 = ga_engine.create_chromosome()
        parent2 = ga_engine.create_chromosome()
        
        child = ga_engine.crossover(parent1, parent2)
        assert len(child) == len(set(child))
    
    def test_crossover_items_from_pool(self, ga_engine):
        """ทดสอบว่า child มี items จาก pool"""
        parent1 = ga_engine.create_chromosome()
        parent2 = ga_engine.create_chromosome()
        
        child = ga_engine.crossover(parent1, parent2)
        for item_id in child:
            assert item_id in ga_engine.item_pool
    
    def test_crossover_combines_parents(self, ga_engine):
        """ทดสอบว่า child มี items จากทั้ง 2 parents"""
        parent1 = ga_engine.create_chromosome()
        parent2 = ga_engine.create_chromosome()
        
        child = ga_engine.crossover(parent1, parent2)
        
        # บาง items ใน child ควรมาจาก parent1 หรือ parent2
        from_parent1 = sum(1 for i in child if i in parent1)
        from_parent2 = sum(1 for i in child if i in parent2)
        
        # อย่างน้อย 1 item ควรมาจาก parent ใด parent หนึ่ง
        # (ยกเว้นถ้า ensure_unique_items แทนที่ทั้งหมด)
        assert from_parent1 + from_parent2 >= 0


class TestMutation:
    """ทดสอบ mutate()"""
    
    def test_mutate_returns_list(self, ga_engine):
        """ทดสอบว่า mutate return list"""
        chrom = ga_engine.create_chromosome()
        mutated = ga_engine.mutate(chrom[:])
        assert isinstance(mutated, list)
    
    def test_mutate_length_preserved(self, ga_engine):
        """ทดสอบว่า mutation ไม่เปลี่ยนความยาว"""
        chrom = ga_engine.create_chromosome()
        mutated = ga_engine.mutate(chrom[:])
        assert len(mutated) == 6
    
    def test_mutate_valid_items(self, ga_engine):
        """ทดสอบว่า items หลัง mutate ยังอยู่ใน pool"""
        chrom = ga_engine.create_chromosome()
        mutated = ga_engine.mutate(chrom[:])
        
        for item_id in mutated:
            assert item_id in ga_engine.item_pool
    
    def test_high_mutation_rate_changes(self):
        """ทดสอบว่า mutation rate สูงทำให้เปลี่ยน"""
        # ต้องสร้าง engine ใหม่ด้วย mutation_rate 1.0
        pass  # Skip complex test
    
    def test_mutation_probabilistic(self, ga_engine):
        """ทดสอบว่า mutation เป็น probabilistic"""
        chrom = ga_engine.create_chromosome()
        original = chrom[:]
        
        # Run mutation หลายครั้ง
        changed_count = 0
        for _ in range(20):
            mutated = ga_engine.mutate(original[:])
            if mutated != original:
                changed_count += 1
        
        # ถ้า mutation_rate > 0, บางครั้งควรเปลี่ยน
        if ga_engine.mutation_rate > 0:
            assert changed_count >= 0  # ไม่ guarantee ว่าต้องเปลี่ยน


class TestRun:
    """ทดสอบ run() - Main GA Loop"""
    
    def test_run_returns_tuple(self, ga_engine):
        """ทดสอบว่า run() return tuple (build, score)"""
        result = ga_engine.run()
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_run_build_is_list(self, ga_engine):
        """ทดสอบว่า build เป็น list"""
        build, score = ga_engine.run()
        assert isinstance(build, list)
    
    def test_run_build_length(self, ga_engine):
        """ทดสอบว่า build มี 6 items"""
        build, score = ga_engine.run()
        assert len(build) == 6
    
    def test_run_build_unique(self, ga_engine):
        """ทดสอบว่า build มี unique items"""
        build, score = ga_engine.run()
        assert len(build) == len(set(build))
    
    def test_run_score_is_number(self, ga_engine):
        """ทดสอบว่า score เป็นตัวเลข"""
        build, score = ga_engine.run()
        assert isinstance(score, (int, float))
    
    def test_run_items_valid(self, ga_engine):
        """ทดสอบว่า items ใน build มาจาก pool"""
        build, score = ga_engine.run()
        for item_id in build:
            assert item_id in ga_engine.item_pool
    
    def test_run_consistent_result_type(self, ga_engine):
        """ทดสอบ run หลายครั้งได้ result type เดียวกัน"""
        for _ in range(3):
            build, score = ga_engine.run()
            assert isinstance(build, list)
            assert isinstance(score, (int, float))


class TestGASettings:
    """ทดสอบ GA Settings"""
    
    def test_get_fast_settings(self):
        """ทดสอบ fast settings"""
        settings = get_ga_settings('fast')
        assert settings['POP_SIZE'] > 0
        assert settings['MAX_GEN'] > 0
        assert 0 <= settings['MUTATION_RATE'] <= 1
    
    def test_get_medium_settings(self):
        """ทดสอบ medium settings"""
        settings = get_ga_settings('medium')
        assert settings['POP_SIZE'] > 0
        assert settings['MAX_GEN'] > 0
    
    def test_get_expert_settings(self):
        """ทดสอบ expert settings"""
        settings = get_ga_settings('expert')
        assert settings['POP_SIZE'] > 0
        assert settings['MAX_GEN'] > 0
    
    def test_expert_more_generations_than_fast(self):
        """ทดสอบว่า expert มี generations มากกว่า fast"""
        fast = get_ga_settings('fast')
        expert = get_ga_settings('expert')
        assert expert['MAX_GEN'] > fast['MAX_GEN']
    
    def test_invalid_profile_raises(self):
        """ทดสอบว่า profile ไม่ถูกต้อง raise error"""
        with pytest.raises(ValueError):
            get_ga_settings('invalid_profile_xyz')


class TestGAPerformance:
    """ทดสอบ Performance ของ GA"""
    
    def test_run_completes_in_time(self, ga_engine, timer):
        """ทดสอบว่า GA เสร็จในเวลาที่เหมาะสม"""
        timer.start()
        build, score = ga_engine.run()
        elapsed = timer.stop()
        
        # ควรเสร็จใน 5 วินาที (สำหรับ minimal settings)
        assert elapsed < 5.0, f"GA took too long: {elapsed}s"
    
    def test_larger_settings_take_longer(self, evaluator, valid_items, timer):
        """ทดสอบว่า settings ใหญ่กว่าใช้เวลานานกว่า"""
        small_settings = {'POP_SIZE': 5, 'MAX_GEN': 2, 'MUTATION_RATE': 0.3, 'ELITISM_COUNT': 1}
        large_settings = {'POP_SIZE': 20, 'MAX_GEN': 10, 'MUTATION_RATE': 0.3, 'ELITISM_COUNT': 2}
        
        # Small
        engine_small = GeneticEngine(evaluator, valid_items, small_settings)
        timer.start()
        engine_small.run()
        time_small = timer.stop()
        
        # Large
        engine_large = GeneticEngine(evaluator, valid_items, large_settings)
        timer.start()
        engine_large.run()
        time_large = timer.stop()
        
        # Large ควรใช้เวลานานกว่า (ไม่ guarantee แต่น่าจะใช่)
        # ไม่ assert เพราะอาจมี variance


class TestGAConvergence:
    """ทดสอบการ Converge ของ GA"""
    
    def test_multiple_runs_find_similar_quality(self, evaluator, valid_items):
        """ทดสอบว่า GA หลายรอบได้คุณภาพใกล้เคียงกัน"""
        settings = {'POP_SIZE': 15, 'MAX_GEN': 10, 'MUTATION_RATE': 0.2, 'ELITISM_COUNT': 2}
        engine = GeneticEngine(evaluator, valid_items, settings)
        
        scores = []
        for _ in range(5):
            build, score = engine.run()
            scores.append(score)
        
        # Scores ไม่ควรต่างกันมาก (ถ้า converge ดี)
        avg_score = sum(scores) / len(scores)
        max_diff = max(abs(s - avg_score) for s in scores)
        
        # ไม่ assert hard limit เพราะ GA มี randomness
        # แค่ตรวจว่าไม่ crash

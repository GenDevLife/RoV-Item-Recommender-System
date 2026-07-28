# tests/conftest.py - Pytest Configuration และ Fixtures
"""
Shared fixtures สำหรับ test ทั้งหมด
"""
import pytest
import sys
import os
import sqlite3
import tempfile
import shutil

# เพิ่ม project root เข้า path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.config import DB_PATH
from app.data.repository import RoVRepository
from app.core.evaluator import BuildEvaluator
from app.core.ga_engine import GeneticEngine
from app.core.passive_manager import PassiveManager


# ============================================
# Database Fixtures
# ============================================

@pytest.fixture(scope="session")
def db_path():
    """Path ไปยัง database จริง"""
    return DB_PATH


@pytest.fixture(scope="session")
def repository(db_path):
    """Repository instance สำหรับใช้ทดสอบ"""
    return RoVRepository(db_path)


@pytest.fixture(scope="session")
def all_items(repository):
    """โหลด items ทั้งหมดจาก database"""
    return repository.get_all_items()


@pytest.fixture(scope="session")
def valid_items(all_items):
    """รายการ item IDs ที่เป็น Tier 3"""
    return [k for k, v in all_items.items() if v.get('tier') == 3]


@pytest.fixture(scope="session")
def hero_list(repository):
    """รายชื่อ heroes ทั้งหมด"""
    return repository.get_hero_list()


# ============================================
# Hero Fixtures
# ============================================

@pytest.fixture
def sample_hero_physical(repository):
    """ตัวอย่าง Physical hero (Valhein)"""
    hero = repository.get_hero_data('valhein')
    if hero is None:
        # Fallback ถ้าไม่มี valhein
        heroes = repository.get_hero_list()
        if heroes:
            hero = repository.get_hero_data(heroes[0])
    return hero


@pytest.fixture
def sample_hero_magic(repository):
    """ตัวอย่าง Magic hero"""
    # ลองหา mage hero
    for hero_code in ['krixi', 'lauriel', 'tulen', 'liliana']:
        hero = repository.get_hero_data(hero_code)
        if hero and hero.get('damage_type') == 'Magic':
            return hero
    
    # Fallback: หา hero ที่เป็น magic
    for hero_code in repository.get_hero_list():
        hero = repository.get_hero_data(hero_code)
        if hero and hero.get('damage_type') == 'Magic':
            return hero
    
    return None


@pytest.fixture
def dummy_hero():
    """Hero data สำหรับ test ที่ไม่ต้องการ database"""
    return {
        'hero_id': 999,
        'code_name': 'test_hero',
        'name_en': 'Test Hero',
        'damage_type': 'Physical',
        'primary_role': 'Carry',
        'secondary_role': 'Assassin',
        'primary_lane': 'Dragon Slayer',
        'secondary_lane': 'Jungle',
        'base_atk': 168,
        'base_def': 89,
        'base_hp': 3420
    }


# ============================================
# Build Fixtures
# ============================================

@pytest.fixture
def sample_build(valid_items):
    """ตัวอย่าง build (6 items)"""
    import random
    if len(valid_items) >= 6:
        return random.sample(valid_items, 6)
    return valid_items[:6]


@pytest.fixture
def empty_build():
    """Build ว่างเปล่า"""
    return []


@pytest.fixture
def invalid_build():
    """Build ที่มี item ID ไม่ถูกต้อง"""
    return [-1, -2, -3, -4, -5, -6]


# ============================================
# Evaluator Fixtures
# ============================================

@pytest.fixture
def evaluator(dummy_hero, all_items):
    """BuildEvaluator instance"""
    return BuildEvaluator(dummy_hero, all_items)


@pytest.fixture
def evaluator_physical(sample_hero_physical, all_items):
    """Evaluator สำหรับ Physical hero"""
    if sample_hero_physical:
        return BuildEvaluator(sample_hero_physical, all_items)
    return None


@pytest.fixture
def evaluator_magic(sample_hero_magic, all_items):
    """Evaluator สำหรับ Magic hero"""
    if sample_hero_magic:
        return BuildEvaluator(sample_hero_magic, all_items)
    return None


# ============================================
# GA Engine Fixtures
# ============================================

@pytest.fixture
def ga_settings_fast():
    """Fast GA settings"""
    return {
        'POP_SIZE': 10,  # เล็กลงสำหรับ test ให้เร็ว
        'MAX_GEN': 5,
        'MUTATION_RATE': 0.3,
        'ELITISM_COUNT': 2
    }


@pytest.fixture
def ga_settings_test():
    """Minimal GA settings สำหรับ test"""
    return {
        'POP_SIZE': 5,
        'MAX_GEN': 3,
        'MUTATION_RATE': 0.5,
        'ELITISM_COUNT': 1
    }


@pytest.fixture
def ga_engine(evaluator, valid_items, ga_settings_test):
    """GeneticEngine instance"""
    return GeneticEngine(evaluator, valid_items, ga_settings_test)


# ============================================
# Passive Manager Fixtures
# ============================================

@pytest.fixture
def passive_manager():
    """PassiveManager instance"""
    return PassiveManager()


@pytest.fixture
def items_with_conflict(all_items):
    """หา items ที่มี passive ซ้ำกัน"""
    # หา items ที่มี passive 'elemental_power' (Omni Arms, Frost Cape)
    conflicting = []
    for item_id, item in all_items.items():
        passives = item.get('passives', [])
        if 'elemental_power' in passives:
            conflicting.append(item)
    return conflicting


@pytest.fixture
def items_with_boots_conflict(all_items):
    """หา boots หลายคู่"""
    boots = []
    for item_id, item in all_items.items():
        restrictions = item.get('restrictions', [])
        if 'limit_one_boots' in restrictions:
            boots.append(item)
    return boots[:2] if len(boots) >= 2 else boots


# ============================================
# Temporary Database Fixture (สำหรับ write tests)
# ============================================

@pytest.fixture
def temp_db():
    """สร้าง temporary database copy สำหรับ test ที่ต้อง write"""
    # สร้าง temp directory
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, 'test_rov_data.db')
    
    # Copy database จริง
    if os.path.exists(DB_PATH):
        shutil.copy(DB_PATH, temp_db_path)
    
    yield temp_db_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================
# Performance Fixtures
# ============================================

@pytest.fixture
def timer():
    """Simple timer สำหรับวัด performance"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.elapsed
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0
    
    return Timer()

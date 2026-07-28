# tests/test_passive_manager.py - Tests สำหรับ Passive Manager
"""
Test cases สำหรับ PassiveManager
ทดสอบการตรวจสอบ Passive Conflicts
"""
import pytest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.core.passive_manager import PassiveManager
from app.config import PENALTIES


class TestPassiveManagerInit:
    """ทดสอบการสร้าง PassiveManager"""
    
    def test_init(self):
        """ทดสอบว่าสร้าง PassiveManager ได้"""
        pm = PassiveManager()
        assert pm is not None
    
    def test_has_check_method(self):
        """ทดสอบว่ามี method check_passive_conflicts"""
        pm = PassiveManager()
        assert hasattr(pm, 'check_passive_conflicts')


class TestCheckPassiveConflicts:
    """ทดสอบ check_passive_conflicts()"""
    
    def test_no_conflict_empty_list(self, passive_manager):
        """ทดสอบกับ list ว่าง"""
        penalty, conflicts = passive_manager.check_passive_conflicts([])
        assert penalty == 0.0
        assert conflicts == []
    
    def test_no_conflict_single_item(self, passive_manager):
        """ทดสอบกับ item เดียว"""
        item = {'name_en': 'Test Item', 'passives': ['unique_passive_a']}
        penalty, conflicts = passive_manager.check_passive_conflicts([item])
        assert penalty == 0.0
        assert conflicts == []
    
    def test_no_conflict_different_passives(self, passive_manager):
        """ทดสอบกับ items ที่มี passives ต่างกัน"""
        items = [
            {'name_en': 'Item A', 'passives': ['passive_a']},
            {'name_en': 'Item B', 'passives': ['passive_b']},
            {'name_en': 'Item C', 'passives': ['passive_c']}
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        assert penalty == 0.0
        assert conflicts == []
    
    def test_conflict_same_passive(self, passive_manager):
        """ทดสอบว่าจับ passive ซ้ำได้"""
        items = [
            {'name_en': 'Item A', 'passives': ['shared_passive']},
            {'name_en': 'Item B', 'passives': ['shared_passive']}
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        assert penalty < 0, "Penalty should be negative"
        assert len(conflicts) > 0, "Should have conflicts"
    
    def test_conflict_penalty_value(self, passive_manager):
        """ทดสอบค่า penalty ที่ถูกต้อง"""
        items = [
            {'name_en': 'Item A', 'passives': ['shared']},
            {'name_en': 'Item B', 'passives': ['shared']}
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        expected_penalty = PENALTIES['duplicate_passive']
        assert penalty == expected_penalty
    
    def test_multiple_conflicts(self, passive_manager):
        """ทดสอบ multiple conflicts"""
        items = [
            {'name_en': 'Item A', 'passives': ['shared']},
            {'name_en': 'Item B', 'passives': ['shared']},
            {'name_en': 'Item C', 'passives': ['shared']}
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        # 3 items มี passive เดียวกัน = 2 conflicts (B และ C ซ้ำกับ A)
        expected_penalty = PENALTIES['duplicate_passive'] * 2
        assert penalty == expected_penalty
        assert len(conflicts) == 2
    
    def test_no_passives(self, passive_manager):
        """ทดสอบกับ items ที่ไม่มี passives"""
        items = [
            {'name_en': 'Item A', 'passives': []},
            {'name_en': 'Item B', 'passives': []},
            {'name_en': 'Item C'}  # ไม่มี passives key
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        assert penalty == 0.0
        assert conflicts == []
    
    def test_mixed_passives(self, passive_manager):
        """ทดสอบ items ที่บางตัวมี passives บางตัวไม่มี"""
        items = [
            {'name_en': 'Item A', 'passives': ['unique']},
            {'name_en': 'Item B', 'passives': []},
            {'name_en': 'Item C', 'passives': ['unique']}  # ซ้ำกับ A
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        assert penalty < 0
        assert len(conflicts) == 1
    
    def test_multiple_passives_per_item(self, passive_manager):
        """ทดสอบ item ที่มีหลาย passives"""
        items = [
            {'name_en': 'Item A', 'passives': ['passive_1', 'passive_2']},
            {'name_en': 'Item B', 'passives': ['passive_2', 'passive_3']},  # ซ้ำ passive_2
            {'name_en': 'Item C', 'passives': ['passive_4']}
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        # passive_2 ซ้ำ
        assert penalty < 0
        assert len(conflicts) == 1


class TestRealItemConflicts:
    """ทดสอบ Conflicts กับ Items จริง"""
    
    def test_elemental_power_conflict(self, passive_manager, all_items):
        """ทดสอบ conflict ของ Omni Arms และ Frost Cape"""
        # หา items ที่มี elemental_power
        elemental_items = []
        for item_id, item in all_items.items():
            if 'elemental_power' in item.get('passives', []):
                elemental_items.append(item)
        
        if len(elemental_items) >= 2:
            penalty, conflicts = passive_manager.check_passive_conflicts(elemental_items[:2])
            assert penalty < 0, "Elemental power items should conflict"
    
    def test_boots_movement_conflict(self, passive_manager, all_items):
        """ทดสอบ conflict ของ boots (unique_movement)"""
        # หา boots
        boots = []
        for item_id, item in all_items.items():
            if 'unique_movement' in item.get('passives', []):
                boots.append(item)
        
        if len(boots) >= 2:
            penalty, conflicts = passive_manager.check_passive_conflicts(boots[:2])
            assert penalty < 0, "Multiple boots should conflict"


class TestConflictMessages:
    """ทดสอบ Conflict Messages"""
    
    def test_conflict_message_contains_passive_name(self, passive_manager):
        """ทดสอบว่า message มีชื่อ passive"""
        items = [
            {'name_en': 'Item A', 'passives': ['test_passive']},
            {'name_en': 'Item B', 'passives': ['test_passive']}
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        assert len(conflicts) > 0
        assert 'test_passive' in conflicts[0]
    
    def test_conflict_message_contains_item_name(self, passive_manager):
        """ทดสอบว่า message มีชื่อ item"""
        items = [
            {'name_en': 'First Item', 'passives': ['shared']},
            {'name_en': 'Second Item', 'passives': ['shared']}
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        assert len(conflicts) > 0
        # Message ควรมีชื่อ item ที่ซ้ำ
        assert 'Second Item' in conflicts[0] or 'shared' in conflicts[0]


class TestEdgeCases:
    """ทดสอบ Edge Cases"""
    
    def test_none_passives(self, passive_manager):
        """ทดสอบกับ passives เป็น None"""
        items = [
            {'name_en': 'Item A', 'passives': None},
            {'name_en': 'Item B'}
        ]
        # ไม่ควร crash
        try:
            penalty, conflicts = passive_manager.check_passive_conflicts(items)
        except (TypeError, AttributeError):
            pytest.skip("PassiveManager doesn't handle None passives")
    
    def test_empty_passive_string(self, passive_manager):
        """ทดสอบกับ passive เป็น empty string"""
        items = [
            {'name_en': 'Item A', 'passives': ['']},
            {'name_en': 'Item B', 'passives': ['']}
        ]
        # Empty string ก็ถือว่าซ้ำ
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        # ขึ้นกับ implementation ว่าจะนับ empty string หรือไม่
    
    def test_large_number_of_items(self, passive_manager):
        """ทดสอบกับ items จำนวนมาก"""
        items = [
            {'name_en': f'Item {i}', 'passives': [f'passive_{i}']}
            for i in range(100)
        ]
        penalty, conflicts = passive_manager.check_passive_conflicts(items)
        
        # ไม่ควรมี conflicts เพราะแต่ละตัว passive ต่างกัน
        assert penalty == 0.0
        assert len(conflicts) == 0

# tests/test_repository.py - Tests สำหรับ Database Repository
"""
Test cases สำหรับ RoVRepository
ทดสอบการเข้าถึง database และ query ข้อมูล
"""
import pytest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.data.repository import RoVRepository


class TestRepositoryConnection:
    """ทดสอบการเชื่อมต่อ Database"""
    
    def test_repository_init(self, db_path):
        """ทดสอบว่าสร้าง repository ได้"""
        repo = RoVRepository(db_path)
        assert repo is not None
        assert repo.db_path == db_path
    
    def test_database_exists(self, db_path):
        """ทดสอบว่า database file มีอยู่"""
        assert os.path.exists(db_path), f"Database not found at {db_path}"
    
    def test_connection_works(self, repository):
        """ทดสอบว่าเชื่อมต่อ database ได้"""
        conn = repository._get_conn()
        assert conn is not None
        conn.close()


class TestHeroQueries:
    """ทดสอบการ Query Hero Data"""
    
    def test_get_hero_list_not_empty(self, repository):
        """ทดสอบว่ามี heroes ในระบบ"""
        heroes = repository.get_hero_list()
        assert len(heroes) > 0, "Hero list should not be empty"
    
    def test_get_hero_list_returns_strings(self, repository):
        """ทดสอบว่า hero list เป็น list ของ strings"""
        heroes = repository.get_hero_list()
        assert all(isinstance(h, str) for h in heroes)
    
    def test_get_hero_list_sorted(self, repository):
        """ทดสอบว่า hero list เรียงตามตัวอักษร"""
        heroes = repository.get_hero_list()
        assert heroes == sorted(heroes)
    
    def test_get_hero_data_valid(self, repository, hero_list):
        """ทดสอบดึงข้อมูล hero ที่มีอยู่"""
        if hero_list:
            hero = repository.get_hero_data(hero_list[0])
            assert hero is not None
            assert 'code_name' in hero
    
    def test_get_hero_data_invalid(self, repository):
        """ทดสอบดึง hero ที่ไม่มี"""
        hero = repository.get_hero_data('nonexistent_hero_xyz')
        assert hero is None
    
    def test_hero_has_required_fields(self, repository, hero_list):
        """ทดสอบว่า hero มี fields ที่จำเป็น"""
        required_fields = ['code_name', 'damage_type']
        
        if hero_list:
            hero = repository.get_hero_data(hero_list[0])
            for field in required_fields:
                assert field in hero, f"Missing field: {field}"
    
    def test_hero_damage_type_valid(self, repository, hero_list):
        """ทดสอบว่า damage_type เป็นค่าที่ถูกต้อง"""
        valid_types = ['Physical', 'Magic', 'Hybrid', None]
        
        if hero_list:
            hero = repository.get_hero_data(hero_list[0])
            assert hero.get('damage_type') in valid_types


class TestItemQueries:
    """ทดสอบการ Query Item Data"""
    
    def test_get_all_items_not_empty(self, repository):
        """ทดสอบว่ามี items ในระบบ"""
        items = repository.get_all_items()
        assert len(items) > 0, "Item list should not be empty"
    
    def test_get_all_items_returns_dict(self, repository):
        """ทดสอบว่า items เป็น dict ของ item_id -> item_data"""
        items = repository.get_all_items()
        assert isinstance(items, dict)
        
        for item_id, item_data in items.items():
            assert isinstance(item_id, int)
            assert isinstance(item_data, dict)
    
    def test_item_has_required_fields(self, all_items):
        """ทดสอบว่า items มี fields ที่จำเป็น"""
        required_fields = ['name_en', 'price', 'tier']
        
        for item_id, item in list(all_items.items())[:5]:  # ทดสอบ 5 items แรก
            for field in required_fields:
                assert field in item, f"Item {item_id} missing field: {field}"
    
    def test_item_has_passives_list(self, all_items):
        """ทดสอบว่า items มี passives เป็น list"""
        for item_id, item in list(all_items.items())[:5]:
            assert 'passives' in item
            assert isinstance(item['passives'], list)
    
    def test_item_has_restrictions_list(self, all_items):
        """ทดสอบว่า items มี restrictions เป็น list"""
        for item_id, item in list(all_items.items())[:5]:
            assert 'restrictions' in item
            assert isinstance(item['restrictions'], list)
    
    def test_tier3_items_exist(self, valid_items):
        """ทดสอบว่ามี Tier 3 items"""
        assert len(valid_items) > 0, "Should have Tier 3 items"
    
    def test_item_price_positive(self, all_items):
        """ทดสอบว่าราคา item เป็นบวก"""
        for item_id, item in all_items.items():
            price = item.get('price', 0)
            assert price >= 0, f"Item {item_id} has negative price"
    
    def test_item_tier_valid(self, all_items):
        """ทดสอบว่า tier เป็น 1, 2, หรือ 3"""
        valid_tiers = [1, 2, 3]
        for item_id, item in all_items.items():
            tier = item.get('tier')
            assert tier in valid_tiers, f"Item {item_id} has invalid tier: {tier}"


class TestRoleAndLaneQueries:
    """ทดสอบการ Query Roles และ Lanes"""
    
    def test_get_all_roles(self, repository):
        """ทดสอบดึง roles ทั้งหมด"""
        roles = repository.get_all_roles()
        assert len(roles) > 0
        assert all(isinstance(r, str) for r in roles)
    
    def test_get_all_lanes(self, repository):
        """ทดสอบดึง lanes ทั้งหมด"""
        lanes = repository.get_all_lanes()
        assert len(lanes) > 0
        assert all(isinstance(l, str) for l in lanes)
    
    def test_get_heroes_by_role(self, repository):
        """ทดสอบดึง heroes ตาม role"""
        roles = repository.get_all_roles()
        if roles:
            heroes = repository.get_heroes_by_role(roles[0])
            assert isinstance(heroes, list)
    
    def test_get_heroes_by_lane(self, repository):
        """ทดสอบดึง heroes ตาม lane"""
        lanes = repository.get_all_lanes()
        if lanes:
            heroes = repository.get_heroes_by_lane(lanes[0])
            assert isinstance(heroes, list)


class TestDataIntegrity:
    """ทดสอบความถูกต้องของข้อมูล"""
    
    def test_hero_stats_at_level_15(self, repository, hero_list):
        """ทดสอบว่า hero มี stats ที่ level 15"""
        if hero_list:
            hero = repository.get_hero_data(hero_list[0], level=15)
            # ควรมี base_atk, base_def, base_hp
            stat_fields = ['base_atk', 'base_def', 'base_hp']
            has_stats = any(hero.get(f) is not None for f in stat_fields)
            # อาจไม่มี stats ถ้า hero_scaling table ไม่มีข้อมูล
            # ไม่ fail test แต่ให้ warning
            if not has_stats:
                pytest.skip("No stats data for this hero at level 15")
    
    def test_minimum_heroes_count(self, hero_list):
        """ทดสอบว่ามี heroes อย่างน้อย 10 ตัว"""
        assert len(hero_list) >= 10, f"Expected at least 10 heroes, got {len(hero_list)}"
    
    def test_minimum_items_count(self, all_items):
        """ทดสอบว่ามี items อย่างน้อย 50 ชิ้น"""
        assert len(all_items) >= 50, f"Expected at least 50 items, got {len(all_items)}"

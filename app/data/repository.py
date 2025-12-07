# repository.py - จัดการการเข้าถึง database
import sqlite3
from typing import Dict, List, Optional
from app.config import DB_PATH

class RoVRepository:
    """คลาสสำหรับดึงข้อมูล heroes และ items จาก SQLite"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def get_hero_data(self, hero_code_name: str, level: int = 15) -> Optional[Dict]:
        """ดึงข้อมูล hero พร้อม stats ที่ level ที่กำหนด"""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM heroes WHERE code_name = ?", 
                      (hero_code_name.lower(),))
        hero_row = cursor.fetchone()
        
        if not hero_row:
            conn.close()
            return None
            
        cursor.execute("""
            SELECT * FROM hero_scaling 
            WHERE hero_id = ? AND level = ?
        """, (hero_row['hero_id'], level))
        stat_row = cursor.fetchone()
        
        conn.close()
        
        hero_data = dict(hero_row)
        if stat_row:
            hero_data.update(dict(stat_row))
        else:
            print(f"[WARN] No stats found for {hero_code_name} at level {level}")
            
        return hero_data

    def get_all_items(self) -> Dict[int, Dict]:
        """ดึง items ทั้งหมดพร้อม stats, passives และ restrictions"""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT i.*, s.* FROM items i
            LEFT JOIN item_stats s ON i.item_id = s.item_id
            WHERE i.is_active = 1
        """
        cursor.execute(query)
        items = {}
        
        for row in cursor.fetchall():
            item = dict(row)
            item_id = item['item_id']
            item = {k: v for k, v in item.items() if v is not None}
            item['passives'] = []
            item['restrictions'] = []
            items[item_id] = item
            
        # ดึง passives
        cursor.execute("SELECT * FROM item_passives")
        for row in cursor.fetchall():
            if row['item_id'] in items:
                items[row['item_id']]['passives'].append(row['passive_group_name'])
                
        # ดึง restrictions
        cursor.execute("SELECT * FROM item_restrictions")
        for row in cursor.fetchall():
            if row['item_id'] in items:
                items[row['item_id']]['restrictions'].append(row['rule_type'])
                
        conn.close()
        return items
    
    def get_hero_list(self) -> List[str]:
        """ดึงรายชื่อ hero ทั้งหมด"""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT code_name FROM heroes ORDER BY code_name ASC")
            return [row['code_name'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_heroes_by_role(self, role: str) -> List[str]:
        """ดึง heroes ตาม role"""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT code_name FROM heroes 
                WHERE TRIM(primary_role) = ? OR TRIM(secondary_role) = ?
                ORDER BY code_name ASC
            """, (role.strip(), role.strip()))
            return [row['code_name'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_heroes_by_lane(self, lane: str) -> List[str]:
        """ดึง heroes ตาม lane"""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT code_name FROM heroes 
                WHERE TRIM(primary_lane) = ? OR TRIM(secondary_lane) = ?
                ORDER BY code_name ASC
            """, (lane.strip(), lane.strip()))
            return [row['code_name'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all_roles(self) -> List[str]:
        """ดึง roles ทั้งหมดที่มี"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT TRIM(primary_role) as role FROM heroes 
                WHERE primary_role IS NOT NULL
                UNION
                SELECT DISTINCT TRIM(secondary_role) as role FROM heroes 
                WHERE secondary_role IS NOT NULL
                ORDER BY role ASC
            """)
            return [row[0] for row in cursor.fetchall() if row[0]]
        finally:
            conn.close()
    
    def get_all_lanes(self) -> List[str]:
        """ดึง lanes ทั้งหมดที่มี"""
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT TRIM(primary_lane) as lane FROM heroes 
                WHERE primary_lane IS NOT NULL
                UNION
                SELECT DISTINCT TRIM(secondary_lane) as lane FROM heroes 
                WHERE secondary_lane IS NOT NULL
                ORDER BY lane ASC
            """)
            return [row[0] for row in cursor.fetchall() if row[0]]
        finally:
            conn.close()
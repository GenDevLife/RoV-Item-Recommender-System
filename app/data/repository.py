# app/data/repository.py
import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from app.config import DB_PATH

class RoVRepository:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def get_hero_data(self, hero_code_name: str, level: int = 15) -> Optional[Dict]:
        """
        ดึงข้อมูล Hero + Base Stat ที่เลเวลที่กำหนด (Default Lv.15)
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row # เพื่อให้ดึงข้อมูลโดยใช้ชื่อ column ได้
        cursor = conn.cursor()
        
        # 1. ดึง Info หลัก
        cursor.execute("""
            SELECT * FROM heroes WHERE code_name = ?
        """, (hero_code_name.lower(),))
        hero_row = cursor.fetchone()
        
        if not hero_row:
            conn.close()
            return None
            
        # 2. ดึง Scaling Stat (Base Stat)
        cursor.execute("""
            SELECT * FROM hero_scaling 
            WHERE hero_id = ? AND level = ?
        """, (hero_row['hero_id'], level))
        stat_row = cursor.fetchone()
        
        conn.close()
        
        # รวมร่างเป็น Dict เดียว
        hero_data = dict(hero_row)
        if stat_row:
            hero_data.update(dict(stat_row)) # เอา stat มาแปะรวม
        else:
            # Fallback ถ้าไม่มี stat (ไม่ควรเกิดขึ้นถ้า migrate ดี)
            print(f"[WARN] No stats found for {hero_code_name} at level {level}")
            
        return hero_data

    def get_all_items(self) -> Dict[int, Dict]:
        """
        ดึงไอเทมทั้งหมดที่ Active อยู่ พร้อม Stats และ Rules
        Return: Dict {item_id: item_data}
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. ดึง Items + Stats (Join กันเลย)
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
            
            # Clean up: ลบ key ซ้ำ หรือ key ที่เป็น None
            item = {k: v for k, v in item.items() if v is not None}
            
            # เตรียมที่ว่างสำหรับเก็บ Passives/Restrictions
            item['passives'] = []
            item['restrictions'] = []
            
            items[item_id] = item
            
        # 2. ดึง Passives ใส่เข้าไป
        cursor.execute("SELECT * FROM item_passives")
        for row in cursor.fetchall():
            iid = row['item_id']
            if iid in items:
                items[iid]['passives'].append(row['passive_group_name'])
                
        # 3. ดึง Restrictions ใส่เข้าไป
        cursor.execute("SELECT * FROM item_restrictions")
        for row in cursor.fetchall():
            iid = row['item_id']
            if iid in items:
                items[iid]['restrictions'].append(row['rule_type'])
                
        conn.close()
        return items
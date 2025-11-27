from __future__ import annotations
import time
from functools import lru_cache
from typing import Dict, List, Optional, Any

import mysql.connector
from mysql.connector import pooling, Error

import config

_CONNECTION_POOL: Optional[pooling.MySQLConnectionPool] = None

def initialize_connection_pool() -> None:
    """Initialize MySQL connection pool with lazy initialization."""
    global _CONNECTION_POOL
    try:
        _CONNECTION_POOL = pooling.MySQLConnectionPool(
            pool_name='rov_pool', pool_size=3, **config.DB_CONFIG
        )
        print('[INFO] MySQL pool initialized')
    except Error as e:
        print(f'[WARN] Pool init failed: {e} – falling back to direct connect')
        _CONNECTION_POOL = None

def get_connection() -> mysql.connector.connection.MySQLConnection:
    """Get a database connection, retrying with exponential backoff if needed."""
    global _CONNECTION_POOL
    if _CONNECTION_POOL is None:
        initialize_connection_pool()
    tries, delay = 0, 1
    while tries < 4:
        try:
            if _CONNECTION_POOL:
                return _CONNECTION_POOL.get_connection()
            return mysql.connector.connect(**config.DB_CONFIG)
        except Error as e:
            print(f'[WARN] DB connect failed: {e}; retrying in {delay}s')
            time.sleep(delay)
            tries += 1
            delay *= 2
    raise RuntimeError('Cannot connect to MySQL')

# ---------------------------- Data Loading ----------------------------------

@lru_cache(maxsize=None)
def load_item_data() -> Dict[str, Dict[str, float]]:
    """Load item data from the database."""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ItemID, ItemName, Class, Price, Phys_ATK, Magic_Power,
                   Phys_Defense, HP, Cooldown_Reduction, Critical_Rate,
                   Movement_Speed, Attack_Speed, HP_5_sec, Mana_5_sec,
                   Armor_Pierce, Magic_Pierce, Life_Steal, Magic_Life_Steal,
                   Max_Mana, Magic_Defense, Resistance
            FROM items
        """)
        items = {}
        for row in cursor.fetchall():
            for key, value in row.items():
                if key not in ('ItemID', 'ItemName', 'Class'):
                    row[key] = float(value or 0.0)
            items[row['ItemID']] = row
        return items

ITEM_DATA = load_item_data()

@lru_cache(maxsize=128)
def load_hero_stats(hero: str, level: int) -> Dict[str, float]:
    """Load hero base stats at a given level."""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Phys_ATK, Magic_Power, Phys_Defense, HP,
                   Cooldown_Reduction, Critical_Rate, Movement_Speed
            FROM herostats WHERE HeroID=%s AND Level=%s
        """, (hero, level))
        return cursor.fetchone() or {}

@lru_cache(maxsize=128)
def load_stat_caps(hero: str, phase: str, buffer: float = 0.20) -> Dict[str, float]:
    """Load hero stat caps with a buffer."""
    phase_levels = {'Early': 3, 'Mid': 9, 'Late': 15}
    level = phase_levels[phase]
    base_stats = load_hero_stats(hero, level)
    return {stat.upper(): value * (1 + buffer) for stat, value in base_stats.items()}

@lru_cache(maxsize=128)
def get_recommended_item_types(hero: str) -> List[str]:
    """Get recommended item types for a hero."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT RecommendItemType FROM heroskills WHERE HeroID=%s', (hero,))
        return [row[0] for row in cursor.fetchall() if row[0]]

def get_hero_info(hero: str) -> Dict[str, Optional[str]]:
    """คืนข้อมูลคลาสหลัก/รอง และเลนหลักรองของฮีโร่"""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT First_Class, Second_Class, First_Lane, Second_Lane "
            "FROM heroes WHERE HeroID=%s",
            (hero,)
        )
        row = cur.fetchone() or (None, None, None, None)

    first_class, second_class, first_lane, second_lane = row
    # รวบเลนทั้งสอง (ถ้ามี)  ถ้าไม่มีเลยให้ Default เป็น Mid
    lanes = [l for l in (first_lane, second_lane) if l] or ["Mid"]

    return {
        "primary":    first_class   or "Fighter",
        "secondary":  second_class  or None,
        "lanes":      lanes,
        # เพื่อไม่ให้กระทบที่ใช้กันเดิม ยังคงมี field "lane" คืนเป็นเลนแรก (fallback)
        "lane":       first_lane    or second_lane or "Mid",
    }

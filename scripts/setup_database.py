# scripts/setup_database.py
import sqlite3
import pandas as pd
import os
import re

# ==========================================
# ⚙️ Config: Paths relative to project root
# ==========================================
# Get the absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_NAME = os.path.join(BASE_DIR, 'data', 'rov_data.db')

# CSV file paths
CSV_FILES = {
    'heroes': os.path.join(BASE_DIR, 'data', 'raw', 'heroes.csv'),
    'hero_stat': os.path.join(BASE_DIR, 'data', 'raw', 'hero_stat.csv'),
    'item_info': os.path.join(BASE_DIR, 'data', 'raw', 'item_info.csv'),
    'item_ext': os.path.join(BASE_DIR, 'data', 'raw', 'item_extended_info.csv')
}

# ==========================================
# 🛠️ Schema Definition
# ==========================================
def create_schema(cursor):
    print("🔨 Creating Tables...")
    # ลบตารางเก่าทิ้งก่อนเพื่อความสะอาด (Reset)
    cursor.executescript("""
        DROP TABLE IF EXISTS item_restrictions;
        DROP TABLE IF EXISTS item_passives;
        DROP TABLE IF EXISTS item_stats;
        DROP TABLE IF EXISTS items;
        DROP TABLE IF EXISTS hero_scaling;
        DROP TABLE IF EXISTS heroes;

        -- 1. HEROES: ข้อมูลฮีโร่
        CREATE TABLE heroes (
            hero_id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_name VARCHAR(50) NOT NULL UNIQUE,
            name_th VARCHAR(100),
            primary_role VARCHAR(50),
            secondary_role VARCHAR(50),
            damage_type VARCHAR(20),       -- คำนวณจาก Logic
            attack_range_type VARCHAR(20), -- รับจาก CSV หรือคำนวณ
            primary_lane VARCHAR(50),
            secondary_lane VARCHAR(50)
        );

        -- 2. HERO_SCALING: Stat ตามเลเวล
        CREATE TABLE hero_scaling (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hero_id INTEGER NOT NULL,
            level INTEGER NOT NULL,
            base_hp DECIMAL(10,2),
            base_mana DECIMAL(10,2),
            base_atk DECIMAL(10,2),
            base_def DECIMAL(10,2),
            base_mdef DECIMAL(10,2),
            base_aspd_growth DECIMAL(5,4),
            FOREIGN KEY (hero_id) REFERENCES heroes(hero_id)
        );

        -- 3. ITEMS: ข้อมูลไอเทม
        CREATE TABLE items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code VARCHAR(10),
            code_name VARCHAR(50) UNIQUE,
            name_en VARCHAR(100),
            tier INTEGER,
            price INTEGER NOT NULL,
            class VARCHAR(50),
            is_active BOOLEAN DEFAULT 1
        );

        -- 4. ITEM_STATS: ค่าพลังไอเทม
        CREATE TABLE item_stats (
            item_id INTEGER PRIMARY KEY,
            p_atk INTEGER DEFAULT 0, m_power INTEGER DEFAULT 0,
            p_def INTEGER DEFAULT 0, m_def INTEGER DEFAULT 0,
            max_hp INTEGER DEFAULT 0, max_mana INTEGER DEFAULT 0,
            cdr DECIMAL(4,2) DEFAULT 0, crit_rate DECIMAL(4,2) DEFAULT 0,
            move_speed INTEGER DEFAULT 0, aspd DECIMAL(4,2) DEFAULT 0,
            life_steal DECIMAL(4,2) DEFAULT 0, magic_life_steal DECIMAL(4,2) DEFAULT 0,
            p_pierce_flat INTEGER DEFAULT 0, p_pierce_percent DECIMAL(4,2) DEFAULT 0,
            m_pierce_flat INTEGER DEFAULT 0, m_pierce_percent DECIMAL(4,2) DEFAULT 0,
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        );

        -- 5. ITEM_PASSIVES: กลุ่มสกิลติดตัว (ห้ามซ้ำ)
        CREATE TABLE item_passives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            passive_group_name VARCHAR(100),
            description TEXT,
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        );

        -- 6. ITEM_RESTRICTIONS: กฎพิเศษ
        CREATE TABLE item_restrictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            rule_type VARCHAR(50),
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        );
    """)

# ==========================================
# 🧠 Logic Functions (AI Helper)
# ==========================================
def clean_name(name):
    """แปลงชื่อให้เป็นรหัส (code_name) เช่น 'Valhein' -> 'valhein'"""
    if pd.isna(name): return "unknown"
    return re.sub(r'[^a-zA-Z0-9]', '_', str(name).lower().strip())

def calculate_damage_type(p_role, s_role):
    """เดาประเภทดาเมจจาก Role"""
    roles = set()
    if pd.notna(p_role): roles.add(str(p_role).strip().title())
    if pd.notna(s_role): roles.add(str(s_role).strip().title())
    
    # Logic: Mage หรือ Support สายเวท = Magic, นอกนั้น Physical
    if 'Mage' in roles: return 'Magic'
    if 'Support' in roles and not ({'Tank', 'Fighter'} & roles): return 'Magic'
    return 'Physical'

def calculate_tier(price):
    """เดาระดับไอเทมจากราคา"""
    if price < 600: return 1
    if price < 1600: return 2
    return 3

# ==========================================
# 🚀 Main Import Script
# ==========================================
def run_import():
    print(f"🚀 Starting Database Setup for: {DB_NAME}")
    
    # ลบ Database เก่าทิ้งเสมอเพื่อความสะอาด (Clean Start)
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            print(f"🗑️ Removed old database file.")
        except PermissionError:
            print(f"❌ Error: Cannot delete {DB_NAME}. File might be open in another program.")
            return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. สร้างตาราง
    create_schema(cursor)

    # 2. Import Heroes
    print("📥 Importing Heroes...")
    try:
        df_heroes = pd.read_csv(CSV_FILES['heroes'])
        
        # แก้ชื่อคอลัมน์ผิด (Typo) ใน CSV ต้นฉบับ
        if 'sencondary_lane' in df_heroes.columns:
            df_heroes.rename(columns={'sencondary_lane': 'secondary_lane'}, inplace=True)
        if 'secondary_class' not in df_heroes.columns and 'secondary_class' in df_heroes.columns: 
             pass # Handle potential typo variations if needed

        hero_id_map = {} # เก็บ Map ID เก่า -> ID ใหม่

        for _, row in df_heroes.iterrows():
            code_name = clean_name(row['hero_name'])
            
            # คำนวณค่าที่ขาด
            dmg_type = calculate_damage_type(row.get('primary_class'), row.get('secondary_class'))
            range_type = row.get('attack_range', 'Melee')

            cursor.execute("""
                INSERT INTO heroes (
                    code_name, name_th, primary_role, secondary_role, 
                    damage_type, attack_range_type, primary_lane, secondary_lane
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                code_name,
                row['hero_name'], # ใช้ชื่อ Eng เป็นชื่อไทยไปก่อน
                row.get('primary_class'),
                row.get('secondary_class'),
                dmg_type,
                range_type,
                row.get('primary_lane'),
                row.get('secondary_lane')
            ))
            
            # เก็บ ID ใหม่ไว้ใช้กับตาราง Stats
            new_id = cursor.lastrowid
            hero_id_map[row['hero_id']] = new_id
            
        print(f"✅ Heroes Imported: {len(df_heroes)} rows")

    except FileNotFoundError:
        print(f"❌ Error: File '{CSV_FILES['heroes']}' not found.")
        return

    # 3. Import Hero Stats
    print("📥 Importing Hero Stats...")
    try:
        df_stats = pd.read_csv(CSV_FILES['hero_stat'])
        count = 0
        for _, row in df_stats.iterrows():
            if row['hero_id'] in hero_id_map:
                # แก้ชื่อคอลัมน์ผิด physical_degense -> defense
                p_def = row.get('physical_degense', row.get('physical_defense', 0))
                
                cursor.execute("""
                    INSERT INTO hero_scaling (
                        hero_id, level, base_hp, base_mana, base_atk, 
                        base_def, base_mdef, base_aspd_growth
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    hero_id_map[row['hero_id']], 
                    row['level'], 
                    row.get('hp', 0), 
                    row.get('max_mana', 0),
                    row.get('physical_attack', 0), 
                    p_def, 
                    row.get('Magic_Defense', 0), 
                    row.get('attack_speed', 0)
                ))
                count += 1
        print(f"✅ Hero Stats Imported: {count} rows")
        
    except Exception as e:
        print(f"⚠️ Warning: Stats import issue ({e})")

    # 4. Import Items
    print("📥 Importing Items...")
    try:
        # อ่าน 2 ไฟล์ (ไฟล์หลัก + ไฟล์ extended)
        df_info = pd.read_csv(CSV_FILES['item_info'])
        # ไฟล์ extended ใช้ Tab (\t) คั่น
        df_ext = pd.read_csv(CSV_FILES['item_ext'], sep='\t')
        
        # รวมร่างและลบคอลัมน์ขยะ
        df_info = df_info.loc[:, ~df_info.columns.str.contains('^Unnamed')]
        df_items = pd.concat([df_info, df_ext], axis=1)

        for _, row in df_items.iterrows():
            name = str(row['item_name']).strip()
            price = int(row.get('price', 0))
            tier = calculate_tier(price)
            code_name = clean_name(name)
            item_code = row.get('item_id')  # เก็บรหัสไอเทมจาก CSV เช่น I001, I002
            
            # 4.1 Insert Main Info
            cursor.execute("""
                INSERT INTO items (item_code, code_name, name_en, tier, price, class) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item_code, code_name, name, tier, price, row.get('item_class')))
            
            new_item_id = cursor.lastrowid

            # 4.2 Insert Stats (เติม Logic Pierce %)
            p_pierce_pct = 0.40 if 'Muramasa' in name else 0.0
            m_pierce_pct = 0.40 if 'Staff of Nuul' in name else 0.0

            cursor.execute("""
                INSERT INTO item_stats (
                    item_id, p_atk, m_power, p_def, m_def, max_hp, max_mana,
                    cdr, crit_rate, move_speed, aspd, 
                    life_steal, magic_life_steal,
                    p_pierce_percent, m_pierce_percent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_item_id,
                row.get('physical_attack', 0), row.get('magic_power', 0),
                row.get('physical_defense', 0), row.get('magic_defense', 0),
                row.get('hp', 0), row.get('max_mana', 0),
                row.get('cooldown_reduction', 0), row.get('critical_rate', 0),
                row.get('movement_speed', 0), row.get('attack_speed', 0),
                row.get('life_steal', 0), row.get('magic_life_steal', 0),
                p_pierce_pct, m_pierce_pct
            ))
            
            # 4.3 Inject Rules (Passives & Restrictions)
            # กฎรองเท้า
            if 'Boots' in name or row.get('item_class') == 'Movement':
                cursor.execute("INSERT INTO item_restrictions (item_id, rule_type) VALUES (?, ?)", 
                               (new_item_id, 'limit_one_boots'))
                cursor.execute("INSERT INTO item_passives (item_id, passive_group_name) VALUES (?, ?)", 
                               (new_item_id, 'unique_movement'))
            
            # กฎของป่า
            if row.get('item_class') == 'Jungle' or 'Kukri' in name:
                cursor.execute("INSERT INTO item_restrictions (item_id, rule_type) VALUES (?, ?)", 
                               (new_item_id, 'must_have_punish'))

            # กฎ Omni/Frost (ทับกัน)
            if 'Omni' in name or 'Frost Cape' in name:
                cursor.execute("INSERT INTO item_passives (item_id, passive_group_name) VALUES (?, ?)", 
                               (new_item_id, 'elemental_power'))

        print(f"✅ Items Imported: {len(df_items)} rows")

    except Exception as e:
        print(f"❌ Item Import Error: {e}")
        import traceback
        traceback.print_exc()

    # Finalize
    conn.commit()
    conn.close()
    print("\n🎉 SUCCESS: Database 'rov_data.db' is ready to use!")

if __name__ == "__main__":
    run_import()

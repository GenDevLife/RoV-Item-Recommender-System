# 📘 Sum_RoV — สรุป Project แบบละเอียดทุกขั้นตอน

> **Project:** RoV Item Recommender System  
> **เทคโนโลยีหลัก:** Python 3.8+, SQLite, Genetic Algorithm, Ridge Regression (scikit-learn)  
> **วันที่สรุป:** 19 กุมภาพันธ์ 2569

---

## 📑 สารบัญ

1. [ภาพรวมของ Project](#1-ภาพรวมของ-project)
2. [โครงสร้างโฟลเดอร์ (Project Structure)](#2-โครงสร้างโฟลเดอร์-project-structure)
3. [Pipeline ทั้งหมด (End-to-End Pipeline)](#3-pipeline-ทั้งหมด-end-to-end-pipeline)
4. [Data Layer — ข้อมูลและฐานข้อมูล](#4-data-layer--ข้อมูลและฐานข้อมูล)
5. [Core Logic — หัวใจของระบบ](#5-core-logic--หัวใจของระบบ)
6. [Machine Learning Pipeline — การ Calibrate Weights](#6-machine-learning-pipeline--การ-calibrate-weights)
7. [Application Layer — แอปพลิเคชัน CLI](#7-application-layer--แอปพลิเคชัน-cli)
8. [Scripts — เครื่องมือช่วยพัฒนา](#8-scripts--เครื่องมือช่วยพัฒนา)
9. [Testing — ระบบทดสอบ](#9-testing--ระบบทดสอบ)
10. [Flow Diagram สรุป](#10-flow-diagram-สรุป)
11. [เทคโนโลยีและ Dependencies](#11-เทคโนโลยีและ-dependencies)
12. [ข้อจำกัดของระบบ](#12-ข้อจำกัดของระบบ)

---

## 1. ภาพรวมของ Project

### 1.1 จุดประสงค์

ระบบนี้เป็น **ระบบแนะนำชุดไอเทม (Item Build)** สำหรับเกม **Garena RoV (Arena of Valor)** โดยใช้ **Genetic Algorithm (GA)** เป็น AI หลักในการค้นหาชุดไอเทม 6 ชิ้นที่เหมาะสมที่สุดสำหรับแต่ละฮีโร่

### 1.2 แนวคิดหลัก

- **Input:** เลือกฮีโร่ + Role + Lane → ระบบรับ base stats ของฮีโร่
- **Process:** GA สุ่มสร้างชุดไอเทมหลายๆ ชุด แล้ว "วิวัฒนาการ" หาชุดที่ดีที่สุดผ่าน Fitness Function
- **Output:** ชุดไอเทม 6 ชิ้นที่ Fitness Score สูงที่สุด พร้อมสถิติสรุป

### 1.3 โหมดการทำงาน 2 โหมด

| โหมด            | คำอธิบาย                                                                |
| --------------- | ----------------------------------------------------------------------- |
| **All Heroes**  | วิเคราะห์ทุกฮีโร่ทุก Role×Lane combinations แบบ batch → export เป็น CSV |
| **Select Hero** | เลือกฮีโร่ตัวเดียว → เลือก Role, Lane, AI Mode → แสดงผลใน console ทันที |

### 1.4 AI Mode 3 ระดับ

| Mode       | Population | Generations | Mutation Rate | Elitism | เวลาเฉลี่ย | คุณภาพ |
| ---------- | ---------- | ----------- | ------------- | ------- | ---------- | ------ |
| **Fast**   | 30         | 50          | 0.30          | 3       | ~80ms      | Good   |
| **Medium** | 50         | 100         | 0.20          | 2       | ~150ms     | Better |
| **Expert** | 80         | 150         | 0.15          | 4       | ~300ms     | Best   |

---

## 2. โครงสร้างโฟลเดอร์ (Project Structure)

```
RoV-Item-Recommender-System/
│
├── app/                              # 🏠 Application หลัก
│   ├── __init__.py
│   ├── main.py                       # CLI หลัก (RoVRecommender class)
│   ├── config.py                     # ค่าคงที่, GA Profiles, Stat Caps, Penalties
│   ├── core/                         # 🧠 Core Logic
│   │   ├── __init__.py
│   │   ├── evaluator.py              # Fitness Function (BuildEvaluator class)
│   │   ├── ga_engine.py              # Genetic Algorithm Engine (GeneticEngine class)
│   │   ├── passive_manager.py        # ตรวจ Unique Passive ซ้ำ (PassiveManager class)
│   │   └── learned_weights.json      # Weights ที่ calibrate แล้ว (ผลจาก ML)
│   ├── data/                         # 💾 Data Access Layer
│   │   ├── __init__.py
│   │   └── repository.py             # Repository Pattern (RoVRepository class)
│   └── utils/                        # 🔧 Utilities
│       ├── __init__.py
│       └── logger.py                 # Logging (colorlog + rotating file)
│
├── data/                             # 📂 ข้อมูลทั้งหมด
│   ├── rov_data.db                   # SQLite Database (heroes, items, stats)
│   └── raw/                          # ข้อมูลดิบ CSV
│       ├── heroes.csv                # ข้อมูลฮีโร่ (ชื่อ, role, lane)
│       ├── hero_stat.csv             # Stat แต่ละ level (HP, ATK, DEF...)
│       ├── hero_skill.csv            # ข้อมูลสกิล
│       ├── item_info.csv             # ข้อมูลไอเทมหลัก
│       ├── item_extended_info.csv    # ข้อมูลไอเทมเพิ่มเติม (tab-separated)
│       ├── item_composition.csv      # ส่วนประกอบไอเทม
│       ├── synthetic_training_data.csv  # ข้อมูล training สังเคราะห์ (2000 records)
│       └── test_fitness.csv          # ข้อมูลจริงสำหรับ calibrate
│
├── scripts/                          # 🛠️ Script เครื่องมือต่างๆ
│   ├── setup_database.py             # สร้าง/reset database จาก CSV
│   ├── generate_training_data.py     # สร้าง synthetic training data
│   ├── calibrate.py                  # Calibrate weights ด้วย Ridge Regression
│   ├── tune_ga.py                    # Tune GA parameters
│   ├── tune_alpha.py                 # Tune Ridge Regression alpha
│   ├── compare_profiles.py           # เปรียบเทียบ Fast/Medium/Expert
│   ├── analyze_results.py            # วิเคราะห์ learned weights
│   ├── visualize_results.py          # แสดงผล ASCII charts
│   ├── test_recommendations.py       # ทดสอบ recommendations อัตโนมัติ
│   ├── check_db_info.py              # ตรวจสอบข้อมูลใน database
│   └── check_schema.py              # ตรวจสอบ schema ใน database
│
├── tests/                            # 🧪 Unit Tests (pytest)
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures, test configurations
│   ├── test_repository.py            # ทดสอบ data access layer
│   ├── test_evaluator.py             # ทดสอบ fitness function
│   ├── test_ga_engine.py             # ทดสอบ GA engine
│   └── test_passive_manager.py       # ทดสอบ passive conflict checks
│
├── docs/                             # 📚 เอกสาร
│   ├── USER_GUIDE.md
│   ├── RoV_Project_Complete_Logic_Explanation.txt
│   ├── Report.xlsx
│   └── image/                        # รูปภาพประกอบ
│
├── logs/                             # 📝 Log files (auto-generated)
├── requirements.txt                  # Dependencies
├── all_heroes_analysis.csv           # ผลลัพธ์ batch analysis
└── README.md                         # เอกสารหลัก
```

---

## 3. Pipeline ทั้งหมด (End-to-End Pipeline)

### 3.1 Overview Pipeline

ระบบทำงานใน 2 Pipeline หลัก:

#### Pipeline A: Data Preparation (ทำครั้งเดียว / เมื่อต้องการ update)

```
CSV Files ──→ setup_database.py ──→ SQLite DB (rov_data.db)
                                         │
                                         ▼
                              generate_training_data.py ──→ synthetic_training_data.csv
                                                                    │
                                                                    ▼
                                                           calibrate.py ──→ learned_weights.json
```

**ขั้นตอน:**

1. **สร้าง Database** — `scripts/setup_database.py` อ่าน CSV 4 ไฟล์ (heroes.csv, hero_stat.csv, item_info.csv, item_extended_info.csv) แล้ว import ลง SQLite
2. **สร้าง Training Data** — `scripts/generate_training_data.py` สุ่มชุดไอเทม 2000 ชุด แล้วคำนวณ score จาก ground truth weights
3. **Calibrate Weights** — `scripts/calibrate.py` ใช้ Ridge Regression เรียนรู้ weights จาก training data → บันทึกเป็น `learned_weights.json`

#### Pipeline B: Recommendation (ใช้งานจริง)

```
User Input (Hero, Role, Lane, Mode)
       │
       ▼
   RoVRepository  ──→  ดึง hero_data + all_items จาก SQLite
       │
       ▼
   BuildEvaluator  ──→  โหลด learned_weights.json + กำหนด fitness function
       │
       ▼
   GeneticEngine  ──→  รัน GA (Initialize → Evaluate → Select → Crossover → Mutate → Repeat)
       │
       ▼
   Best Build (6 items) + Fitness Score ──→ แสดงผลใน Console / บันทึก CSV
```

### 3.2 ลำดับการทำงานละเอียด

```
1. [Startup] main.py สร้าง RoVRecommender instance
     │
     ├── สร้าง RoVRepository เชื่อมต่อ SQLite
     ├── โหลด all_items จาก DB (items + stats + passives + restrictions)
     └── กรอง valid_items เฉพาะ Tier 3

2. [User Selection] ผู้ใช้เลือก Hero → Role → Lane → AI Mode

3. [Recommendation] get_recommendation() ถูกเรียก
     │
     ├── [3.1] repo.get_hero_data(hero_code, level=15)
     │         ดึง hero base stats ที่ level 15
     │
     ├── [3.2] สร้าง BuildEvaluator(hero_data, all_items)
     │         ├── โหลด learned_weights.json
     │         └── ถ้าโหลดไม่ได้ → ใช้ default weights ตาม damage_type
     │
     ├── [3.3] สร้าง GeneticEngine(evaluator, valid_items, ga_settings)
     │         ├── POP_SIZE, MAX_GEN, MUTATION_RATE, ELITISM_COUNT
     │
     └── [3.4] engine.run() → GA Loop
               │
               ├── สร้าง initial population (สุ่ม 6 items ไม่ซ้ำ × POP_SIZE)
               │
               └── Loop MAX_GEN รอบ:
                    ├── คำนวณ fitness ทุกตัว
                    │     ├── check passive conflicts → penalty
                    │     ├── check boots limit → penalty
                    │     ├── calculate_stats (hero base + item bonuses)
                    │     ├── enforce stat caps (CDR 40%, Crit 100%, ASPD 200%)
                    │     └── weighted sum ตาม learned weights
                    │
                    ├── เรียงลำดับ (best → worst)
                    ├── เก็บ best_solution ถ้าดีกว่าเดิม
                    ├── Elitism: คัดลอก top N ตัวไปรุ่นถัดไปโดยตรง
                    └── สร้างรุ่นถัดไป:
                         ├── Tournament Selection (top 10)
                         ├── Single-point Crossover
                         ├── Mutation (สุ่มเปลี่ยน 1 item)
                         └── Ensure unique items (ไม่มี item ซ้ำ)

4. [Output] แสดงผล build (ชื่อ item, ราคา, stats, score, mode, เวลา)
```

---

## 4. Data Layer — ข้อมูลและฐานข้อมูล

### 4.1 ไฟล์ CSV ต้นทาง

| ไฟล์                          | คำอธิบาย                                                                                      | ขนาด                      |
| ----------------------------- | --------------------------------------------------------------------------------------------- | ------------------------- |
| `heroes.csv`                  | ข้อมูลฮีโร่: ชื่อ, primary_class, secondary_class, primary_lane, secondary_lane, attack_range | ~5KB, ~70 heroes          |
| `hero_stat.csv`               | Base stats ต่อ level: hp, mana, atk, def, mdef, aspd                                          | ~75KB, 15 levels ต่อ hero |
| `item_info.csv`               | ข้อมูลไอเทมหลัก: ชื่อ, ราคา, class, stats                                                     | ~7KB                      |
| `item_extended_info.csv`      | ข้อมูลเพิ่มเติม (tab-separated): stats เพิ่มเติม                                              | ~2.5KB                    |
| `synthetic_training_data.csv` | Training data สังเคราะห์: 2000 builds + NoisyScore                                            | ~127KB                    |
| `test_fitness.csv`            | ข้อมูลจริงสำหรับ calibrate                                                                    | ~40KB                     |

### 4.2 SQLite Database Schema (rov_data.db)

Database ประกอบด้วย 6 ตาราง:

#### Table 1: `heroes` — ข้อมูลฮีโร่

```sql
CREATE TABLE heroes (
    hero_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_name VARCHAR(50) NOT NULL UNIQUE,    -- เช่น 'valhein', 'tachi'
    name_th VARCHAR(100),                      -- ชื่อแสดงผล (ใช้ชื่ออังกฤษ)
    primary_role VARCHAR(50),                  -- เช่น 'Marksman', 'Fighter'
    secondary_role VARCHAR(50),
    damage_type VARCHAR(20),                   -- 'Physical' / 'Magic' (คำนวณจาก Logic)
    attack_range_type VARCHAR(20),             -- 'Melee' / 'Ranged'
    primary_lane VARCHAR(50),                  -- เช่น 'Dragon Slayer', 'Mid'
    secondary_lane VARCHAR(50)
);
```

#### Table 2: `hero_scaling` — Stat ต่อ Level

```sql
CREATE TABLE hero_scaling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hero_id INTEGER NOT NULL,
    level INTEGER NOT NULL,                    -- 1-15
    base_hp DECIMAL, base_mana DECIMAL,
    base_atk DECIMAL, base_def DECIMAL,
    base_mdef DECIMAL, base_aspd_growth DECIMAL,
    FOREIGN KEY (hero_id) REFERENCES heroes(hero_id)
);
```

#### Table 3: `items` — ข้อมูลไอเทม

```sql
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_code VARCHAR(10),                     -- รหัสจาก CSV เช่น 'I001'
    code_name VARCHAR(50) UNIQUE,              -- ชื่อ normalized
    name_en VARCHAR(100),                      -- ชื่อแสดงผล
    tier INTEGER,                              -- 1/2/3 (คำนวณจากราคา)
    price INTEGER NOT NULL,
    class VARCHAR(50),                         -- เช่น 'Attack', 'Magic', 'Defense'
    is_active BOOLEAN DEFAULT 1
);
```

#### Table 4: `item_stats` — ค่าพลังไอเทม

```sql
CREATE TABLE item_stats (
    item_id INTEGER PRIMARY KEY,
    p_atk INTEGER DEFAULT 0,                   -- Physical Attack
    m_power INTEGER DEFAULT 0,                 -- Magic Power
    p_def INTEGER DEFAULT 0,                   -- Physical Defense
    m_def INTEGER DEFAULT 0,                   -- Magic Defense
    max_hp INTEGER DEFAULT 0,
    max_mana INTEGER DEFAULT 0,
    cdr DECIMAL DEFAULT 0,                     -- Cooldown Reduction (0.00-0.40)
    crit_rate DECIMAL DEFAULT 0,               -- Critical Rate (0.00-1.00)
    move_speed INTEGER DEFAULT 0,
    aspd DECIMAL DEFAULT 0,                    -- Attack Speed bonus
    life_steal DECIMAL DEFAULT 0,
    magic_life_steal DECIMAL DEFAULT 0,
    p_pierce_flat INTEGER DEFAULT 0,           -- Physical Pierce (flat)
    p_pierce_percent DECIMAL DEFAULT 0,        -- Physical Pierce (%, e.g., 0.40 = 40%)
    m_pierce_flat INTEGER DEFAULT 0,
    m_pierce_percent DECIMAL DEFAULT 0,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);
```

#### Table 5: `item_passives` — Unique Passive Groups

```sql
CREATE TABLE item_passives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    passive_group_name VARCHAR(100),            -- เช่น 'elemental_power', 'unique_movement'
    description TEXT,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);
```

**กฎ Passive ที่ถูก inject:**

- **Boots** → passive group: `unique_movement`
- **Omni Arms / Frost Cape** → passive group: `elemental_power`

#### Table 6: `item_restrictions` — กฎพิเศษ

```sql
CREATE TABLE item_restrictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    rule_type VARCHAR(50),                     -- เช่น 'limit_one_boots', 'must_have_punish'
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);
```

**กฎที่ถูก inject:**

- **Boots / Movement items** → `limit_one_boots`
- **Jungle items / Kukri** → `must_have_punish`

### 4.3 Data Access: RoVRepository (`app/data/repository.py`)

ใช้ **Repository Pattern** เพื่อแยก data access ออกจาก business logic:

```python
class RoVRepository:
    def get_hero_data(hero_code_name, level=15) → Dict    # ดึงข้อมูล hero + stats ที่ level 15
    def get_all_items() → Dict[int, Dict]                  # ดึง items ทั้งหมด + stats + passives + restrictions
    def get_hero_list() → List[str]                        # ดึงรายชื่อ hero ทั้งหมด
    def get_heroes_by_role(role) → List[str]               # กรอง hero ตาม role
    def get_heroes_by_lane(lane) → List[str]               # กรอง hero ตาม lane
    def get_all_roles() → List[str]                        # ดึง roles ทั้งหมด
    def get_all_lanes() → List[str]                        # ดึง lanes ทั้งหมด
```

**จุดสำคัญ:**

- ใช้ `sqlite3.Row` เพื่อให้เข้าถึงได้ทั้ง index และ column name
- `get_all_items()` JOIN ข้อมูล 3 ตาราง (items + item_stats + item_passives + item_restrictions) เป็น dictionary เดียว
- `get_hero_data()` JOIN heroes + hero_scaling ที่ level ที่ต้องการ (default level 15)

### 4.4 Database Setup Logic (`scripts/setup_database.py`)

การ import ข้อมูลมี **business logic** ที่น่าสนใจ:

1. **damage_type** ไม่ได้มาจาก CSV โดยตรง — ถูกคำนวณจาก role:

   ```
   ถ้ามี role 'Mage' → damage_type = 'Magic'
   ถ้ามี role 'Support' แต่ไม่มี Tank/Fighter → damage_type = 'Magic'
   อื่นๆ → damage_type = 'Physical'
   ```

2. **tier** ของไอเทมคำนวณจากราคา:

   ```
   ราคา < 600  → Tier 1
   ราคา < 1600 → Tier 2
   ราคา ≥ 1600 → Tier 3
   ```

3. **Pierce %** ถูก hardcode สำหรับไอเทมเฉพาะ:

   ```
   Muramasa    → p_pierce_percent = 0.40 (40%)
   Staff of Nuul → m_pierce_percent = 0.40 (40%)
   ```

4. **Passive Rules** ถูก inject ตาม logic:
   - ชื่อมี "Boots" หรือ class เป็น "Movement" → เพิ่ม restriction `limit_one_boots` + passive `unique_movement`
   - class เป็น "Jungle" หรือชื่อมี "Kukri" → เพิ่ม restriction `must_have_punish`
   - ชื่อมี "Omni" หรือ "Frost Cape" → เพิ่ม passive `elemental_power`

---

## 5. Core Logic — หัวใจของระบบ

### 5.1 Configuration (`app/config.py`)

#### Stat Caps (ข้อจำกัดในเกม)

```python
STATS_CAPS = {
    "cdr": 0.40,        # CDR สูงสุด 40%
    "aspd": 2.00,       # ASPD สูงสุด 200%
    "crit_rate": 1.00,  # Crit สูงสุด 100%
    "move_speed": 800   # Move Speed (soft cap)
}
```

#### Penalties (ค่าปรับลดคะแนน)

```python
PENALTIES = {
    "duplicate_passive": -50.0,    # Passive ซ้ำ
    "boots_limit": -100.0,         # รองเท้าเกิน 1
    "jungle_wrong": -200.0,        # ไอเทมป่าโดยไม่มี spell
    "support_limit": -100.0        # ไอเทม support เกิน
}
```

### 5.2 Passive Manager (`app/core/passive_manager.py`)

**หน้าที่:** ตรวจสอบว่าชุดไอเทมมี **unique passive ซ้ำกัน**หรือไม่

**Logic:**

```
สำหรับแต่ละ item ใน build:
    สำหรับแต่ละ passive group ของ item:
        ถ้า passive group นี้เคยเห็นแล้ว:
            → เพิ่ม penalty -50.0
            → บันทึก conflict message
        มิฉะนั้น:
            → เพิ่ม passive group เข้า seen set
```

**ตัวอย่าง:** ถ้ามีทั้ง Omni Arms และ Frost Cape (ทั้งคู่อยู่ใน group `elemental_power`) → penalty -50

### 5.3 Build Evaluator — Fitness Function (`app/core/evaluator.py`)

นี่คือ **หัวใจของระบบ** — ฟังก์ชันที่ตัดสินว่าชุดไอเทมดีแค่ไหน

#### 5.3.1 การโหลด Weights

```
ลองโหลดจาก learned_weights.json (ผลจาก ML calibration)
    → สำเร็จ: ใช้ learned weights
    → ล้มเหลว: ใช้ default weights ตาม damage_type
```

**Default Weights (ถ้าไม่มี learned_weights.json):**

| Stat         | Physical Hero | Magic Hero |
| ------------ | ------------- | ---------- |
| p_atk        | 1.0           | 0.0        |
| ap (m_power) | 0.0           | 1.0        |
| hp           | 0.1           | 0.1        |
| cdr          | —             | 50.0       |
| aspd         | 20.0          | —          |
| crit         | 50.0          | —          |
| p_pierce     | 0.5           | —          |
| m_pierce     | —             | 0.5        |
| move_speed   | 0.05          | 0.05       |

**Learned Weights (จาก calibration — ค่าจริงที่ระบบใช้):**

```json
{
  "p_atk": 0.15,
  "m_power": 0.15,
  "max_hp": 0.001,
  "p_def": 0.01,
  "m_def": 0.01,
  "cdr": 0.2,
  "aspd": 0.5,
  "crit_rate": 0.8,
  "p_pierce_percent": 1.2,
  "m_pierce_percent": 1.2,
  "move_speed": 0.1
}
```

#### 5.3.2 การคำนวณ Stats (`calculate_stats`)

```python
stats = {
    "p_atk":    hero.base_atk (default 100),
    "p_def":    hero.base_def (default 50),
    "max_hp":   hero.base_hp (default 3000),
    "m_power":  0.0,
    "cdr":      0.0,
    "aspd":     0.0,
    "crit_rate": 0.0,
    "move_speed": 350.0,
    "p_pierce_percent": 0.0,
    "m_pierce_percent": 0.0,
}

# รวม stats จากไอเทมทุกชิ้น
for item in chromosome:
    stats["p_atk"]  += item.p_atk
    stats["m_power"] += item.m_power
    stats["p_def"]  += item.p_def
    stats["max_hp"] += item.max_hp
    stats["cdr"]    += item.cdr
    stats["aspd"]   += item.aspd
    stats["crit_rate"] += item.crit_rate
    stats["move_speed"] += item.move_speed
    # Pierce ใช้ค่าสูงสุด (ไม่สะสม)
    stats["p_pierce_percent"] = max(current, item.p_pierce_percent)
    stats["m_pierce_percent"] = max(current, item.m_pierce_percent)
```

> **หมายเหตุ:** Pierce % ใช้ `max()` ไม่ใช่ `+=` เพราะในเกมจริง pierce % ไม่สะสม

#### 5.3.3 การคำนวณ Fitness (`get_fitness`)

```
score = 0.0

# 1. ตรวจ Passive Conflicts → penalty
score += passive_manager.check_passive_conflicts(items)

# 2. ตรวจรองเท้าซ้ำ → penalty
if boots_count > 1:
    score += -100.0 × (boots_count - 1)

# 3. คำนวณ stats (hero base + all items)
stats = calculate_stats(chromosome)

# 4. บังคับ Stat Caps
effective_cdr  = min(stats.cdr, 0.40)
effective_crit = min(stats.crit_rate, 1.00)
effective_aspd = min(stats.aspd, 2.00)

# 5. คำนวณ Weighted Score
score += stats.p_atk × weight_p_atk
score += stats.m_power × weight_ap
score += stats.max_hp × weight_hp
score += effective_cdr × weight_cdr
score += effective_aspd × weight_aspd
score += effective_crit × weight_crit
score += stats.p_pierce_percent × 100 × weight_p_pierce
score += stats.m_pierce_percent × 100 × weight_m_pierce

return score
```

### 5.4 Genetic Algorithm Engine (`app/core/ga_engine.py`)

#### 5.4.1 Representation (การแทนค่า)

- **Chromosome:** List ของ 6 item IDs (integers) → `[12, 45, 3, 78, 22, 56]`
- **Population:** List ของ chromosomes (ขนาด = POP_SIZE)
- **Gene:** แต่ละ item ID ใน chromosome

#### 5.4.2 Initialization

```python
def create_chromosome():
    return random.sample(item_pool, 6)  # สุ่ม 6 ไอเทมไม่ซ้ำจาก Tier 3 ทั้งหมด
```

#### 5.4.3 Selection Strategy

- **Elitism:** คัดลอก top `ELITISM_COUNT` ตัวไปรุ่นถัดไปโดยตรง
- **Tournament Selection:** เลือก parent จาก top 10 ตัว (แบบ random)

#### 5.4.4 Crossover (Single-point)

```python
def crossover(parent1, parent2):
    point = random.randint(1, 5)           # จุดตัด 1-5
    child = parent1[:point] + parent2[point:]
    return ensure_unique_items(child)       # แก้ item ซ้ำ
```

**ตัวอย่าง:**

```
Parent1: [A, B, C, D, E, F]    point = 3
Parent2: [G, H, I, J, K, L]
Child:   [A, B, C, J, K, L]    → ensure_unique_items()
```

#### 5.4.5 Mutation

```python
def mutate(chromosome):
    if random.random() < mutation_rate:     # ตามความน่าจะเป็น
        idx = random.randint(0, 5)          # เลือก slot สุ่ม
        available = [i for i in item_pool if i not in chromosome]
        chromosome[idx] = random.choice(available)  # เปลี่ยนเป็น item ใหม่
    return chromosome
```

#### 5.4.6 Ensure Unique Items

```python
def ensure_unique_items(chromosome):
    # ถ้ามี item ซ้ำ → แทนที่ด้วย item ที่ยังไม่ได้ใช้
    seen = set()
    for each item:
        if item in seen:
            replace with random unused item
        else:
            add to seen
```

#### 5.4.7 Main GA Loop

```python
def run():
    population = [create_chromosome() × POP_SIZE]
    best_solution = None
    best_fitness = -999999.0

    for gen in range(MAX_GEN):
        # 1. Evaluate all
        scores = [(chrom, fitness(chrom)) for chrom in population]
        scores.sort(by fitness, descending)

        # 2. Track global best
        if scores[0].fitness > best_fitness:
            best_fitness = scores[0].fitness
            best_solution = scores[0].chromosome

        # 3. Build next generation
        next_gen = top ELITISM_COUNT chromosomes  # Elitism

        while len(next_gen) < POP_SIZE:
            parent1 = random from top 10
            parent2 = random from top 10
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_gen.append(child)

        population = next_gen

    return best_solution, best_fitness
```

---

## 6. Machine Learning Pipeline — การ Calibrate Weights

### 6.1 ทำไมต้อง Calibrate?

Default weights ถูกตั้งด้วย domain knowledge (เช่น crit สำคัญกว่า HP สำหรับ AD carry) แต่อาจไม่แม่นที่สุด → ใช้ **Machine Learning** เรียนรู้ weights จากข้อมูลจริง/สังเคราะห์

### 6.2 Synthetic Training Data Generation (`scripts/generate_training_data.py`)

**ขั้นตอน:**

1. **ตั้ง Ground Truth Weights** (domain knowledge):

   ```python
   TRUE_WEIGHTS = {
       'p_atk': 0.15, 'm_power': 0.15, 'max_hp': 0.001,
       'p_def': 0.01, 'm_def': 0.01, 'cdr': 0.20,
       'aspd': 0.50, 'crit_rate': 0.80, 'p_pierce_percent': 1.20,
       'm_pierce_percent': 1.20, 'move_speed': 0.10
   }
   ```

2. **สุ่ม Build 2000 ชุด:**
   - สุ่ม 4-6 ไอเทมจาก pool (ไม่ซ้ำ)
   - คำนวณ stats ด้วย BuildEvaluator

3. **คำนวณ TrueScore:**

   ```
   TrueScore = Σ (stat_i × weight_i)
   ```

4. **เพิ่ม Noise 5%:**

   ```
   NoisyScore = TrueScore + Gaussian(μ=0, σ=0.05 × TrueScore)
   ```

5. **บันทึก CSV** (HeroID, Class, Lane, Item1-6, TrueScore, NoisyScore, CombatPower)

### 6.3 Ridge Regression Calibration (`scripts/calibrate.py`)

**เทคนิค:** Ridge Regression (L2 Regularization)

**ขั้นตอน:**

1. **โหลดข้อมูล** จาก CSV (synthetic หรือ real)
2. **Extract Features:** สำหรับแต่ละ build → คำนวณ 11 stats เป็น feature vector
   ```
   Features = [p_atk, m_power, max_hp, p_def, m_def, cdr, aspd,
                crit_rate, p_pierce_percent, m_pierce_percent, move_speed]
   ```
3. **StandardScaler:** ปรับ features ให้มี mean=0, std=1 (Z-score normalization)
   - จำเป็นเพราะ stats มีสเกลต่างกันมาก (HP ~3000 vs CDR ~0.40)
4. **Ridge Regression:**
   ```
   model = Ridge(alpha=1.0)
   model.fit(X_scaled, y)
   ```

   - `alpha` = 1.0 (regularization strength, ป้องกัน overfitting)
5. **Un-normalize Coefficients:**
   ```
   w_raw = w_scaled / std_of_feature
   ```

   - จำเป็นเพราะ Evaluator ใช้ raw stats ไม่ใช่ scaled stats
6. **บันทึก** เป็น `learned_weights.json`

### 6.4 Alpha Tuning (`scripts/tune_alpha.py`)

ทดสอบ alpha 9 ค่า: `0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0`

**เมตริก:**

- **CV Score (R²):** Cross-validation 5-fold R² score
- **Average Error %:** เปรียบเทียบ learned weights กับ ground truth weights

**เลือก alpha ที่ให้ Average Error % ต่ำที่สุด**

---

## 7. Application Layer — แอปพลิเคชัน CLI

### 7.1 Class: RoVRecommender (`app/main.py`)

**คลาสหลักที่รวมทุกส่วนเข้าด้วยกัน:**

| Method                                              | หน้าที่                                                       |
| --------------------------------------------------- | ------------------------------------------------------------- |
| `__init__()`                                        | สร้าง Repository, โหลด items, กรอง Tier 3                     |
| `get_recommendation(hero, role, lane, profile)`     | สร้าง build recommendation → return (build, score, hero_data) |
| `format_build_output(build, hero_data, score, ...)` | จัดรูปแบบผลลัพธ์                                              |
| `get_hero_role_lane_combinations(hero)`             | ดึง role×lane combinations                                    |
| `analyze_all_heroes(profile, output_file)`          | Batch analysis → CSV                                          |
| `select_hero_mode()`                                | UI เลือก hero เดี่ยว                                          |

### 7.2 UI Library: Questionary

ใช้ **questionary** สำหรับ interactive CLI menus:

- `questionary.select()` — เลือกจาก list
- `questionary.confirm()` — ยืนยัน yes/no
- `questionary.text()` — ใส่ข้อความ
- Custom style: สีม่วง (#673ab7) เป็นสีหลัก

### 7.3 All Heroes Mode Flow

```
1. โหลด hero_list ทั้งหมด
2. สำหรับแต่ละ hero → ดึง role×lane combinations
3. นับ total combinations
4. วน loop ทุก combination (ด้วย tqdm progress bar):
     a. get_recommendation(hero, role, lane, "expert")
     b. คำนวณ stats, items, total_cost
     c. เก็บผลลัพธ์ (hero_code, hero_name, role, lane, damage_type,
                      fitness_score, item_1-6, total_cost, final stats, time_ms)
5. สร้าง DataFrame → บันทึก CSV (UTF-8 BOM)
6. แสดงสรุป (จำนวน, avg score, avg time, total time)
```

### 7.4 Logging System (`app/utils/logger.py`)

- **Console:** สีตาม level (green=INFO, yellow=WARN, red=ERROR) ด้วย `colorlog`
- **File:** Rotating file handler (10MB max, 5 backups) ใน `logs/rov_recommender.log`
- **Format:** `LEVEL [RoV-AI] message` (console), `timestamp - RoV-AI - LEVEL - message` (file)

---

## 8. Scripts — เครื่องมือช่วยพัฒนา

| Script                      | หน้าที่                                                       | เมื่อใช้                                 |
| --------------------------- | ------------------------------------------------------------- | ---------------------------------------- |
| `setup_database.py`         | สร้าง/reset SQLite database จาก CSV                           | ตอน setup ครั้งแรก หรือเมื่อ CSV เปลี่ยน |
| `generate_training_data.py` | สุ่ม builds 2000 ชุด → synthetic_training_data.csv            | ก่อน calibrate                           |
| `calibrate.py`              | Train Ridge Regression → learned_weights.json                 | หลัง generate training data              |
| `tune_ga.py`                | ทดสอบ GA parameters 12 configs × 3 heroes × 3 runs            | เมื่อต้องการหา GA settings ที่ดีที่สุด   |
| `tune_alpha.py`             | ทดสอบ Ridge alpha 9 ค่า + cross-validation                    | เมื่อต้องการหา alpha ที่ดีที่สุด         |
| `compare_profiles.py`       | เปรียบเทียบ Fast/Medium/Expert 3 profiles × 3 heroes × 5 runs | เมื่อต้องการเปรียบเทียบ profiles         |
| `analyze_results.py`        | แสดง learned weights, วิเคราะห์ไอเทมที่สำคัญ                  | เมื่อต้องการดู weights                   |
| `visualize_results.py`      | แสดง ASCII charts จาก ga_tuning_results.csv                   | หลัง tune_ga.py                          |
| `test_recommendations.py`   | ทดสอบ recommendations กับหลาย heroes                          | Sanity check                             |
| `check_db_info.py`          | ตรวจ database info                                            | Debugging                                |
| `check_schema.py`           | ตรวจ database schema                                          | Debugging                                |

### 8.1 GA Tuning Configs ที่ทดสอบ (`tune_ga.py`)

```
12 configurations:
├── Baseline (Pop=50, Gen=100, Mut=0.2, Elite=2)
├── Population Size: Small(20), Large(100)
├── Generations: Quick(50), Deep(200)
├── Mutation Rate: Low(0.1), High(0.3), Very High(0.5)
├── Elitism: None(0), High(5)
└── Combos: Fast&Furious(30/50/0.3/3), Slow&Steady(80/150/0.15/4)
```

---

## 9. Testing — ระบบทดสอบ

### 9.1 Framework: pytest

### 9.2 Fixtures (conftest.py)

| Fixture                | Scope    | คำอธิบาย                         |
| ---------------------- | -------- | -------------------------------- |
| `db_path`              | session  | Path ไป database                 |
| `repository`           | session  | RoVRepository instance           |
| `all_items`            | session  | Items ทั้งหมด                    |
| `valid_items`          | session  | Tier 3 item IDs                  |
| `hero_list`            | session  | ชื่อ heroes ทั้งหมด              |
| `sample_hero_physical` | function | Valhein (Physical)               |
| `sample_hero_magic`    | function | Krixi/Lauriel (Magic)            |
| `dummy_hero`           | function | Mock hero data                   |
| `sample_build`         | function | Random 6 items                   |
| `evaluator`            | function | BuildEvaluator instance          |
| `ga_engine`            | function | GeneticEngine (minimal settings) |
| `passive_manager`      | function | PassiveManager instance          |
| `temp_db`              | function | Temporary database copy          |
| `timer`                | function | Performance timer                |

### 9.3 Test Files

| File                      | ทดสอบ                                               | จำนวน Tests |
| ------------------------- | --------------------------------------------------- | ----------- |
| `test_repository.py`      | ดึงข้อมูล hero, items, roles, lanes, data integrity | ~10 tests   |
| `test_evaluator.py`       | Fitness calculation, stat caps, penalties, weights  | ~12 tests   |
| `test_ga_engine.py`       | Chromosome creation, crossover, mutation, GA run    | ~14 tests   |
| `test_passive_manager.py` | Passive conflicts, boots limit                      | ~8 tests    |

---

## 10. Flow Diagram สรุป

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PREPARATION PIPELINE                     │
│                                                                  │
│  CSV Files ──→ setup_database.py ──→ SQLite DB                  │
│                                        │                        │
│                                        ▼                        │
│  generate_training_data.py ──→ synthetic_training_data.csv      │
│                                        │                        │
│                                        ▼                        │
│  calibrate.py (Ridge Regression) ──→ learned_weights.json       │
│                                                                  │
│  (Optional) tune_ga.py ──→ optimal GA parameters                │
│  (Optional) tune_alpha.py ──→ optimal Ridge alpha               │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RECOMMENDATION PIPELINE                       │
│                                                                  │
│  User Input ──→ RoVRecommender                                  │
│                    │                                             │
│                    ├── RoVRepository ──→ hero_data + items       │
│                    │                                             │
│                    ├── BuildEvaluator ──→ fitness function       │
│                    │     ├── learned_weights.json                │
│                    │     ├── PassiveManager (conflict check)     │
│                    │     ├── stat caps enforcement               │
│                    │     └── weighted score calculation          │
│                    │                                             │
│                    └── GeneticEngine ──→ evolution loop          │
│                          ├── Initialize (random population)     │
│                          ├── Evaluate (fitness)                 │
│                          ├── Select (elitism + tournament)      │
│                          ├── Crossover (single-point)           │
│                          ├── Mutate (single-gene replacement)   │
│                          └── Repeat × MAX_GEN                   │
│                                 │                               │
│                                 ▼                               │
│                    Best Build (6 items) + Score                  │
│                                 │                               │
│                    ┌────────────┴────────────┐                  │
│                    ▼                         ▼                  │
│              Console Output           CSV Export                │
│         (Select Hero Mode)       (All Heroes Mode)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. เทคโนโลยีและ Dependencies

| Library        | Version  | ใช้ทำอะไร                                          |
| -------------- | -------- | -------------------------------------------------- |
| `pandas`       | ≥2.0.0   | อ่าน CSV, สร้าง DataFrame, export CSV              |
| `numpy`        | ≥1.24.0  | คำนวณทางคณิตศาสตร์, random seed                    |
| `scikit-learn` | ≥1.3.0   | Ridge Regression, StandardScaler, cross-validation |
| `questionary`  | ≥2.0.0   | Interactive CLI menus                              |
| `tqdm`         | ≥4.66.0  | Progress bar                                       |
| `colorlog`     | ≥6.7.0   | Colored console logging                            |
| `sqlite3`      | built-in | Database (ไม่ต้อง install)                         |

---

## 12. ข้อจำกัดของระบบ

1. **stat-based optimization เท่านั้น** — ระบบคำนวณจาก raw stats ไม่ได้พิจารณา passive effects เชิงกลยุทธ์ (เช่น life steal, shield, active skills)
2. **ไม่พิจารณา team composition** — build ที่ดีอาจขึ้นกับ hero ฝ่ายตรงข้าม หรือ synergy กับทีม
3. **ไม่พิจารณา counter items** — ไม่มีการคำนวณว่าศัตรูเป็นสาย AP หรือ AD
4. **Pierce % ใช้ max()** — ในเกมจริงอาจมีกลไกที่ซับซ้อนกว่า
5. **damage_type ไม่ dynamic** — Hybrid heroes (เช่น Amily) ถูกจัดเป็น Physical/Magic เท่านั้น
6. **learned_weights เป็น global** — ใช้ weights ชุดเดียวกันสำหรับทุก hero/role/lane

---

> **📌 สรุป:** Project นี้เป็นระบบ AI ที่ผสานระหว่าง **Evolutionary Algorithm (GA)** กับ **Machine Learning (Ridge Regression)** เพื่อสร้างระบบแนะนำไอเทมอัตโนมัติสำหรับเกม RoV ที่มีการออกแบบโครงสร้างชัดเจน แยก Layer เป็น Data → Core Logic → Application ด้วย Repository Pattern และมีระบบทดสอบครบถ้วน

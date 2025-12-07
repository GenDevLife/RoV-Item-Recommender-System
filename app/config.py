# config.py - ค่าคงที่และการตั้งค่าสำหรับระบบแนะนำไอเทม RoV
import os

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'rov_data.db')

# ค่า cap ของ stats ในเกม (ตามกฎเกม RoV)
STATS_CAPS = {
    "cdr": 0.40,           # Cooldown Reduction สูงสุด 40%
    "aspd": 2.00,          # Attack Speed สูงสุด 200%
    "crit_rate": 1.00,     # Critical Rate สูงสุด 100%
    "move_speed": 800      # Movement Speed (soft cap)
}

# ค่าปรับลดคะแนนกรณีสร้างชุดไอเทมผิดกฎ
PENALTIES = {
    "duplicate_passive": -50.0,   # ไอเทม passive ซ้ำกัน
    "boots_limit": -100.0,        # รองเท้าเกิน 1 คู่
    "jungle_wrong": -200.0,       # ไอเทมป่าโดยไม่มี spell ป่า
    "support_limit": -100.0       # ไอเทม support เกิน
}

# ====================================
# Genetic Algorithm Profiles
# ====================================

# Medium - สมดุลระหว่างความเร็วและคุณภาพ
GA_SETTINGS_MEDIUM = {
    "POP_SIZE": 50,
    "MAX_GEN": 100,
    "MUTATION_RATE": 0.2,
    "ELITISM_COUNT": 2
}

# Fast - เร็วกว่า 3x สำหรับใช้งานทั่วไป
GA_SETTINGS_FAST = {
    "POP_SIZE": 30,
    "MAX_GEN": 50,
    "MUTATION_RATE": 0.3,
    "ELITISM_COUNT": 3
}

# Expert - คุณภาพสูงสุดสำหรับการวิเคราะห์
GA_SETTINGS_EXPERT = {
    "POP_SIZE": 80,
    "MAX_GEN": 150,
    "MUTATION_RATE": 0.15,
    "ELITISM_COUNT": 4
}

# Profile ที่ใช้เป็นค่าเริ่มต้น
GA_PROFILE = "fast"
GA_SETTINGS = GA_SETTINGS_FAST

def get_ga_settings(profile: str = None):
    """ดึงค่า settings ตาม profile ที่เลือก"""
    if profile is None:
        profile = GA_PROFILE
    
    profile = profile.lower()
    
    if profile == "fast":
        return GA_SETTINGS_FAST.copy()
    elif profile == "medium":
        return GA_SETTINGS_MEDIUM.copy()
    elif profile == "expert":
        return GA_SETTINGS_EXPERT.copy()
    else:
        raise ValueError(f"ไม่รู้จัก profile: {profile}")
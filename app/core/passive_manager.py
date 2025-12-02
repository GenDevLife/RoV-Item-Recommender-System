# app/core/passive_manager.py
from typing import List, Dict, Tuple
from app.config import PENALTIES

class PassiveManager:
    def __init__(self):
        pass

    def check_passive_conflicts(self, build_items: List[Dict]) -> Tuple[float, List[str]]:
        """
        ตรวจสอบว่ามี Unique Passive กลุ่มเดียวกันซ้ำกันหรือไม่?
        """
        seen_groups = set()
        conflicts = []
        total_penalty = 0.0
        
        for item in build_items:
            # ดึง List ของกลุ่ม Passive จากไอเทมชิ้นนั้น
            passives = item.get('passives', [])
            
            for group in passives:
                if group in seen_groups:
                    # 🚨 เจอซ้ำ!
                    item_name = item.get('name_en', 'Unknown Item')
                    msg = f"Conflict: Passive '{group}' found duplicate in '{item_name}'"
                    conflicts.append(msg)
                    
                    # บวกโทษเพิ่ม
                    total_penalty += PENALTIES["duplicate_passive"]
                else:
                    # ยังไม่เคยเจอ จดไว้
                    seen_groups.add(group)
                    
        return total_penalty, conflicts
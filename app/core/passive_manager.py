# passive_manager.py - จัดการ unique passive ของไอเทม
from typing import List, Dict, Tuple
from app.config import PENALTIES

class PassiveManager:
    """ตรวจสอบ passive ซ้ำในชุดไอเทม"""
    
    def __init__(self):
        pass

    def check_passive_conflicts(self, build_items: List[Dict]) -> Tuple[float, List[str]]:
        """ตรวจว่ามี passive กลุ่มเดียวกันซ้ำหรือไม่ ถ้าซ้ำจะโดน penalty"""
        seen_groups = set()
        conflicts = []
        total_penalty = 0.0
        
        for item in build_items:
            passives = item.get('passives', [])
            
            for group in passives:
                if group in seen_groups:
                    item_name = item.get('name_en', 'Unknown')
                    conflicts.append(f"Passive '{group}' ซ้ำใน '{item_name}'")
                    total_penalty += PENALTIES["duplicate_passive"]
                else:
                    seen_groups.add(group)
                    
        return total_penalty, conflicts
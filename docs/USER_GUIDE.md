# User Guide - RoV Item Recommender

## Quick Start

```bash
python app/main.py
```

## Modes

### All Heroes Mode

- วิเคราะห์ทุก hero พร้อมทุก role x lane combination
- ใช้ Expert mode (150 generations)
- บันทึกผลลง CSV

### Select Hero Mode

- เลือก hero, role, lane แบบ interactive
- เลือก AI mode ได้: Fast / Medium / Expert
- แสดงผลทันที

## AI Modes

| Mode   | Speed  | Generations | Use Case     |
| ------ | ------ | ----------- | ------------ |
| Fast   | ~80ms  | 50          | ทดสอบเร็วๆ   |
| Medium | ~150ms | 100         | ใช้งานทั่วไป |
| Expert | ~300ms | 150         | คุณภาพสูงสุด |

## Output Example

```
==================================================
Recommended Build for Valhein
Score: 361.46
Role: Carry
Lane: Dragon Slayer
Damage Type: Physical
==================================================
[1] Claves Sancti                   ( 2150g)
[2] War Boots                       (  660g)
[3] Slikk's Sting                   ( 2050g)
[4] The Beast                       ( 1870g)
[5] Muramasa                        ( 2020g)
[6] Fenrir's Tooth                  ( 2950g)
--------------------------------------------------
Total Cost: 11700g
Stats: AD=480, AP=0, HP=3400, CDR=0%
==================================================
```

## CSV Columns

| Column          | Description            |
| --------------- | ---------------------- |
| hero_code       | รหัสฮีโร่              |
| hero_name       | ชื่อฮีโร่              |
| role            | Role ที่ใช้            |
| lane            | Lane ที่ใช้            |
| fitness_score   | คะแนน build            |
| item_1 - item_6 | ไอเทม 6 ชิ้น           |
| total_cost      | ราคารวม                |
| final_p_atk     | Physical Attack        |
| final_m_power   | Magic Power            |
| final_hp        | HP                     |
| final_cdr       | Cooldown Reduction (%) |

## Tips

- ใช้ **Medium mode** สำหรับการใช้งานทั่วไป
- ใช้ **Expert mode** เมื่อต้องการคุณภาพสูงสุด
- **All Heroes mode** ใช้เวลาประมาณ 30-60 วินาที

## Troubleshooting

**Q: โปรแกรมช้าใน All Heroes mode?**  
A: ปกติครับ เพราะต้องคำนวณหลายร้อย combinations

**Q: Fitness score คืออะไร?**  
A: คะแนนความเหมาะสมของ build (ยิ่งสูงยิ่งดี)

**Q: Build แตกต่างจากโปร?**  
A: ระบบ optimize ตาม stats ของฮีโร่ ไม่ได้คำนึงถึง meta หรือ team composition

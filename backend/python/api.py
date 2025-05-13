# ── api.py ───────────────────────────────────────────────────────────
from flask import Flask, request, jsonify
from flask_cors import CORS
import main as ga                         # main.py อยู่โฟลเดอร์เดียวกัน

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ---------------- preload (ของเดิมคุณมีอยู่แล้ว) ----------------
ga.load_theta_config()
ga.initialize_connection_pool()
ITEM_DATA = ga.load_item_data()           # ← ตาราง items ใน MySQL

# === NEW ===  map ItemID → {name,img}
def slugify(item_name: str) -> str:
    """
    แปลง 'Flashy Boots' -> 'Flashy_Boots' เหมือนชื่อไฟล์ใน /assets/images/item
    กฎคร่าว ๆ: space/apostrophe -> '_', ตัวอักษรอื่นปล่อยไว้
    """
    import re, unicodedata
    name = unicodedata.normalize("NFKD", item_name)
    name = re.sub(r"[ '’]", "_", name)    # ช่องว่าง & อัญประกาศ
    name = re.sub(r"[^A-Za-z0-9_]", "", name)  # ตัดอักษรพิเศษอื่น
    return name

IMG_BASE = "/src/assets/images/item"      # <-- เหมือน path ที่ index.php สร้าง (ดูไฟล์ PHP)

def decorate(ids: list[str]):
    out = []
    for iid in ids:
        meta = ITEM_DATA[iid]                         # name จาก DB
        fname = f"{slugify(meta['ItemName'])}.png"    # รูปเก็บเป็น .png ทั้งหมด
        out.append({
            "id":   iid,
            "name": meta["ItemName"],
            "img":  f"{IMG_BASE}/{fname}"
        })
    return out

# --------------------------- ROUTE -----------------------------
@app.post("/ga")
def run_ga():
    payload = request.get_json(force=True)
    for k in ("hero", "lane"):
        if k not in payload:
            return jsonify({"error": f"missing field {k}"}), 400

    hero        = payload["hero"]
    lane        = payload["lane"]
    hero_class  = payload.get("heroClass")
    force_ids   = payload.get("force", []) or []
    ban_ids     = payload.get("ban", [])   or []

    result = {}
    for phase in ("Early", "Mid", "Late"):
        ids, fitness = ga.run_ga(
            hero=hero, lane=lane, hero_class=hero_class,
            force_items=force_ids, ban_items=ban_ids, phase=phase
        )
        result[phase] = {
            "fitness":  round(fitness, 4),
            "items":    decorate(ids)     # แทน id ล้วน
        }
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

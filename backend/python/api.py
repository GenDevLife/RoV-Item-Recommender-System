from flask import Flask, request, jsonify
from flask_cors import CORS
import main as ga
import re, unicodedata
from pathlib import Path
from main import load_hero_stats, ITEM_DATA

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ── preload ─────────────────────────────────────────────────────
ga.load_theta_config()
ga.initialize_connection_pool()
ITEM_DATA = ga.load_item_data()

# ── slugify item name to match your filenames ──────────────────
def slugify(item_name: str) -> str:
    # normalize
    name = unicodedata.normalize("NFKD", item_name)
    # spaces → _
    name = re.sub(r"\s+", "_", name)
    # curly apostrophe → straight
    name = name.replace("’", "'")
    # keep only A–Z, a–z, 0–9, _ and '
    name = re.sub(r"[^A-Za-z0-9_']", "", name)
    return name

# ── where to point URLs (from your frontend public folder) ───────
IMG_BASE = "./src/assets/images/item"

# ── where images live on disk ───────────────────────────────────
IMG_DIR = (
    Path(__file__).parent.parent.parent
    / "frontend" / "public"
    / "src" / "assets" / "images" / "item"
)

def decorate(ids: list[str]):
    out = []
    for iid in ids:
        meta = ITEM_DATA.get(iid)
        if not meta:
            continue

        slug = slugify(meta["ItemName"])
        fname = f"{slug}.png"
        rel_path = None

        # ตรวจทั้ง item/, farm-item/, support-item/
        for sub in ["", "farm-item", "support-item"]:
            candidate = IMG_DIR / sub / fname
            if candidate.exists():
                # ถ้า sub == "" ก็ไม่ต้องใส่ slash ซ้ำ
                rel_path = f"{IMG_BASE}/{sub}/{fname}" if sub else f"{IMG_BASE}/{fname}"
                break

        if rel_path is None:
            app.logger.warning(f"Could not find image for {fname}; defaulting to base folder")
            rel_path = f"{IMG_BASE}/{fname}"

        out.append({
            "id":   iid,
            "name": meta["ItemName"],
            "img":  rel_path
        })
    return out

# ── the GA endpoint ─────────────────────────────────────────────
@app.post("/ga")
def run_ga():
    payload = request.get_json(force=True)
    for k in ("hero", "lane"):
        if k not in payload:
            return jsonify({"error": f"missing field {k}"}), 400

    hero       = payload["hero"]
    lane       = payload["lane"]
    hero_class = payload.get("heroClass")
    force_ids  = payload.get("force") or []
    ban_ids    = payload.get("ban")   or []

    result = {}
    for phase in ("Early", "Mid", "Late"):
        ids, fitness = ga.run_ga(
            hero=hero, lane=lane, hero_class=hero_class,
            force_items=force_ids, ban_items=ban_ids, phase=phase
        )
        result[phase] = {
            "fitness": round(fitness, 4),
            "items": decorate(ids)
        }

    return jsonify(result), 200

@app.post("/calculate_stats")
def calculate_stats():
    payload = request.get_json(force=True)
    hero = payload["hero"]
    phase = payload["phase"]
    items = payload["items"]

    # คำนวณ Stat
    level = {'Early': 3, 'Mid': 9, 'Late': 15}[phase]
    hero_base_stats = load_hero_stats(hero, level)
    total_stats = {stat: float(hero_base_stats.get(stat, 0)) for stat in [
        'Phys_ATK', 'Magic_Power', 'Phys_Defense', 'HP', 'Cooldown_Reduction', 'Critical_Rate', 'Movement_Speed'
    ]}

    for item_id in items:
        item = ITEM_DATA.get(item_id, {})
        for stat in total_stats:
            total_stats[stat] += float(item.get(stat, 0))

    return jsonify({"stats": total_stats})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

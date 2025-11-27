from __future__ import annotations
import re
import unicodedata
from typing import Any

def safe_float(value: Any) -> float:
    """Convert a value to float, defaulting to 0.0 if None."""
    return float(value or 0.0)

STAT_MAPPING = [
    ('patk', 'Phys_ATK'),
    ('ap', 'Magic_Power'),
    ('def', 'Phys_Defense'),
    ('hp', 'HP'),
    ('cdr', 'Cooldown_Reduction'),
    ('crit', 'Critical_Rate'),
    ('ms', 'Movement_Speed'),
]

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

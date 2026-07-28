# evaluator.py - ประเมินคุณภาพของชุดไอเทม
from pathlib import Path
from app.config import PENALTIES, STATS_CAPS
from app.core.passive_manager import PassiveManager


class BuildEvaluator:
    """คลาสสำหรับประเมินว่าชุดไอเทมดีแค่ไหนสำหรับ hero นั้นๆ"""

    __STAT_KEYS = [
        "p_atk",
        "p_def",
        "max_hp",
        "m_power",
        "m_def",
        "cdr",
        "aspd",
        "crit_rate",
        "p_pierce_percent",
        "m_pierce_percent",
        "move_speed",
    ]

    # ponytail: hero_scaling uses base_atk/base_def/base_mdef/base_hp, items use p_atk/p_def/m_def/max_hp
    __HERO_STAT_MAP = {
        "base_atk": "p_atk",
        "base_def": "p_def",
        "base_mdef": "m_def",
        "base_hp": "max_hp",
    }

    def __init__(
        self,
        hero_data: dict,
        all_items: dict[int, dict],
    ):
        self.hero = hero_data
        self.all_items = all_items
        self.passive_manager = PassiveManager()
        self.weights = self._load_weights(hero_data.get("damage_type", "Physical"))

    def _load_weights(self, damage_type: str) -> dict:
        weights_path = (
            Path(__file__).resolve().parent.parent / "core" / "learned_weights.json"
        )
        try:
            with open(weights_path) as f:
                learned = f.read()
                import json

                learned = json.loads(learned)
            return {k: learned.get(k, 0) for k in self.__STAT_KEYS}
        except FileNotFoundError:
            if damage_type == "Magic":
                return {
                    "p_atk": 0.0,
                    "p_def": 0.01,
                    "max_hp": 0.001,
                    "m_power": 0.30,
                    "m_def": 0.01,
                    "cdr": 0.40,
                    "aspd": 0.0,
                    "crit_rate": 0.0,
                    "p_pierce_percent": 0.0,
                    "m_pierce_percent": 2.0,
                    "move_speed": 0.10,
                }
            return {
                "p_atk": 0.30,
                "p_def": 0.01,
                "max_hp": 0.001,
                "m_power": 0.0,
                "m_def": 0.01,
                "cdr": 0.20,
                "aspd": 0.50,
                "crit_rate": 0.80,
                "p_pierce_percent": 2.0,
                "m_pierce_percent": 0.0,
                "move_speed": 0.10,
            }

    def calculate_stats(self, build: list) -> dict:
        stats = dict.fromkeys(self.__STAT_KEYS, 0.0)
        for hero_key, stat_key in self.__HERO_STAT_MAP.items():
            stats[stat_key] = self.hero.get(hero_key, 0.0)
        stats["move_speed"] = (
            350.0  # ponytail: hardcoded base, no hero_scaling column for it
        )
        _pierce = {"p_pierce_percent", "m_pierce_percent"}
        for item_id in build:
            item = self.all_items.get(item_id)
            if not item:
                continue
            for stat in stats:
                val = item.get(stat, 0)
                stats[stat] = (
                    max(stats[stat], val) if stat in _pierce else stats[stat] + val
                )
        return stats

    def evaluate(self, build: list) -> tuple[float, dict, dict]:
        stats = self.calculate_stats(build)
        score = 0.0
        for stat, weight in self.weights.items():
            if stat in stats:
                try:
                    capped = min(stats[stat], STATS_CAPS.get(stat, float("inf")))
                except (KeyError, ValueError):
                    capped = stats[stat]
                value = capped * (
                    100 if stat in ("p_pierce_percent", "m_pierce_percent") else 1
                )
                score += weight * value
        items = [self.all_items[i] for i in build if i in self.all_items]
        conflicts_penalty, _ = self.passive_manager.check_passive_conflicts(items)
        score += conflicts_penalty
        boots = sum(
            1 for it in items if "limit_one_boots" in it.get("restrictions", [])
        )
        if boots > 1:
            score += PENALTIES["boots_limit"] * (boots - 1)
        return score, stats, conflicts_penalty  # type: ignore

    def get_fitness(self, build: list) -> float:
        score, _, _ = self.evaluate(build)
        return score

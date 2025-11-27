from __future__ import annotations
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

# ---------------------------- Parameter Setting -----------------------------
THETA: Dict[str, float] = {
    "stat": 12.210533136438032,
    "budget": 1.5418784650503874,
    "skill": -3.227235535145378,
    "cat": 9.251270790312363,
    "cat_ATK": 0.0,
    "cat_Def": 2.220446049250313e-16,
    "cat_Magic": -0.02990767569504543,
    "class": 6.8907772290645015,
    "lane": -5.282919354476533
}

GA_CONSTANTS: Dict[str, Any] = {
    'POP_SIZE': 600,
    'MAX_GEN': 300,
    'CROSSOVER_RATE': 0.8,
    'BASE_MUT_RATE': 0.5,
    'STAGNANT_LIMIT': 50,
    'PHASE_WEIGHTS': {'Early': 0.1, 'Mid': 0.3, 'Late': 0.6},
    'BASE_BUDGET': {'Early': 2700, 'Mid': 7500, 'Late': 14000},
}

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PRIMARY_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': 'utf8mb4',
}

def load_theta_config(path: str = 'weights.json') -> None:
    """Load and override THETA weights from an external JSON file if it exists."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            THETA.update(json.load(f))
            print(f'[INFO] Loaded THETA overrides from {path}')
    except FileNotFoundError:
        pass

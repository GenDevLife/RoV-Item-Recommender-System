# RoV Item Recommender System

An automated item build recommendation system for Garena RoV (Arena of Valor) using Genetic Algorithm optimization.

## Overview

This system analyzes hero statistics and generates optimal 6-item builds based on:

- Hero base stats and scaling
- Damage type (Physical/Magic/Hybrid)
- Role and lane combinations
- Item synergies and restrictions
- Game rule constraints (stat caps, unique passives)

## Features

### Two Operation Modes

**All Heroes Mode**

- Batch analyze every hero in the database
- Generates builds for all role × lane combinations per hero
- Uses Expert mode (150 generations) for highest quality
- Exports results to CSV file

**Select Hero Mode**

- Interactive single hero analysis
- Choose specific role and lane from hero's available options
- Select AI computation mode (Fast/Medium/Expert)
- Instant console output

### Three AI Modes

| Mode   | Population | Generations | Avg Time | Quality |
| ------ | ---------- | ----------- | -------- | ------- |
| Fast   | 30         | 50          | ~80ms    | Good    |
| Medium | 50         | 100         | ~150ms   | Better  |
| Expert | 80         | 150         | ~300ms   | Best    |

## Installation

```bash
# Clone repository
git clone https://github.com/YourUsername/RoV-Item-Recommender-System.git
cd RoV-Item-Recommender-System

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python app/main.py
```

### Menu Options

1. **All Heroes** - Analyze all heroes with all role-lane combinations
2. **Select Hero** - Choose a specific hero for analysis
3. **Exit** - Close the application

### Example Output

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
Mode: FAST
==================================================
```

## Project Structure

```
RoV-Item-Recommender-System/
├── app/
│   ├── main.py              # Main CLI application
│   ├── config.py            # Configuration and GA settings
│   ├── core/
│   │   ├── evaluator.py     # Build fitness evaluation
│   │   ├── ga_engine.py     # Genetic Algorithm engine
│   │   └── passive_manager.py
│   ├── data/
│   │   └── repository.py    # Database access layer
│   └── utils/
│       └── logger.py        # Logging configuration
├── data/
│   └── rov_data.db          # SQLite database (heroes, items, stats)
├── scripts/
│   ├── calibrate.py         # Weight calibration script
│   ├── tune_ga.py           # GA parameter tuning
│   └── setup_database.py    # Database initialization
├── docs/
│   └── USER_GUIDE.md        # Detailed user documentation
├── requirements.txt
└── README.md
```

## How It Works

### Genetic Algorithm Process

1. **Initialization**: Generate random population of item builds (6 items each)
2. **Evaluation**: Calculate fitness score for each build based on:
   - Stat bonuses weighted by hero's damage type
   - Penalty for rule violations (duplicate passives, multiple boots)
   - Stat cap enforcement (CDR 40%, Crit 100%, etc.)
3. **Selection**: Keep top performers (elitism) + tournament selection
4. **Crossover**: Combine parent builds to create offspring
5. **Mutation**: Random item replacement with probability
6. **Repeat**: Continue for specified generations
7. **Output**: Return best build found

### Fitness Calculation

The fitness function uses calibrated weights learned from training data:

```
Score = (P_ATK × w1) + (M_POWER × w2) + (HP × w3) + (CDR × w4) + ...
        - Penalties (duplicate passives, rule violations)
```

Weights are stored in `app/core/learned_weights.json` and can be recalibrated using `scripts/calibrate.py`.

## CSV Output Format

When using All Heroes mode, the output CSV contains:

| Column           | Description                  |
| ---------------- | ---------------------------- |
| hero_code        | Hero identifier (lowercase)  |
| hero_name        | Display name                 |
| role             | Selected role for this build |
| lane             | Selected lane for this build |
| damage_type      | Physical/Magic/Hybrid        |
| fitness_score    | Build quality score          |
| item_1 to item_6 | Recommended items            |
| total_cost       | Combined item cost (gold)    |
| final_p_atk      | Total Physical Attack        |
| final_m_power    | Total Magic Power            |
| final_hp         | Total HP                     |
| final_cdr        | Cooldown Reduction (%)       |
| time_ms          | Computation time             |

## Configuration

Edit `app/config.py` to modify:

- **STATS_CAPS**: Game stat limits (CDR, crit rate, etc.)
- **PENALTIES**: Score deductions for rule violations
- **GA*SETTINGS*\***: Population size, generations, mutation rate

## Scripts

| Script                | Purpose                                |
| --------------------- | -------------------------------------- |
| `calibrate.py`        | Train fitness weights from sample data |
| `tune_ga.py`          | Find optimal GA parameters             |
| `compare_profiles.py` | Benchmark Fast/Medium/Expert modes     |
| `setup_database.py`   | Initialize SQLite database             |

## Requirements

- Python 3.8+
- pandas
- tqdm
- questionary
- colorlog

## Limitations

- Builds are optimized for raw stats, not meta or team composition
- Does not consider enemy counters or situational items
- Item passive effects are simplified (only unique passive conflicts checked)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Acknowledgments

- Hero and item data from Garena RoV
- Genetic Algorithm concepts from evolutionary computation research

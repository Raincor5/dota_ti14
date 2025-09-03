"""
Configuration settings for Dota 2 Data Science Project.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# API settings
OPENDOTA_BASE_URL = "https://api.opendota.com/api"
OPENDOTA_RATE_LIMIT_DELAY = 1.0  # seconds between requests

# ELO rating system settings
ELO_BASE_K_FACTOR = 32.0
ELO_RATING_DECAY_DAYS = 365
ELO_DECAY_FACTOR = 0.95

# Tournament importance multipliers
TOURNAMENT_MULTIPLIERS = {
    'S': 1.5,      # Major tournaments (TI, Majors)
    'A': 1.2,      # Minor tournaments
    'B': 1.0,      # Regular tournaments
    'C': 0.8,      # Small tournaments
    'Qualifier': 1.1,  # Qualifier matches
    'League': 0.9,     # League matches
}

# Data collection settings
DEFAULT_DAYS_BACK = 30
DEFAULT_MAX_MATCHES = 1000
DEFAULT_BATCH_SIZE = 100

# Hero roles for analysis
HERO_ROLES = {
    'Carry': ['Anti-Mage', 'Phantom Assassin', 'Juggernaut', 'Luna', 'Spectre'],
    'Mid': ['Shadow Fiend', 'Storm Spirit', 'Queen of Pain', 'Invoker', 'Lina'],
    'Offlane': ['Axe', 'Bristleback', 'Dark Seer', 'Timbersaw', 'Underlord'],
    'Support': ['Crystal Maiden', 'Lion', 'Shadow Shaman', 'Witch Doctor', 'Dazzle'],
    'Hard Support': ['Crystal Maiden', 'Lion', 'Shadow Shaman', 'Witch Doctor', 'Dazzle']
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'high_gpm': 600,
    'high_xpm': 600,
    'high_kills': 8,
    'high_assists': 15,
    'low_deaths': 5,
    'high_last_hits': 200,
    'medium_last_hits': 100,
    'medium_gpm': 400
}

# Match analysis settings
MATCH_ANALYSIS = {
    'min_match_duration': 600,  # 10 minutes in seconds
    'max_match_duration': 7200,  # 2 hours in seconds
    'min_players_per_team': 5,
    'max_players_per_team': 5
}

# Database settings (for future use)
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'dota2_analysis'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': PROJECT_ROOT / 'logs' / 'dota2_analysis.log'
}

# Model settings
ML_MODEL_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'cv_folds': 5,
    'feature_columns': [
        'elo_difference',
        'team_a_avg_gpm',
        'team_b_avg_gpm',
        'team_a_avg_xpm',
        'team_b_avg_xpm',
        'team_a_hero_pool_size',
        'team_b_hero_pool_size',
        'team_a_recent_form',
        'team_b_recent_form'
    ]
}

# TI14 specific settings
TI14_CONFIG = {
    'tournament_name': 'The International 2024',
    'tournament_tier': 'S',
    'expected_teams': 20,
    'qualification_regions': ['NA', 'SA', 'WEU', 'EEU', 'SEA', 'CN'],
    'direct_invites': 12,
    'qualifier_slots': 8
}

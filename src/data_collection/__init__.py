"""
Data collection modules for Dota 2 analysis.
"""

# Only import modules that exist
from .opendota_client import OpenDotaClient

# These will be imported when the modules are created
try:
    from .liquipedia_scraper import LiquipediaScraper
    from .match_collector import MatchCollector
except ImportError:
    # These modules don't exist yet
    pass

__all__ = ['OpenDotaClient']

#!/usr/bin/env python3
"""
Main entry point for Dota 2 Data Science project.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to Python path for imports
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from data_collection.main import Dota2DataCollector
from features.elo_system import EloRatingSystem
from models.player import Player
from models.team import Team
from models.match import Match


def main():
    """Main function to demonstrate the project."""
    # Load environment variables from .env file
    load_dotenv()
    
    print("🎮 Dota 2 Data Science Project - TI14 Predictions")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('OPENDOTA_API_KEY')
    if not api_key:
        print("⚠️  No OpenDota API key found. Set OPENDOTA_API_KEY environment variable for better rate limits.")
        print("   You can still run with limited functionality.")
    
    print("\n📊 Initializing data collector...")
    collector = Dota2DataCollector(api_key=api_key)
    
    # Check for existing data
    if os.path.exists("data/processed/players.csv"):
        print("🔄 Loading existing data...")
        # TODO: Implement load_existing_data method
        print("   Existing data found but loading not implemented yet.")
    else:
        print("🔄 No existing data found. Starting data collection...")
        print("   This will take some time. You can interrupt with Ctrl+C.")
        
        try:
            # Collect a small amount of data for demonstration
            collector.collect_recent_pro_matches(days_back=7, max_matches=10)
            collector.save_data()
            
            print("✅ Data collection completed!")
            
        except KeyboardInterrupt:
            print("\n⏹️  Data collection interrupted by user")
        except Exception as e:
            print(f"❌ Error during data collection: {e}")
            return
    
    # Print summary
    summary = collector.get_collection_summary()
    print("\n📈 Data Collection Summary:")
    for key, value in summary.items():
        if key != 'collection_timestamp':
            print(f"   {key}: {value}")
    
    # Demonstrate ELO system
    if collector.teams:
        print("\n🏆 ELO Rating System Demo:")
        teams_list = list(collector.teams.values())
        if len(teams_list) >= 2:
            team_a = teams_list[0]
            team_b = teams_list[1]
            
            elo_system = EloRatingSystem()
            prediction = elo_system.predict_match_outcome(team_a, team_b, 'S')
            
            print(f"   Team A: {team_a.name} (ELO: {team_a.team_elo:.1f})")
            print(f"   Team B: {team_b.name} (ELO: {team_b.team_elo:.1f})")
            print(f"   Prediction: {prediction['prediction']}")
            print(f"   Team A win probability: {prediction['team_a_win_probability']:.1%}")
            print(f"   Confidence: {prediction['confidence']:.1%}")
    
    print("\n🎯 Next Steps:")
    print("1. Explore data in Jupyter notebooks")
    print("2. Build machine learning models")
    print("3. Analyze tournament trends")
    print("4. Make TI14 predictions!")
    
    print("\n🚀 Project ready! Check the notebooks/ directory for analysis examples.")


if __name__ == "__main__":
    main()

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
            # TI14 teams are already loaded in the constructor
            print("✅ TI14 teams loaded successfully!")
            
            # Skip collecting random recent matches - focus only on TI14 teams
            print("   Skipping recent match collection - focusing on TI14 teams only")
            
            print("✅ TI14 team collection completed!")
            
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
    
    # Demonstrate ELO system with TI14 teams
    if collector.teams:
        print("\n🏆 ELO Rating System Demo (TI14 Teams):")
        
        # Filter for actual TI14 teams (teams with real OpenDota IDs, not generated ones)
        ti14_teams = {team_id: team for team_id, team in collector.teams.items() 
                      if team_id < 10000000}  # Real OpenDota team IDs can be large numbers
        other_teams = {team_id: team for team_id, team in collector.teams.items() 
                      if team_id >= 10000000}  # Generated IDs for teams not found
        
        print(f"   TI14 Teams (Real OpenDota IDs): {len(ti14_teams)}")
        print(f"   Other Teams (Generated IDs): {len(other_teams)}")
        print(f"   Total Teams: {len(collector.teams)}")
        
        # Show TI14 teams
        if ti14_teams:
            print(f"\n   TI14 Teams Found:")
            for team_id, team in list(ti14_teams.items())[:8]:  # Show first 8
                print(f"   - {team.name} (ID: {team_id}, ELO: {team.team_elo:.1f})")
        
        if len(ti14_teams) >= 2:
            teams_list = list(ti14_teams.values())
            team_a = teams_list[0]
            team_b = teams_list[1]
            
            elo_system = EloRatingSystem()
            prediction = elo_system.predict_match_outcome(team_a, team_b, 'S')
            
            print(f"\n   Sample TI14 Match Prediction:")
            print(f"   {team_a.name} vs {team_b.name}")
            print(f"   Prediction: {prediction['prediction']}")
            print(f"   {team_a.name} win probability: {prediction['team_a_win_probability']:.1%}")
            print(f"   Confidence: {prediction['confidence']:.1%}")
        else:
            print("   Need at least 2 TI14 teams for ELO demo")
    
    print("\n🎯 Next Steps:")
    print("1. Explore data in Jupyter notebooks")
    print("2. Build machine learning models")
    print("3. Analyze tournament trends")
    print("4. Make TI14 predictions!")
    
    print("\n🚀 Project ready! Check the notebooks/ directory for analysis examples.")


if __name__ == "__main__":
    main()

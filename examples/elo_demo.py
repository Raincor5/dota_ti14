#!/usr/bin/env python3
"""
ELO Rating System Demo for Dota 2 Teams.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Now import the models and features
from models.team import Team
from models.player import Player
from features.elo_system import EloRatingSystem


def create_sample_teams():
    """Create sample teams for demonstration."""
    
    # Create sample players
    players = {
        'miracle': Player(player_id=1, name='Miracle-', elo_rating=2200),
        'n0tail': Player(player_id=2, name='N0tail', elo_rating=2100),
        'ana': Player(player_id=3, name='Ana', elo_rating=2150),
        'topson': Player(player_id=4, name='Topson', elo_rating=2180),
        'ceb': Player(player_id=5, name='Ceb', elo_rating=2050),
        
        'rtz': Player(player_id=6, name='Arteezy', elo_rating=2180),
        'sumail': Player(player_id=7, name='SumaiL', elo_rating=2150),
        'cr1t': Player(player_id=8, name='Cr1t-', elo_rating=2100),
        'fly': Player(player_id=9, name='Fly', elo_rating=2080),
        's4': Player(player_id=10, name='s4', elo_rating=2120)
    }
    
    # Create Team Liquid (OG-like)
    team_liquid = Team(
        team_id=1,
        name='Team Liquid',
        tag='TL',
        country='International',
        region='WEU'
    )
    
    # Add players to team
    for player in [players['miracle'], players['n0tail'], players['ana'], 
                   players['topson'], players['ceb']]:
        team_liquid.add_player(player, role='Core')
    
    # Calculate team ELO as average of players
    team_liquid.team_elo = sum(p.elo_rating for p in [players['miracle'], players['n0tail'], players['ana'], 
                                                      players['topson'], players['ceb']]) / 5
    
    # Create Evil Geniuses
    team_eg = Team(
        team_id=2,
        name='Evil Geniuses',
        tag='EG',
        country='USA',
        region='NA'
    )
    
    # Add players to team
    for player in [players['rtz'], players['sumail'], players['cr1t'], 
                   players['fly'], players['s4']]:
        team_eg.add_player(player, role='Core')
    
    # Calculate team ELO as average of players
    team_eg.team_elo = sum(p.elo_rating for p in [players['rtz'], players['sumail'], players['cr1t'], 
                                                  players['fly'], players['s4']]) / 5
    
    return team_liquid, team_eg


def demonstrate_elo_system():
    """Demonstrate the ELO rating system."""
    
    print("🏆 Dota 2 ELO Rating System Demo")
    print("=" * 40)
    
    # Create sample teams
    team_liquid, team_eg = create_sample_teams()
    
    print(f"\n📊 Team Information:")
    print(f"Team Liquid: {team_liquid.name} (ELO: {team_liquid.team_elo:.1f})")
    print(f"Evil Geniuses: {team_eg.name} (ELO: {team_eg.team_elo:.1f})")
    
    # Initialize ELO system
    elo_system = EloRatingSystem()
    
    # Predict match outcome
    print(f"\n🔮 Match Prediction:")
    prediction = elo_system.predict_match_outcome(team_liquid, team_eg, 'S')
    
    print(f"Prediction: {prediction['prediction']}")
    print(f"Team Liquid win probability: {prediction['team_a_win_probability']:.1%}")
    print(f"Evil Geniuses win probability: {prediction['team_b_win_probability']:.1%}")
    print(f"Confidence: {prediction['confidence']:.1%}")
    
    # Simulate a match
    print(f"\n🎮 Simulating Match Results:")
    
    # Simulate Team Liquid winning
    print(f"\nScenario 1: Team Liquid wins")
    old_elo_liquid = team_liquid.team_elo
    old_elo_eg = team_eg.team_elo
    
    # Update ratings
    new_elo_liquid = elo_system.update_team_rating(
        team_liquid, team_eg.team_elo, 1.0, 
        match_date=None, match_importance='S'
    )
    new_elo_eg = elo_system.update_team_rating(
        team_eg, team_liquid.team_elo, 0.0, 
        match_date=None, match_importance='S'
    )
    
    print(f"Team Liquid ELO: {old_elo_liquid:.1f} → {new_elo_liquid:.1f} (Δ: {new_elo_liquid - old_elo_liquid:+.1f})")
    print(f"Evil Geniuses ELO: {old_elo_eg:.1f} → {new_elo_eg:.1f} (Δ: {new_elo_eg - old_elo_eg:+.1f})")
    
    # Reset ratings for next simulation
    team_liquid.team_elo = old_elo_liquid
    team_eg.team_elo = old_elo_eg
    
    # Simulate Evil Geniuses winning
    print(f"\nScenario 2: Evil Geniuses wins")
    new_elo_liquid = elo_system.update_team_rating(
        team_liquid, team_eg.team_elo, 0.0, 
        match_date=None, match_importance='S'
    )
    new_elo_eg = elo_system.update_team_rating(
        team_eg, team_liquid.team_elo, 1.0, 
        match_date=None, match_importance='S'
    )
    
    print(f"Team Liquid ELO: {old_elo_liquid:.1f} → {new_elo_liquid:.1f} (Δ: {new_elo_liquid - old_elo_liquid:+.1f})")
    print(f"Evil Geniuses ELO: {old_elo_eg:.1f} → {new_elo_eg:.1f} (Δ: {new_elo_eg - old_elo_eg:+.1f})")
    
    # Show rating confidence
    print(f"\n📈 Rating Confidence:")
    liquid_confidence = elo_system.get_team_rating_confidence(team_liquid)
    eg_confidence = elo_system.get_team_rating_confidence(team_eg)
    
    print(f"Team Liquid confidence: {liquid_confidence:.1%}")
    print(f"Evil Geniuses confidence: {eg_confidence:.1%}")
    
    print(f"\n🎯 This demonstrates how the ELO system:")
    print(f"   - Rewards wins and penalizes losses")
    print(f"   - Considers match importance (tournament tier)")
    print(f"   - Provides confidence levels for predictions")
    print(f"   - Can be used for match outcome predictions")


if __name__ == "__main__":
    demonstrate_elo_system()

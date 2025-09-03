#!/usr/bin/env python3
"""
Simple ELO Rating System Demo for Dota 2 Teams.
This version doesn't require numpy to avoid dependency issues.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Simple math functions to replace numpy
def mean(values):
    """Calculate mean of a list of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)

def std(values):
    """Calculate standard deviation of a list of values."""
    if not values:
        return 0.0
    avg = mean(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return variance ** 0.5

def min_val(values):
    """Get minimum value from a list."""
    if not values:
        return 0.0
    return min(values)

def max_val(values):
    """Get maximum value from a list."""
    if not values:
        return 0.0
    return max(values)


class SimplePlayer:
    """Simple player class for demo purposes."""
    
    def __init__(self, player_id: int, name: str, elo_rating: float = 1200.0):
        self.player_id = player_id
        self.name = name
        self.elo_rating = elo_rating
        self.total_matches = 0
        self.wins = 0
        self.losses = 0
        self.elo_history = []
    
    @property
    def win_rate(self):
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100
    
    def update_elo(self, new_rating: float, match_date=None):
        elo_change = new_rating - self.elo_rating
        self.elo_rating = new_rating
        self.elo_history.append((match_date, elo_change))


class SimpleTeam:
    """Simple team class for demo purposes."""
    
    def __init__(self, team_id: int, name: str, tag: str, country: str = None, region: str = None):
        self.team_id = team_id
        self.name = name
        self.tag = tag
        self.country = country
        self.region = region
        self.team_elo = 1200.0
        self.total_matches = 0
        self.wins = 0
        self.losses = 0
        self.elo_history = []
        self.players = {}
    
    @property
    def win_rate(self):
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100
    
    def add_player(self, player, role: str = "Unknown"):
        self.players[player.player_id] = player
        player.team_id = self.team_id
    
    def update_team_elo(self, new_rating: float, match_date=None):
        elo_change = new_rating - self.team_elo
        self.team_elo = new_rating
        self.elo_history.append((match_date, elo_change))


class SimpleEloSystem:
    """Simple ELO rating system for demo purposes."""
    
    def __init__(self, base_k_factor: float = 32.0):
        self.base_k_factor = base_k_factor
        
        # Tournament importance multipliers
        self.tournament_multipliers = {
            'S': 1.5,      # Major tournaments
            'A': 1.2,      # Minor tournaments
            'B': 1.0,      # Regular tournaments
            'C': 0.8,      # Small tournaments
        }
    
    def calculate_expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for team A against team B."""
        return 1.0 / (1.0 + (10 ** ((rating_b - rating_a) / 400.0)))
    
    def calculate_k_factor(self, team: SimpleTeam, match_importance: str = 'B') -> float:
        """Calculate K-factor for team."""
        # Base K-factor adjustment based on team rating
        if team.team_elo < 1200:
            rating_factor = 1.3  # New teams get higher K-factor
        elif team.team_elo < 2000:
            rating_factor = 1.1  # Intermediate teams
        elif team.team_elo < 2400:
            rating_factor = 1.0  # Standard teams
        else:
            rating_factor = 0.8  # Elite teams get lower K-factor
        
        # Tournament importance multiplier
        tournament_mult = self.tournament_multipliers.get(match_importance, 1.0)
        
        # Team experience factor
        experience_factor = max(0.6, 1.0 - (team.total_matches / 500))
        
        return self.base_k_factor * rating_factor * tournament_mult * experience_factor
    
    def update_team_rating(self, team: SimpleTeam, opponent_rating: float,
                          actual_score: float, match_date=None,
                          match_importance: str = 'B') -> float:
        """Update team ELO rating after a match."""
        # Calculate expected score
        expected_score = self.calculate_expected_score(team.team_elo, opponent_rating)
        
        # Calculate K-factor
        k_factor = self.calculate_k_factor(team, match_importance)
        
        # Calculate new rating
        rating_change = k_factor * (actual_score - expected_score)
        new_rating = team.team_elo + rating_change
        
        # Update team rating
        team.update_team_elo(new_rating, match_date)
        
        return new_rating
    
    def get_team_rating_confidence(self, team: SimpleTeam) -> float:
        """Calculate confidence in team's current rating."""
        if team.total_matches < 20:
            return 0.3
        elif team.total_matches < 100:
            return 0.6
        elif team.total_matches < 500:
            return 0.8
        else:
            return 1.0
    
    def predict_match_outcome(self, team_a: SimpleTeam, team_b: SimpleTeam,
                            match_importance: str = 'B') -> dict:
        """Predict match outcome based on ELO ratings."""
        # Calculate expected scores
        team_a_expected = self.calculate_expected_score(team_a.team_elo, team_b.team_elo)
        team_b_expected = self.calculate_expected_score(team_b.team_elo, team_a.team_elo)
        
        # Calculate confidence levels
        confidence_a = self.get_team_rating_confidence(team_a)
        confidence_b = self.get_team_rating_confidence(team_b)
        
        # Overall confidence
        overall_confidence = (confidence_a + confidence_b) / 2
        
        # Rating difference
        rating_diff = team_a.team_elo - team_b.team_elo
        
        # Prediction
        if team_a_expected > 0.6:
            prediction = 'Team A Strong Favorite'
        elif team_a_expected > 0.55:
            prediction = 'Team A Slight Favorite'
        elif team_a_expected > 0.45:
            prediction = 'Even Match'
        elif team_a_expected > 0.4:
            prediction = 'Team B Slight Favorite'
        else:
            prediction = 'Team B Strong Favorite'
        
        return {
            'team_a_win_probability': team_a_expected,
            'team_b_win_probability': team_b_expected,
            'prediction': prediction,
            'rating_difference': rating_diff,
            'confidence': overall_confidence,
            'team_a_confidence': confidence_a,
            'team_b_confidence': confidence_b
        }


def create_sample_teams():
    """Create sample teams for demonstration."""
    
    # Create sample players
    players = {
        'miracle': SimplePlayer(player_id=1, name='Miracle-', elo_rating=2200),
        'n0tail': SimplePlayer(player_id=2, name='N0tail', elo_rating=2100),
        'ana': SimplePlayer(player_id=3, name='Ana', elo_rating=2150),
        'topson': SimplePlayer(player_id=4, name='Topson', elo_rating=2180),
        'ceb': SimplePlayer(player_id=5, name='Ceb', elo_rating=2050),
        
        'rtz': SimplePlayer(player_id=6, name='Arteezy', elo_rating=2180),
        'sumail': SimplePlayer(player_id=7, name='SumaiL', elo_rating=2150),
        'cr1t': SimplePlayer(player_id=8, name='Cr1t-', elo_rating=2100),
        'fly': SimplePlayer(player_id=9, name='Fly', elo_rating=2080),
        's4': SimplePlayer(player_id=10, name='s4', elo_rating=2120)
    }
    
    # Create Team Liquid (OG-like)
    team_liquid = SimpleTeam(
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
    team_eg = SimpleTeam(
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
    team_eg.team_elo = sum(p.elo_rating for p in players.values() if p.team_id == 2) / 5
    
    return team_liquid, team_eg


def demonstrate_elo_system():
    """Demonstrate the ELO rating system."""
    
    print("🏆 Dota 2 ELO Rating System Demo (Simple Version)")
    print("=" * 50)
    
    # Create sample teams
    team_liquid, team_eg = create_sample_teams()
    
    print(f"\n📊 Team Information:")
    print(f"Team Liquid: {team_liquid.name} (ELO: {team_liquid.team_elo:.1f})")
    print(f"Evil Geniuses: {team_eg.name} (ELO: {team_eg.team_elo:.1f})")
    
    # Initialize ELO system
    elo_system = SimpleEloSystem()
    
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
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Install numpy: pip install numpy")
    print(f"   2. Run the full demo: python examples/elo_demo.py")
    print(f"   3. Start collecting real data: python src/main.py")


if __name__ == "__main__":
    demonstrate_elo_system()

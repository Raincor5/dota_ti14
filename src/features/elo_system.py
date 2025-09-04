"""
ELO Rating System for Dota 2 players and teams.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Import numpy if available, otherwise use simple math functions
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    
    # Simple math functions to replace numpy
    def mean(values):
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    def median(values):
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def std(values):
        if not values:
            return 0.0
        avg = mean(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def min_val(values):
        if not values:
            return 0.0
        return min(values)
    
    def max_val(values):
        if not values:
            return 0.0
        return max(values)

# Import models - use absolute imports that work from project root
from models.player import Player
from models.team import Team
from models.match import Match


class EloRatingSystem:
    """
    Advanced ELO rating system for Dota 2 with K-factor adjustment,
    rating decay, and tournament importance weighting.
    """
    
    def __init__(self, base_k_factor: float = 32.0, 
                 rating_decay_days: int = 365,
                 decay_factor: float = 0.95):
        """
        Initialize ELO rating system.
        
        Args:
            base_k_factor: Base K-factor for rating calculations
            rating_decay_days: Days after which ratings start decaying
            decay_factor: Factor by which ratings decay (0.95 = 5% decay)
        """
        self.base_k_factor = base_k_factor
        self.rating_decay_days = rating_decay_days
        self.decay_factor = decay_factor
        
        # Tournament importance multipliers
        self.tournament_multipliers = {
            'S': 1.5,      # Major tournaments
            'A': 1.2,      # Minor tournaments
            'B': 1.0,      # Regular tournaments
            'C': 0.8,      # Small tournaments
            'Qualifier': 1.1,  # Qualifier matches
            'League': 0.9,     # League matches
        }
    
    def calculate_expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for player/team A against player/team B.
        
        Args:
            rating_a: Rating of player/team A
            rating_b: Rating of player/team B
            
        Returns:
            Expected score (0.0 to 1.0) for player/team A
        """
        return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / 400.0))
    
    def calculate_k_factor(self, player: Player, match_importance: str = 'B') -> float:
        """
        Calculate dynamic K-factor based on player rating and match importance.
        
        Args:
            player: Player object
            match_importance: Tournament tier or match importance
            
        Returns:
            Adjusted K-factor
        """
        # Base K-factor adjustment based on rating
        if player.elo_rating < 1200:
            rating_factor = 1.5  # New players get higher K-factor
        elif player.elo_rating < 2000:
            rating_factor = 1.2  # Intermediate players
        elif player.elo_rating < 2400:
            rating_factor = 1.0  # Standard players
        else:
            rating_factor = 0.8  # Elite players get lower K-factor
        
        # Tournament importance multiplier
        tournament_mult = self.tournament_multipliers.get(match_importance, 1.0)
        
        # Player experience factor (more matches = lower K-factor)
        experience_factor = max(0.5, 1.0 - (player.total_matches / 1000))
        
        return self.base_k_factor * rating_factor * tournament_mult * experience_factor
    
    def calculate_team_k_factor(self, team: Team, match_importance: str = 'B') -> float:
        """
        Calculate dynamic K-factor for teams.
        
        Args:
            team: Team object
            match_importance: Tournament tier or match importance
            
        Returns:
            Adjusted K-factor
        """
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
        
        # TI14-specific adjustments
        if match_importance == 'S':  # TI14 matches
            tournament_mult *= 1.3  # Higher volatility for TI14
        elif match_importance == 'A':  # TI14 qualifiers
            tournament_mult *= 1.1
        
        # Roster stability factor (simplified - in practice you'd track actual roster changes)
        roster_factor = self._calculate_roster_stability_factor(team)
        
        return self.base_k_factor * rating_factor * tournament_mult * experience_factor * roster_factor
    
    def _calculate_roster_stability_factor(self, team: Team) -> float:
        """
        Calculate roster stability factor for TI14 teams.
        Accounts for stand-ins, roster changes, etc.
        
        Args:
            team: Team object
            
        Returns:
            Roster stability factor (0.5 to 1.5)
        """
        # This is a simplified version - in practice you'd track actual roster changes
        # For now, we'll use team age and recent performance as proxies
        
        if not hasattr(team, 'elo_history') or len(team.elo_history) < 5:
            return 1.0  # Default for new teams
        
        # Calculate recent performance volatility
        recent_matches = team.elo_history[-10:]  # Last 10 matches
        if len(recent_matches) < 3:
            return 1.0
        
        # Calculate standard deviation of recent ELO changes
        changes = [change for _, change in recent_matches]
        if len(changes) < 2:
            return 1.0
        
        # Simple variance calculation
        mean_change = sum(changes) / len(changes)
        variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)
        std_dev = variance ** 0.5
        
        # High volatility suggests roster instability
        if std_dev > 50:  # High volatility
            return 0.7  # Reduce K-factor for unstable rosters
        elif std_dev > 30:  # Medium volatility
            return 0.85
        elif std_dev < 15:  # Low volatility
            return 1.2  # Increase K-factor for stable rosters
        else:
            return 1.0
    
    def detect_stand_in_impact(self, team: Team, match: Match) -> float:
        """
        Detect potential stand-in impact on team performance.
        
        Args:
            team: Team object
            match: Match object
            
        Returns:
            Stand-in impact factor (0.8 to 1.2)
        """
        # This is a simplified approach - in practice you'd track actual roster changes
        # For now, we'll use performance consistency as a proxy
        
        if not hasattr(team, 'elo_history') or len(team.elo_history) < 10:
            return 1.0  # Default for new teams
        
        # Calculate performance consistency over last 20 matches
        recent_matches = team.elo_history[-20:]
        if len(recent_matches) < 10:
            return 1.0
        
        # Calculate win rate consistency
        # This is a simplified approach - in practice you'd analyze actual player rosters
        
        # For now, return neutral factor
        # In a real implementation, you'd:
        # 1. Track player rosters for each match
        # 2. Detect when key players are missing
        # 3. Adjust ELO calculations accordingly
        
        return 1.0
    
    def update_player_rating(self, player: Player, opponent_rating: float, 
                           actual_score: float, match_date: datetime,
                           match_importance: str = 'B') -> float:
        """
        Update player ELO rating after a match.
        
        Args:
            player: Player to update
            opponent_rating: Rating of the opponent
            actual_score: Actual score (1.0 for win, 0.0 for loss, 0.5 for draw)
            match_date: Date of the match
            match_importance: Tournament tier or match importance
            
        Returns:
            New ELO rating
        """
        # Apply rating decay if player hasn't played recently
        self._apply_rating_decay(player, match_date)
        
        # Calculate expected score
        expected_score = self.calculate_expected_score(player.elo_rating, opponent_rating)
        
        # Calculate K-factor
        k_factor = self.calculate_k_factor(player, match_importance)
        
        # Calculate new rating
        rating_change = k_factor * (actual_score - expected_score)
        new_rating = player.elo_rating + rating_change
        
        # Update player rating
        player.update_elo(new_rating, match_date)
        
        return new_rating
    
    def update_team_rating(self, team: Team, opponent_rating: float,
                          actual_score: float, match_date: datetime,
                          match_importance: str = 'B') -> float:
        """
        Update team ELO rating after a match.
        
        Args:
            team: Team to update
            opponent_rating: Rating of the opponent
            actual_score: Actual score (1.0 for win, 0.0 for loss, 0.5 for draw)
            match_date: Date of the match
            match_importance: Tournament tier or match importance
            
        Returns:
            New ELO rating
        """
        # Apply rating decay if team hasn't played recently
        self._apply_team_rating_decay(team, match_date)
        
        # Calculate expected score
        expected_score = self.calculate_expected_score(team.team_elo, opponent_rating)
        
        # Calculate K-factor
        k_factor = self.calculate_team_k_factor(team, match_importance)
        
        # Calculate new rating
        rating_change = k_factor * (actual_score - expected_score)
        new_rating = team.team_elo + rating_change
        
        # Update team rating
        team.update_team_elo(new_rating, match_date)
        
        return new_rating
    
    def _apply_rating_decay(self, player: Player, current_date: datetime):
        """Apply rating decay for inactive players."""
        if not player.elo_history or current_date is None:
            return
        
        last_match_date = player.elo_history[-1][0]
        if last_match_date is None:
            return
            
        days_since_last_match = (current_date - last_match_date).days
        
        if days_since_last_match > self.rating_decay_days:
            decay_periods = (days_since_last_match - self.rating_decay_days) // 30  # Monthly decay
            decay_factor = math.pow(self.decay_factor, decay_periods)
            
            # Apply decay to current rating
            decayed_rating = 1200 + (player.elo_rating - 1200) * decay_factor
            player.elo_rating = decayed_rating
    
    def _apply_team_rating_decay(self, team: Team, current_date: datetime):
        """Apply rating decay for inactive teams."""
        if not team.elo_history or current_date is None:
            return
        
        last_match_date = team.elo_history[-1][0]
        if last_match_date is None:
            return
            
        days_since_last_match = (current_date - last_match_date).days
        
        if days_since_last_match > self.rating_decay_days:
            decay_periods = (days_since_last_match - self.rating_decay_days) // 30
            decay_factor = math.pow(self.decay_factor, decay_periods)
            
            # Apply decay to current rating
            decayed_rating = 1200 + (team.team_elo - 1200) * decay_factor
            team.team_elo = decayed_rating
    
    def calculate_match_rating_change(self, match: Match, 
                                    radiant_team: Team, dire_team: Team,
                                    match_importance: str = 'B') -> Tuple[float, float]:
        """
        Calculate rating changes for both teams in a match.
        
        Args:
            match: Match object
            radiant_team: Radiant team
            dire_team: Dire team
            match_importance: Tournament tier or match importance
            
        Returns:
            Tuple of (radiant_rating_change, dire_rating_change)
        """
        if match.radiant_win is None:
            return 0.0, 0.0
        
        # Determine actual scores
        if match.radiant_win:
            radiant_score = 1.0
            dire_score = 0.0
        else:
            radiant_score = 0.0
            dire_score = 1.0
        
        # Calculate expected scores
        radiant_expected = self.calculate_expected_score(radiant_team.team_elo, dire_team.team_elo)
        dire_expected = self.calculate_expected_score(dire_team.team_elo, radiant_team.team_elo)
        
        # Calculate K-factors
        radiant_k = self.calculate_team_k_factor(radiant_team, match_importance)
        dire_k = self.calculate_team_k_factor(dire_team, match_importance)
        
        # Calculate rating changes
        radiant_change = radiant_k * (radiant_score - radiant_expected)
        dire_change = dire_k * (dire_score - dire_expected)
        
        return radiant_change, dire_change
    
    def get_rating_confidence(self, player: Player) -> float:
        """
        Calculate confidence in player's current rating based on match history.
        
        Args:
            player: Player object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if player.total_matches < 10:
            return 0.3  # Low confidence for new players
        elif player.total_matches < 50:
            return 0.6  # Medium confidence
        elif player.total_matches < 200:
            return 0.8  # High confidence
        else:
            return 1.0  # Very high confidence
    
    def get_team_rating_confidence(self, team: Team) -> float:
        """
        Calculate confidence in team's current rating.
        
        Args:
            team: Team object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if team.total_matches < 20:
            return 0.3
        elif team.total_matches < 100:
            return 0.6
        elif team.total_matches < 500:
            return 0.8
        else:
            return 1.0
    
    def predict_match_outcome(self, team_a: Team, team_b: Team,
                            match_importance: str = 'B') -> Dict:
        """
        Predict match outcome based on ELO ratings.
        
        Args:
            team_a: First team
            team_b: Second team
            match_importance: Tournament tier or match importance
            
        Returns:
            Dictionary with prediction details
        """
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
    
    def get_rating_distribution_stats(self, players: List[Player]) -> Dict:
        """
        Calculate rating distribution statistics for a group of players.
        
        Args:
            players: List of players
            
        Returns:
            Dictionary with distribution statistics
        """
        if not players:
            return {}
        
        ratings = [p.elo_rating for p in players]
        
        if HAS_NUMPY:
            return {
                'total_players': len(players),
                'mean_rating': np.mean(ratings),
                'median_rating': np.median(ratings),
                'std_rating': np.std(ratings),
                'min_rating': np.min(ratings),
                'max_rating': np.max(ratings),
                'rating_ranges': {
                    'Bronze (<1200)': len([r for r in ratings if r < 1200]),
                    'Silver (1200-1400)': len([r for r in ratings if 1200 <= r < 1400]),
                    'Gold (1400-1600)': len([r for r in ratings if 1400 <= r < 1600]),
                    'Platinum (1600-1800)': len([r for r in ratings if 1600 <= r < 1800]),
                    'Diamond (1800-2000)': len([r for r in ratings if 1800 <= r < 2000]),
                    'Master (2000-2200)': len([r for r in ratings if 2000 <= r < 2200]),
                    'Grandmaster (2200+)': len([r for r in ratings if r >= 2200])
                }
            }
        else:
            return {
                'total_players': len(players),
                'mean_rating': mean(ratings),
                'median_rating': median(ratings),
                'std_rating': std(ratings),
                'min_rating': min_val(ratings),
                'max_rating': max_val(ratings),
                'rating_ranges': {
                    'Bronze (<1200)': len([r for r in ratings if r < 1200]),
                    'Silver (1200-1400)': len([r for r in ratings if 1200 <= r < 1400]),
                    'Gold (1400-1600)': len([r for r in ratings if 1400 <= r < 1600]),
                    'Platinum (1600-1800)': len([r for r in ratings if 1600 <= r < 1800]),
                    'Diamond (1800-2000)': len([r for r in ratings if 1800 <= r < 2000]),
                    'Master (2000-2200)': len([r for r in ratings if 2000 <= r < 2200]),
                    'Grandmaster (2200+)': len([r for r in ratings if r >= 2200])
                }
            }

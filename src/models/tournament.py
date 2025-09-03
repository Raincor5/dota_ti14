"""
Tournament model for Dota 2 analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from .team import Team
from .match import Match


@dataclass
class Tournament:
    """
    Represents a Dota 2 tournament with comprehensive statistics and standings.
    """
    
    # Basic tournament information
    tournament_id: int
    name: str
    tier: str  # S, A, B, C, etc.
    region: Optional[str] = None
    prize_pool: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Tournament structure
    tournament_type: str = "Single Elimination"  # Single/Double Elimination, Round Robin, Swiss
    total_teams: int = 0
    total_matches: int = 0
    
    # Participating teams and results
    teams: Dict[int, Team] = field(default_factory=dict)
    matches: List[Match] = field(default_factory=list)
    standings: List[Tuple[int, int, int, int, float]] = field(default_factory=list)  # team_id, wins, losses, draws, points
    
    # Tournament meta
    patch_version: Optional[str] = None
    meta_analysis: Dict = field(default_factory=dict)
    
    # Historical significance
    dpc_points: int = 0
    international_qualifier: bool = False
    major_tournament: bool = False
    
    def add_team(self, team: Team):
        """Add a team to the tournament."""
        self.teams[team.team_id] = team
        self.total_teams = len(self.teams)
    
    def add_match(self, match: Match):
        """Add a match to the tournament."""
        self.matches.append(match)
        self.total_matches = len(self.matches)
        
        # Update team statistics
        self._update_team_stats_from_match(match)
    
    def _update_team_stats_from_match(self, match: Match):
        """Update team statistics based on match result."""
        if match.radiant_win is None:
            return
        
        # Update team match counts
        if match.radiant_team_id in self.teams:
            self.teams[match.radiant_team_id].add_match_result(
                won=match.radiant_win,
                match_duration=match.match_duration or 0,
                team_kills=match.radiant_score[0] if match.radiant_score else 0,
                team_deaths=match.radiant_score[1] if match.radiant_score else 0,
                team_gold=match.radiant_gold or 0,
                heroes_used=match.radiant_picks
            )
        
        if match.dire_team_id in self.teams:
            self.teams[match.dire_team_id].add_match_result(
                won=not match.radiant_win,
                match_duration=match.match_duration or 0,
                team_kills=match.dire_score[0] if match.dire_score else 0,
                team_deaths=match.dire_score[1] if match.dire_score else 0,
                team_gold=match.dire_gold or 0,
                heroes_used=match.dire_picks
            )
    
    def calculate_standings(self) -> List[Tuple[int, int, int, int, float]]:
        """Calculate tournament standings based on match results."""
        team_stats = {}
        
        # Initialize team statistics
        for team_id in self.teams:
            team_stats[team_id] = {'wins': 0, 'losses': 0, 'draws': 0, 'points': 0}
        
        # Calculate from matches
        for match in self.matches:
            if match.radiant_win is None:
                continue
            
            if match.radiant_win:
                team_stats[match.radiant_team_id]['wins'] += 1
                team_stats[match.dire_team_id]['losses'] += 1
                team_stats[match.radiant_team_id]['points'] += 3
            else:
                team_stats[match.dire_team_id]['wins'] += 1
                team_stats[match.radiant_team_id]['losses'] += 1
                team_stats[match.dire_team_id]['points'] += 3
        
        # Convert to standings list and sort by points
        standings = [(team_id, stats['wins'], stats['losses'], stats['draws'], stats['points']) 
                    for team_id, stats in team_stats.items()]
        standings.sort(key=lambda x: x[4], reverse=True)
        
        self.standings = standings
        return standings
    
    def get_team_performance(self, team_id: int) -> Optional[Dict]:
        """Get comprehensive performance data for a specific team in this tournament."""
        if team_id not in self.teams:
            return None
        
        team = self.teams[team_id]
        team_matches = [m for m in self.matches 
                       if m.radiant_team_id == team_id or m.dire_team_id == team_id]
        
        if not team_matches:
            return None
        
        wins = 0
        losses = 0
        total_kills = 0
        total_deaths = 0
        total_gold = 0
        total_xp = 0
        heroes_used = set()
        
        for match in team_matches:
            is_radiant = match.radiant_team_id == team_id
            won = match.radiant_win if is_radiant else not match.radiant_win
            
            if won:
                wins += 1
            else:
                losses += 1
            
            # Get team performance from match
            team_perf = match.get_team_performance(team_id)
            if team_perf:
                total_kills += team_perf.get('total_kills', 0)
                total_deaths += team_perf.get('total_deaths', 0)
                total_gold += team_perf.get('gold', 0) or 0
                total_xp += team_perf.get('xp', 0) or 0
                heroes_used.update(team_perf.get('picks', []))
        
        return {
            'team_id': team_id,
            'team_name': team.name,
            'matches_played': len(team_matches),
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / len(team_matches)) * 100 if team_matches else 0,
            'avg_kills_per_game': total_kills / len(team_matches) if team_matches else 0,
            'avg_deaths_per_game': total_deaths / len(team_matches) if team_matches else 0,
            'avg_gold_per_game': total_gold / len(team_matches) if team_matches else 0,
            'avg_xp_per_game': total_xp / len(team_matches) if team_matches else 0,
            'hero_pool_size': len(heroes_used),
            'current_standing': self._get_team_standing(team_id)
        }
    
    def _get_team_standing(self, team_id: int) -> Optional[int]:
        """Get current standing position for a team."""
        for i, (tid, _, _, _, _) in enumerate(self.standings):
            if tid == team_id:
                return i + 1
        return None
    
    def analyze_tournament_meta(self) -> Dict:
        """Analyze tournament meta and trends."""
        if not self.matches:
            return {}
        
        # Hero statistics
        hero_picks = {}
        hero_bans = {}
        hero_wins = {}
        
        # Team composition analysis
        composition_types = []
        match_durations = []
        total_kills = []
        
        for match in self.matches:
            if match.radiant_win is None:
                continue
            
            # Hero statistics
            for hero_id in match.radiant_picks + match.dire_picks:
                hero_picks[hero_id] = hero_picks.get(hero_id, 0) + 1
                if match.radiant_win:
                    hero_wins[hero_id] = hero_wins.get(hero_id, 0) + 1
            
            for hero_id in match.radiant_bans + match.dire_bans:
                hero_bans[hero_id] = hero_bans.get(hero_id, 0) + 1
            
            # Match analysis
            if match.match_duration:
                match_durations.append(match.match_duration)
            
            total_kills.append(match.total_kills)
            
            # Composition analysis
            meta = match.get_match_meta_analysis()
            if 'radiant_composition' in meta:
                composition_types.append(meta['radiant_composition']['composition_type'])
            if 'dire_composition' in meta:
                composition_types.append(meta['dire_composition']['composition_type'])
        
        # Calculate meta insights
        meta_analysis = {
            'total_matches': len(self.matches),
            'avg_match_duration': np.mean(match_durations) if match_durations else 0,
            'avg_kills_per_game': np.mean(total_kills) if total_kills else 0,
            'most_picked_heroes': sorted(hero_picks.items(), key=lambda x: x[1], reverse=True)[:10],
            'most_banned_heroes': sorted(hero_bans.items(), key=lambda x: x[1], reverse=True)[:10],
            'hero_win_rates': {hero: (wins / hero_picks[hero]) * 100 
                              for hero, wins in hero_wins.items() if hero in hero_picks},
            'composition_distribution': {comp: composition_types.count(comp) 
                                       for comp in set(composition_types)},
            'patch_version': self.patch_version
        }
        
        self.meta_analysis = meta_analysis
        return meta_analysis
    
    def get_tournament_summary(self) -> Dict:
        """Get comprehensive tournament summary."""
        standings = self.calculate_standings()
        meta = self.analyze_tournament_meta()
        
        return {
            'tournament_id': self.tournament_id,
            'name': self.name,
            'tier': self.tier,
            'region': self.region,
            'prize_pool': self.prize_pool,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_teams': self.total_teams,
            'total_matches': self.total_matches,
            'standings': standings,
            'meta_analysis': meta,
            'dpc_points': self.dpc_points,
            'international_qualifier': self.international_qualifier,
            'major_tournament': self.major_tournament
        }
    
    def to_dict(self) -> Dict:
        """Convert tournament to dictionary for storage/API."""
        return {
            'tournament_id': self.tournament_id,
            'name': self.name,
            'tier': self.tier,
            'region': self.region,
            'prize_pool': self.prize_pool,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'tournament_type': self.tournament_type,
            'total_teams': self.total_teams,
            'total_matches': self.total_matches,
            'patch_version': self.patch_version,
            'dpc_points': self.dpc_points,
            'international_qualifier': self.international_qualifier,
            'major_tournament': self.major_tournament
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Tournament':
        """Create tournament from dictionary."""
        tournament = cls(
            tournament_id=data['tournament_id'],
            name=data['name'],
            tier=data['tier'],
            region=data.get('region'),
            prize_pool=data.get('prize_pool'),
            tournament_type=data.get('tournament_type', 'Single Elimination'),
            total_teams=data.get('total_teams', 0),
            total_matches=data.get('total_matches', 0),
            patch_version=data.get('patch_version'),
            dpc_points=data.get('dpc_points', 0),
            international_qualifier=data.get('international_qualifier', False),
            major_tournament=data.get('major_tournament', False)
        )
        
        # Parse dates
        if data.get('start_date'):
            tournament.start_date = datetime.fromisoformat(data['start_date'])
        if data.get('end_date'):
            tournament.end_date = datetime.fromisoformat(data['end_date'])
        
        return tournament

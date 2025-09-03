"""
Match model for Dota 2 analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from .player import Player
from .team import Team


@dataclass
class Match:
    """
    Represents a Dota 2 match with comprehensive statistics and analysis.
    """
    
    # Basic match information
    match_id: int
    radiant_team_id: int
    dire_team_id: int
    match_date: datetime
    tournament_id: Optional[int] = None
    tournament_name: Optional[str] = None
    
    # Match outcome
    radiant_win: Optional[bool] = None
    match_duration: Optional[float] = None  # in seconds
    
    # Team statistics
    radiant_score: Optional[Tuple[int, int]] = None  # (kills, deaths)
    dire_score: Optional[Tuple[int, int]] = None
    
    # Player performance
    radiant_players: Dict[int, Dict] = field(default_factory=dict)  # player_id -> stats
    dire_players: Dict[int, Dict] = field(default_factory=dict)
    
    # Hero picks and bans
    radiant_picks: List[int] = field(default_factory=list)  # hero_ids
    dire_picks: List[int] = field(default_factory=list)
    radiant_bans: List[int] = field(default_factory=list)
    dire_bans: List[int] = field(default_factory=list)
    
    # Match phases and objectives
    first_blood_time: Optional[float] = None
    radiant_tower_kills: int = 0
    dire_tower_kills: int = 0
    radiant_barracks_kills: int = 0
    dire_barracks_kills: int = 0
    radiant_roshan_kills: int = 0
    dire_roshan_kills: int = 0
    
    # Economic data
    radiant_gold: Optional[float] = None
    dire_gold: Optional[float] = None
    radiant_xp: Optional[float] = None
    dire_xp: Optional[float] = None
    
    # Meta analysis
    patch_version: Optional[str] = None
    game_mode: str = "All Pick"
    lobby_type: str = "Tournament"
    
    def __post_init__(self):
        """Initialize computed properties."""
        self._calculate_match_stats()
    
    def _calculate_match_stats(self):
        """Calculate derived match statistics."""
        if self.radiant_win is not None and self.match_duration is not None:
            self._update_team_stats()
    
    def _update_team_stats(self):
        """Update team statistics based on match result."""
        # This would be called when updating match results
        pass
    
    @property
    def winner_team_id(self) -> Optional[int]:
        """Get the winning team ID."""
        if self.radiant_win is None:
            return None
        return self.radiant_team_id if self.radiant_win else self.dire_team_id
    
    @property
    def loser_team_id(self) -> Optional[int]:
        """Get the losing team ID."""
        if self.radiant_win is None:
            return None
        return self.dire_team_id if self.radiant_win else self.radiant_team_id
    
    @property
    def total_kills(self) -> int:
        """Calculate total kills in the match."""
        if self.radiant_score and self.dire_score:
            return self.radiant_score[0] + self.dire_score[0]
        return 0
    
    @property
    def total_deaths(self) -> int:
        """Calculate total deaths in the match."""
        if self.radiant_score and self.dire_score:
            return self.radiant_score[1] + self.dire_score[1]
        return 0
    
    @property
    def match_efficiency(self) -> float:
        """Calculate match efficiency (objectives vs time)."""
        if not self.match_duration:
            return 0.0
        
        total_objectives = (self.radiant_tower_kills + self.dire_tower_kills + 
                           self.radiant_barracks_kills + self.dire_barracks_kills +
                           self.radiant_roshan_kills + self.dire_roshan_kills)
        
        # Normalize by match duration (in minutes)
        duration_minutes = self.match_duration / 60
        return total_objectives / max(duration_minutes, 1)
    
    def add_player_performance(self, player_id: int, team_side: str, 
                              hero_id: int, role: str, kda: Tuple[int, int, int],
                              gpm: float, xpm: float, net_worth: float,
                              tower_damage: float, hero_damage: float,
                              hero_healing: float, last_hits: int, denies: int):
        """Add player performance data to the match."""
        player_stats = {
            'hero_id': hero_id,
            'role': role,
            'kills': kda[0],
            'deaths': kda[1],
            'assists': kda[2],
            'gpm': gpm,
            'xpm': xpm,
            'net_worth': net_worth,
            'tower_damage': tower_damage,
            'hero_damage': hero_damage,
            'hero_healing': hero_healing,
            'last_hits': last_hits,
            'denies': denies
        }
        
        if team_side.lower() == 'radiant':
            self.radiant_players[player_id] = player_stats
        else:
            self.dire_players[player_id] = player_stats
    
    def get_team_performance(self, team_id: int) -> Optional[Dict]:
        """Get comprehensive performance data for a specific team."""
        if team_id == self.radiant_team_id:
            players = self.radiant_players
            score = self.radiant_score
            gold = self.radiant_gold
            xp = self.radiant_xp
            picks = self.radiant_picks
            bans = self.radiant_bans
        elif team_id == self.dire_team_id:
            players = self.dire_players
            score = self.dire_score
            gold = self.dire_gold
            xp = self.dire_xp
            picks = self.radiant_picks
            bans = self.radiant_bans
        else:
            return None
        
        if not players:
            return None
        
        # Aggregate player statistics
        total_kills = sum(p['kills'] for p in players.values())
        total_deaths = sum(p['deaths'] for p in players.values())
        total_assists = sum(p['assists'] for p in players.values())
        total_gpm = np.mean([p['gpm'] for p in players.values()])
        total_xpm = np.mean([p['xpm'] for p in players.values()])
        total_net_worth = sum(p['net_worth'] for p in players.values())
        total_tower_damage = sum(p['tower_damage'] for p in players.values())
        total_hero_damage = sum(p['hero_damage'] for p in players.values())
        
        return {
            'team_id': team_id,
            'score': score,
            'gold': gold,
            'xp': xp,
            'picks': picks,
            'bans': bans,
            'total_kills': total_kills,
            'total_deaths': total_deaths,
            'total_assists': total_assists,
            'avg_gpm': total_gpm,
            'avg_xpm': total_xpm,
            'total_net_worth': total_net_worth,
            'total_tower_damage': total_tower_damage,
            'total_hero_damage': total_hero_damage,
            'player_count': len(players)
        }
    
    def get_match_meta_analysis(self) -> Dict:
        """Analyze match meta and strategy patterns."""
        meta_analysis = {
            'hero_diversity': len(set(self.radiant_picks + self.dire_picks)),
            'ban_diversity': len(set(self.radiant_bans + self.dire_bans)),
            'pick_ban_ratio': len(set(self.radiant_picks + self.dire_picks)) / 
                             max(len(set(self.radiant_bans + self.dire_bans)), 1),
            'match_pace': self.total_kills / max(self.match_duration / 60, 1) if self.match_duration else 0,
            'objective_focus': self.match_efficiency,
            'team_fight_frequency': self.total_kills / max(len(self.radiant_players) + len(self.dire_players), 1)
        }
        
        # Analyze hero roles and composition
        if self.radiant_players and self.dire_players:
            radiant_roles = [p['role'] for p in self.radiant_players.values()]
            dire_roles = [p['role'] for p in self.dire_players.values()]
            
            meta_analysis['radiant_composition'] = self._analyze_team_composition(radiant_roles)
            meta_analysis['dire_composition'] = self._analyze_team_composition(dire_roles)
        
        return meta_analysis
    
    def _analyze_team_composition(self, roles: List[str]) -> Dict:
        """Analyze team composition based on roles."""
        role_counts = {}
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Determine composition type
        if role_counts.get('Carry', 0) >= 2:
            composition_type = 'Multi-Carry'
        elif role_counts.get('Support', 0) >= 3:
            composition_type = 'Support-Heavy'
        elif role_counts.get('Mid', 0) >= 2:
            composition_type = 'Mid-Focused'
        else:
            composition_type = 'Balanced'
        
        return {
            'composition_type': composition_type,
            'role_distribution': role_counts,
            'flexibility_score': len(set(roles)) / len(roles) if roles else 0
        }
    
    def to_dict(self) -> Dict:
        """Convert match to dictionary for storage/API."""
        return {
            'match_id': self.match_id,
            'radiant_team_id': self.radiant_team_id,
            'dire_team_id': self.dire_team_id,
            'match_date': self.match_date.isoformat(),
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament_name,
            'radiant_win': self.radiant_win,
            'match_duration': self.match_duration,
            'radiant_score': self.radiant_score,
            'dire_score': self.dire_score,
            'radiant_picks': self.radiant_picks,
            'dire_picks': self.dire_picks,
            'radiant_bans': self.radiant_bans,
            'dire_bans': self.dire_bans,
            'first_blood_time': self.first_blood_time,
            'radiant_tower_kills': self.radiant_tower_kills,
            'dire_tower_kills': self.dire_tower_kills,
            'radiant_barracks_kills': self.radiant_barracks_kills,
            'dire_barracks_kills': self.dire_barracks_kills,
            'radiant_roshan_kills': self.radiant_roshan_kills,
            'dire_roshan_kills': self.dire_roshan_kills,
            'radiant_gold': self.radiant_gold,
            'dire_gold': self.dire_gold,
            'radiant_xp': self.radiant_xp,
            'dire_xp': self.dire_xp,
            'patch_version': self.patch_version,
            'game_mode': self.game_mode,
            'lobby_type': self.lobby_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Match':
        """Create match from dictionary."""
        match = cls(
            match_id=data['match_id'],
            radiant_team_id=data['radiant_team_id'],
            dire_team_id=data['dire_team_id'],
            match_date=datetime.fromisoformat(data['match_date']),
            tournament_id=data.get('tournament_id'),
            tournament_name=data.get('tournament_name'),
            radiant_win=data.get('radiant_win'),
            match_duration=data.get('match_duration'),
            radiant_score=data.get('radiant_score'),
            dire_score=data.get('dire_score'),
            radiant_picks=data.get('radiant_picks', []),
            dire_picks=data.get('dire_picks', []),
            radiant_bans=data.get('radiant_bans', []),
            dire_bans=data.get('dire_bans', []),
            first_blood_time=data.get('first_blood_time'),
            radiant_tower_kills=data.get('radiant_tower_kills', 0),
            dire_tower_kills=data.get('dire_tower_kills', 0),
            radiant_barracks_kills=data.get('radiant_barracks_kills', 0),
            dire_barracks_kills=data.get('dire_barracks_kills', 0),
            radiant_roshan_kills=data.get('radiant_roshan_kills', 0),
            dire_roshan_kills=data.get('dire_roshan_kills', 0),
            radiant_gold=data.get('radiant_gold'),
            dire_gold=data.get('dire_gold'),
            radiant_xp=data.get('radiant_xp'),
            dire_xp=data.get('dire_xp'),
            patch_version=data.get('patch_version'),
            game_mode=data.get('game_mode', 'All Pick'),
            lobby_type=data.get('lobby_type', 'Tournament')
        )
        
        # Add player data if available
        if 'radiant_players' in data:
            match.radiant_players = data['radiant_players']
        if 'dire_players' in data:
            match.dire_players = data['dire_players']
        
        return match

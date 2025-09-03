"""
Player model for Dota 2 analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class Player:
    """
    Represents a Dota 2 player with comprehensive statistics and ratings.
    """
    
    # Basic information
    player_id: int
    name: str
    real_name: Optional[str] = None
    country: Optional[str] = None
    team_id: Optional[int] = None
    
    # ELO rating system
    elo_rating: float = 1200.0
    elo_history: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Performance metrics
    total_matches: int = 0
    wins: int = 0
    losses: int = 0
    
    # Role-specific stats
    roles: Dict[str, int] = field(default_factory=dict)  # role -> matches played
    hero_stats: Dict[int, Dict] = field(default_factory=dict)  # hero_id -> stats
    
    # Advanced metrics
    kda_ratio: float = 0.0
    gpm_average: float = 0.0
    xpm_average: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100
    
    @property
    def current_form(self) -> float:
        """Calculate current form based on recent ELO changes."""
        if len(self.elo_history) < 2:
            return 0.0
        
        recent_changes = [change for _, change in self.elo_history[-10:]]
        return np.mean(recent_changes) if recent_changes else 0.0
    
    def update_elo(self, new_rating: float, match_date: datetime = None):
        """Update ELO rating and track history."""
        if match_date is None:
            match_date = datetime.now()
        
        elo_change = new_rating - self.elo_rating
        self.elo_rating = new_rating
        self.elo_history.append((match_date, elo_change))
        
        # Keep only last 100 ELO changes
        if len(self.elo_history) > 100:
            self.elo_history = self.elo_history[-100:]
    
    def add_match_result(self, won: bool, role: str, hero_id: int, 
                        kda: Tuple[int, int, int], gpm: float, xpm: float):
        """Add match result and update statistics."""
        self.total_matches += 1
        if won:
            self.wins += 1
        else:
            self.losses += 1
        
        # Update role statistics
        self.roles[role] = self.roles.get(role, 0) + 1
        
        # Update hero statistics
        if hero_id not in self.hero_stats:
            self.hero_stats[hero_id] = {
                'matches': 0, 'wins': 0, 'kda': [], 'gpm': [], 'xpm': []
            }
        
        hero_stats = self.hero_stats[hero_id]
        hero_stats['matches'] += 1
        if won:
            hero_stats['wins'] += 1
        
        hero_stats['kda'].append(kda)
        hero_stats['gpm'].append(gpm)
        hero_stats['xpm'].append(xpm)
        
        # Update averages
        self._update_averages()
    
    def _update_averages(self):
        """Update overall performance averages."""
        all_kda = []
        all_gpm = []
        all_xpm = []
        
        for hero_stats in self.hero_stats.values():
            all_kda.extend(hero_stats['kda'])
            all_gpm.extend(hero_stats['gpm'])
            all_xpm.extend(hero_stats['xpm'])
        
        if all_kda:
            total_kills = sum(k for k, _, _ in all_kda)
            total_deaths = sum(d for _, d, _ in all_kda)
            total_assists = sum(a for _, _, a in all_kda)
            
            self.kda_ratio = (total_kills + total_assists) / max(total_deaths, 1)
            self.gpm_average = np.mean(all_gpm)
            self.xpm_average = np.mean(all_xpm)
    
    def get_hero_performance(self, hero_id: int) -> Optional[Dict]:
        """Get performance statistics for a specific hero."""
        if hero_id not in self.hero_stats:
            return None
        
        stats = self.hero_stats[hero_id]
        return {
            'matches': stats['matches'],
            'win_rate': (stats['wins'] / stats['matches']) * 100 if stats['matches'] > 0 else 0,
            'avg_kda': np.mean([(k + a) / max(d, 1) for k, d, a in stats['kda']]) if stats['kda'] else 0,
            'avg_gpm': np.mean(stats['gpm']) if stats['gpm'] else 0,
            'avg_xpm': np.mean(stats['xpm']) if stats['xpm'] else 0
        }
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for storage/API."""
        return {
            'player_id': self.player_id,
            'name': self.name,
            'real_name': self.real_name,
            'country': self.country,
            'team_id': self.team_id,
            'elo_rating': self.elo_rating,
            'total_matches': self.total_matches,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': self.win_rate,
            'kda_ratio': self.kda_ratio,
            'gpm_average': self.gpm_average,
            'xpm_average': self.xpm_average,
            'roles': self.roles,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Create player from dictionary."""
        player = cls(
            player_id=data['player_id'],
            name=data['name'],
            real_name=data.get('real_name'),
            country=data.get('country'),
            team_id=data.get('team_id'),
            elo_rating=data.get('elo_rating', 1200.0),
            total_matches=data.get('total_matches', 0),
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            kda_ratio=data.get('kda_ratio', 0.0),
            gpm_average=data.get('gpm_average', 0.0),
            xpm_average=data.get('xpm_average', 0.0),
            roles=data.get('roles', {}),
            hero_stats=data.get('hero_stats', {})
        )
        
        # Parse last_updated
        if 'last_updated' in data:
            player.last_updated = datetime.fromisoformat(data['last_updated'])
        
        return player

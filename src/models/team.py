"""
Team model for Dota 2 analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from .player import Player


@dataclass
class Team:
    """
    Represents a Dota 2 team with comprehensive statistics and player management.
    """
    
    # Basic information
    team_id: int
    name: str
    tag: str
    country: Optional[str] = None
    region: Optional[str] = None
    founded_date: Optional[datetime] = None
    
    # Team ELO rating
    team_elo: float = 1200.0
    elo_history: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Performance metrics
    total_matches: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    
    # Tournament performance
    tournaments_attended: int = 0
    tournament_wins: int = 0
    prize_money: float = 0.0
    
    # Current roster
    players: Dict[int, Player] = field(default_factory=dict)
    active_players: List[int] = field(default_factory=list)  # player_ids
    
    # Team composition stats
    roles: Dict[str, int] = field(default_factory=dict)  # role -> player_count
    hero_pool: Dict[int, int] = field(default_factory=dict)  # hero_id -> matches_played
    
    # Advanced metrics
    avg_match_duration: float = 0.0
    avg_kills_per_game: float = 0.0
    avg_deaths_per_game: float = 0.0
    avg_gold_per_game: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def win_rate(self) -> float:
        """Calculate team win rate percentage."""
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
    
    @property
    def average_player_elo(self) -> float:
        """Calculate average ELO rating of active players."""
        if not self.active_players:
            return 0.0
        
        active_elos = [self.players[pid].elo_rating for pid in self.active_players 
                      if pid in self.players]
        return np.mean(active_elos) if active_elos else 0.0
    
    def add_player(self, player: Player, role: str = "Unknown"):
        """Add a player to the team."""
        self.players[player.player_id] = player
        if player.player_id not in self.active_players:
            self.active_players.append(player.player_id)
        
        # Update role statistics
        self.roles[role] = self.roles.get(role, 0) + 1
        
        # Update player's team_id
        player.team_id = self.team_id
    
    def remove_player(self, player_id: int):
        """Remove a player from the team."""
        if player_id in self.players:
            self.players[player_id].team_id = None
            del self.players[player_id]
        
        if player_id in self.active_players:
            self.active_players.remove(player_id)
    
    def update_team_elo(self, new_rating: float, match_date: datetime = None):
        """Update team ELO rating and track history."""
        if match_date is None:
            match_date = datetime.now()
        
        elo_change = new_rating - self.team_elo
        self.team_elo = new_rating
        self.elo_history.append((match_date, elo_change))
        
        # Keep only last 100 ELO changes
        if len(self.elo_history) > 100:
            self.elo_history = self.elo_history[-100:]
    
    def add_match_result(self, won: bool, match_duration: float, 
                        team_kills: int, team_deaths: int, team_gold: float,
                        heroes_used: List[int]):
        """Add match result and update team statistics."""
        self.total_matches += 1
        if won:
            self.wins += 1
        else:
            self.losses += 1
        
        # Update match statistics
        self.avg_match_duration = ((self.avg_match_duration * (self.total_matches - 1) + 
                                   match_duration) / self.total_matches)
        
        self.avg_kills_per_game = ((self.avg_kills_per_game * (self.total_matches - 1) + 
                                   team_kills) / self.total_matches)
        
        self.avg_deaths_per_game = ((self.avg_deaths_per_game * (self.total_matches - 1) + 
                                    team_deaths) / self.total_matches)
        
        self.avg_gold_per_game = ((self.avg_gold_per_game * (self.total_matches - 1) + 
                                  team_gold) / self.total_matches)
        
        # Update hero pool
        for hero_id in heroes_used:
            self.hero_pool[hero_id] = self.hero_pool.get(hero_id, 0) + 1
    
    def get_team_composition(self) -> Dict[str, List[Player]]:
        """Get current team composition by roles."""
        composition = {}
        for player_id in self.active_players:
            if player_id in self.players:
                player = self.players[player_id]
                # Get primary role (most played)
                primary_role = max(player.roles.items(), key=lambda x: x[1])[0] if player.roles else "Unknown"
                
                if primary_role not in composition:
                    composition[primary_role] = []
                composition[primary_role].append(player)
        
        return composition
    
    def get_team_strengths(self) -> Dict[str, float]:
        """Analyze team strengths in different areas."""
        strengths = {}
        
        # Aggressive play style
        if self.avg_kills_per_game > 25:
            strengths['aggressive'] = 0.8
        elif self.avg_kills_per_game > 20:
            strengths['aggressive'] = 0.6
        else:
            strengths['aggressive'] = 0.4
        
        # Defensive play style
        if self.avg_deaths_per_game < 20:
            strengths['defensive'] = 0.8
        elif self.avg_deaths_per_game < 25:
            strengths['defensive'] = 0.6
        else:
            strengths['defensive'] = 0.4
        
        # Economic efficiency
        if self.avg_gold_per_game > 2000:
            strengths['economic'] = 0.8
        elif self.avg_gold_per_game > 1800:
            strengths['economic'] = 0.6
        else:
            strengths['economic'] = 0.4
        
        # Hero pool diversity
        hero_diversity = len(self.hero_pool) / max(self.total_matches, 1)
        strengths['flexibility'] = min(hero_diversity * 10, 1.0)
        
        # Team coordination (based on ELO consistency)
        if len(self.active_players) >= 5:
            player_elos = [self.players[pid].elo_rating for pid in self.active_players 
                          if pid in self.players]
            elo_std = np.std(player_elos)
            strengths['coordination'] = max(1.0 - (elo_std / 200), 0.0)
        else:
            strengths['coordination'] = 0.5
        
        return strengths
    
    def to_dict(self) -> Dict:
        """Convert team to dictionary for storage/API."""
        return {
            'team_id': self.team_id,
            'name': self.name,
            'tag': self.tag,
            'country': self.country,
            'region': self.region,
            'team_elo': self.team_elo,
            'total_matches': self.total_matches,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'win_rate': self.win_rate,
            'tournaments_attended': self.tournaments_attended,
            'tournament_wins': self.tournament_wins,
            'prize_money': self.prize_money,
            'avg_match_duration': self.avg_match_duration,
            'avg_kills_per_game': self.avg_kills_per_game,
            'avg_deaths_per_game': self.avg_deaths_per_game,
            'avg_gold_per_game': self.avg_gold_per_game,
            'active_players': self.active_players,
            'roles': self.roles,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Team':
        """Create team from dictionary."""
        team = cls(
            team_id=data['team_id'],
            name=data['name'],
            tag=data['tag'],
            country=data.get('country'),
            region=data.get('region'),
            team_elo=data.get('team_elo', 1200.0),
            total_matches=data.get('total_matches', 0),
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            draws=data.get('draws', 0),
            tournaments_attended=data.get('tournaments_attended', 0),
            tournament_wins=data.get('tournament_wins', 0),
            prize_money=data.get('prize_money', 0.0),
            avg_match_duration=data.get('avg_match_duration', 0.0),
            avg_kills_per_game=data.get('avg_kills_per_game', 0.0),
            avg_deaths_per_game=data.get('avg_deaths_per_game', 0.0),
            avg_gold_per_game=data.get('avg_gold_per_game', 0.0),
            active_players=data.get('active_players', []),
            roles=data.get('roles', {}),
            hero_pool=data.get('hero_pool', {})
        )
        
        # Parse founded_date if exists
        if 'founded_date' in data and data['founded_date']:
            team.founded_date = datetime.fromisoformat(data['founded_date'])
        
        # Parse last_updated
        if 'last_updated' in data:
            team.last_updated = datetime.fromisoformat(data['last_updated'])
        
        return team

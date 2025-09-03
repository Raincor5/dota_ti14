"""
Main data collection script for Dota 2 analysis.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv

from models.player import Player
from models.team import Team
from models.match import Match
from models.tournament import Tournament
from features.elo_system import EloRatingSystem
from .opendota_client import OpenDotaClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Dota2DataCollector:
    """
    Main data collector for Dota 2 analysis project.
    """
    
    def __init__(self, data_dir: str = "data", api_key: Optional[str] = None):
        """
        Initialize data collector.
        
        Args:
            data_dir: Directory to store collected data
            api_key: Optional OpenDota API key
        """
        self.data_dir = data_dir
        self.api_key = api_key
        self.client = OpenDotaClient(api_key=api_key)
        self.elo_system = EloRatingSystem()
        
        # Create data directories
        os.makedirs(f"{data_dir}/raw", exist_ok=True)
        os.makedirs(f"{data_dir}/processed", exist_ok=True)
        os.makedirs(f"{data_dir}/models", exist_ok=True)
        
        # Data storage
        self.players: Dict[int, Player] = {}
        self.teams: Dict[int, Team] = {}
        self.matches: List[Match] = []
        self.tournaments: Dict[int, Tournament] = {}
    
    def collect_recent_pro_matches(self, days_back: int = 30, max_matches: int = 1000):
        """
        Collect recent professional matches.
        
        Args:
            days_back: Number of days to look back
            max_matches: Maximum number of matches to collect
        """
        logger.info(f"Collecting pro matches from the last {days_back} days...")
        
        matches_collected = 0
        matches_processed = 0
        matches_skipped = 0
        offset = 0
        limit = 100  # OpenDota API limit per request
        
        while matches_collected < max_matches:
            matches = self.client.get_pro_matches(limit=limit, offset=offset)
            
            if not matches:
                logger.info("No more matches to collect")
                break
            
            logger.info(f"Retrieved {len(matches)} matches from API (offset: {offset})")
            
            for match_data in matches:
                if matches_collected >= max_matches:
                    break
                
                # Check if match is recent enough
                match_time = datetime.fromtimestamp(match_data.get('start_time', 0))
                if match_time < datetime.now() - timedelta(days=days_back):
                    logger.info("Reached older matches, stopping collection")
                    break
                
                # Process match
                initial_matches = len(self.matches)
                self._process_pro_match(match_data)
                
                if len(self.matches) > initial_matches:
                    matches_processed += 1
                    logger.info(f"Successfully processed match {match_data.get('match_id')}")
                else:
                    matches_skipped += 1
                    logger.info(f"Skipped match {match_data.get('match_id')} (missing data)")
                
                matches_collected += 1
            
            offset += limit
            logger.info(f"Progress: {matches_collected} matches retrieved, {matches_processed} processed, {matches_skipped} skipped")
        
        logger.info(f"Collection complete: {matches_collected} retrieved, {matches_processed} processed, {matches_skipped} skipped")
    
    def _process_pro_match(self, match_data: Dict):
        """Process a professional match from OpenDota API."""
        try:
            # Extract basic match information
            match_id = match_data.get('match_id')
            radiant_team_id = match_data.get('radiant_team_id')
            dire_team_id = match_data.get('dire_team_id')
            radiant_win = match_data.get('radiant_win')
            start_time = datetime.fromtimestamp(match_data.get('start_time', 0))
            duration = match_data.get('duration')
            league_id = match_data.get('leagueid')
            league_name = match_data.get('league_name')
            
            # Skip matches without team information
            if not radiant_team_id or not dire_team_id:
                logger.info(f"Skipping match {match_id}: Missing team information")
                return
            
            # Create or update teams
            self._ensure_team_exists(radiant_team_id, match_data.get('radiant_name', 'Unknown'))
            self._ensure_team_exists(dire_team_id, match_data.get('dire_name', 'Unknown'))
            
            # Create match object
            match = Match(
                match_id=match_id,
                radiant_team_id=radiant_team_id,
                dire_team_id=dire_team_id,
                match_date=start_time,
                tournament_id=league_id,
                tournament_name=league_name,
                radiant_win=radiant_win,
                match_duration=duration
            )
            
            # Get detailed match information
            self._enrich_match_data(match)
            
            # Store match
            self.matches.append(match)
            
            # Update ELO ratings if match has result
            if radiant_win is not None:
                self._update_elo_ratings(match)
            
        except Exception as e:
            logger.error(f"Error processing match {match_data.get('match_id')}: {e}")
            logger.error(f"Match data: {match_data}")
    
    def _ensure_team_exists(self, team_id: int, team_name: str):
        """Ensure a team exists in our data, create if necessary."""
        if team_id not in self.teams:
            # Try to get team info from API
            team_info = self.client.get_team_info(team_id)
            
            if team_info and isinstance(team_info, dict):
                # API returned valid team info
                team = Team(
                    team_id=team_id,
                    name=team_info.get('name', team_name),
                    tag=team_info.get('tag', team_name[:3].upper()),
                    country=team_info.get('country'),
                    region=team_info.get('region')
                )
                logger.info(f"Created team from API: {team.name} (ID: {team_id})")
            else:
                # API failed or returned invalid data, create basic team info
                team = Team(
                    team_id=team_id,
                    name=team_name,
                    tag=team_name[:3].upper()
                )
                logger.info(f"Created basic team: {team.name} (ID: {team_id}) - API info unavailable")
            
            self.teams[team_id] = team
    
    def _enrich_match_data(self, match: Match):
        """Enrich match data with detailed information from OpenDota API."""
        try:
            match_details = self.client.get_match_details(match.match_id)
            
            if not match_details:
                logger.warning(f"Could not get match details for match {match.match_id}")
                return
            
            # Extract player performance data
            players = match_details.get('players', [])
            
            for player_data in players:
                player_id = player_data.get('account_id')
                if not player_id or player_id == 4294967295:  # Anonymous player
                    continue
                
                # Ensure player exists
                if player_id not in self.players:
                    player = Player(
                        player_id=player_id,
                        name=player_data.get('personaname', 'Unknown')
                    )
                    self.players[player_id] = player
                
                # Determine team side
                is_radiant = player_data.get('player_slot', 0) < 128
                team_side = 'radiant' if is_radiant else 'dire'
                
                # Extract performance metrics
                hero_id = player_data.get('hero_id', 0)
                kills = player_data.get('kills', 0)
                deaths = player_data.get('deaths', 0)
                assists = player_data.get('assists', 0)
                gpm = player_data.get('gold_per_min', 0)
                xpm = player_data.get('xp_per_min', 0)
                net_worth = player_data.get('net_worth', 0)
                tower_damage = player_data.get('tower_damage', 0)
                hero_damage = player_data.get('hero_damage', 0)
                hero_healing = player_data.get('hero_healing', 0)
                last_hits = player_data.get('last_hits', 0)
                denies = player_data.get('denies', 0)
                
                # Determine role (simplified)
                role = self._determine_player_role(player_data)
                
                # Add player performance to match
                match.add_player_performance(
                    player_id=player_id,
                    team_side=team_side,
                    hero_id=hero_id,
                    role=role,
                    kda=(kills, deaths, assists),
                    gpm=gpm,
                    xpm=xpm,
                    net_worth=net_worth,
                    tower_damage=tower_damage,
                    hero_damage=hero_damage,
                    hero_healing=hero_healing,
                    last_hits=last_hits,
                    denies=denies
                )
            
            # Extract team-level data
            if 'radiant_score' in match_details and isinstance(match_details['radiant_score'], dict):
                match.radiant_score = (
                    match_details['radiant_score'].get('kills', 0),
                    match_details['radiant_score'].get('deaths', 0)
                )
            
            if 'dire_score' in match_details and isinstance(match_details['dire_score'], dict):
                match.dire_score = (
                    match_details['dire_score'].get('kills', 0),
                    match_details['dire_score'].get('deaths', 0)
                )
            
            # Extract picks and bans
            picks_bans = match_details.get('picks_bans', [])
            for pick_ban in picks_bans:
                hero_id = pick_ban.get('hero_id', 0)
                is_pick = pick_ban.get('is_pick', True)
                team = pick_ban.get('team', 0)
                
                if is_pick:
                    if team == 0:  # Radiant
                        match.radiant_picks.append(hero_id)
                    else:  # Dire
                        match.dire_picks.append(hero_id)
                else:
                    if team == 0:  # Radiant
                        match.radiant_bans.append(hero_id)
                    else:  # Dire
                        match.dire_bans.append(hero_id)
            
            # Extract other match data
            match.first_blood_time = match_details.get('first_blood_time')
            match.radiant_tower_kills = match_details.get('tower_status_radiant', 0)
            match.dire_tower_kills = match_details.get('tower_status_dire', 0)
            match.patch_version = match_details.get('patch', 'Unknown')
            
            logger.info(f"Successfully enriched match {match.match_id} with {len(players)} players")
            
        except Exception as e:
            logger.error(f"Error enriching match {match.match_id}: {e}")
            logger.error(f"Match details: {match_details if 'match_details' in locals() else 'Not retrieved'}")
    
    def _determine_player_role(self, player_data: Dict) -> str:
        """Determine player role based on performance data."""
        # This is a simplified role determination
        # In practice, you'd want more sophisticated logic
        
        kills = player_data.get('kills', 0)
        deaths = player_data.get('deaths', 0)
        assists = player_data.get('assists', 0)
        gpm = player_data.get('gold_per_min', 0)
        xpm = player_data.get('xp_per_min', 0)
        last_hits = player_data.get('last_hits', 0)
        denies = player_data.get('denies', 0)
        
        # Simple role determination logic
        if gpm > 600 and last_hits > 200:
            return 'Carry'
        elif xpm > 600 and kills > 8:
            return 'Mid'
        elif assists > 15 and deaths < 5:
            return 'Support'
        elif last_hits > 100 and gpm > 400:
            return 'Offlane'
        else:
            return 'Support'  # Default to support
    
    def _update_elo_ratings(self, match: Match):
        """Update ELO ratings for both teams after a match."""
        try:
            radiant_team = self.teams.get(match.radiant_team_id)
            dire_team = self.teams.get(match.dire_team_id)
            
            if not radiant_team or not dire_team:
                logger.warning(f"Cannot update ELO for match {match.match_id}: Teams not found")
                return
            
            # Determine match importance based on tournament
            match_importance = 'B'  # Default
            if match.tournament_id:
                # You could implement logic to determine tournament tier
                match_importance = 'A'  # Assume pro matches are important
            
            # Calculate rating changes
            radiant_change, dire_change = self.elo_system.calculate_match_rating_change(
                match, radiant_team, dire_team, match_importance
            )
            
            # Update team ratings
            radiant_team.team_elo += radiant_change
            dire_team.team_elo += dire_change
            
            # Update team ELO history
            radiant_team.elo_history.append((match.match_date, radiant_change))
            dire_team.elo_history.append((match.match_date, dire_change))
            
            logger.info(f"Updated ELO ratings for match {match.match_id}: Radiant +{radiant_change:.1f}, Dire +{dire_change:.1f}")
            
        except Exception as e:
            logger.error(f"Error updating ELO ratings for match {match.match_id}: {e}")
    
    def save_data(self):
        """Save collected data to files."""
        logger.info("Saving collected data...")
        
        # Save raw data
        raw_data = {
            'players': [p.to_dict() for p in self.players.values()],
            'teams': [t.to_dict() for t in self.teams.values()],
            'matches': [m.to_dict() for m in self.matches],
            'collection_timestamp': datetime.now().isoformat()
        }
        
        with open(f"{self.data_dir}/raw/collected_data.json", 'w') as f:
            json.dump(raw_data, f, indent=2, default=str)
        
        # Save processed data as CSV
        if self.players:
            players_df = pd.DataFrame([p.to_dict() for p in self.players.values()])
            players_df.to_csv(f"{self.data_dir}/processed/players.csv", index=False)
        
        if self.teams:
            teams_df = pd.DataFrame([t.to_dict() for t in self.teams.values()])
            teams_df.to_csv(f"{self.data_dir}/processed/teams.csv", index=False)
        
        if self.matches:
            matches_df = pd.DataFrame([m.to_dict() for m in self.matches])
            matches_df.to_csv(f"{self.data_dir}/processed/matches.csv", index=False)
        
        logger.info("Data saved successfully")
    
    def get_collection_summary(self) -> Dict:
        """Get summary of collected data."""
        return {
            'total_players': len(self.players),
            'total_teams': len(self.teams),
            'total_matches': len(self.matches),
            'players_with_matches': len([p for p in self.players.values() if p.total_matches > 0]),
            'teams_with_matches': len([t for t in self.teams.values() if t.total_matches > 0]),
            'matches_with_results': len([m for m in self.matches if m.radiant_win is not None]),
            'collection_timestamp': datetime.now().isoformat()
        }


def main():
    """Main function to run data collection."""
    # Load environment variables from .env file
    load_dotenv()
    
    # You can set your OpenDota API key as an environment variable
    api_key = os.getenv('OPENDOTA_API_KEY')
    
    collector = Dota2DataCollector(api_key=api_key)
    
    try:
        # Collect recent pro matches
        collector.collect_recent_pro_matches(days_back=30, max_matches=500)
        
        # Save collected data
        collector.save_data()
        
        # Print summary
        summary = collector.get_collection_summary()
        print("\nData Collection Summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
    except KeyboardInterrupt:
        logger.info("Data collection interrupted by user")
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
    finally:
        collector.client.close()


if __name__ == "__main__":
    main()

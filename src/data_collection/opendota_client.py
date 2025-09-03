"""
OpenDota API client for collecting Dota 2 match data.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OpenDotaClient:
    """
    Client for interacting with the OpenDota API to collect Dota 2 data.
    """
    
    def __init__(self, api_key: Optional[str] = None, rate_limit_delay: float = 1.0):
        """
        Initialize OpenDota client.
        
        Args:
            api_key: Optional API key for higher rate limits
            rate_limit_delay: Delay between requests in seconds
        """
        self.base_url = "https://api.opendota.com/api"
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        # Add user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Dota2DataScience/1.0 (Educational Project)'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a request to the OpenDota API with rate limiting.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response as dictionary or None if failed
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse JSON response for {endpoint}: {e}")
            return None
    
    def get_pro_matches(self, limit: int = 100, offset: int = 0, 
                       tournament_id: Optional[int] = None) -> List[Dict]:
        """
        Get professional matches from OpenDota.
        
        Args:
            limit: Number of matches to retrieve
            offset: Number of matches to skip
            tournament_id: Optional tournament ID filter
            
        Returns:
            List of professional matches
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if tournament_id:
            params['tournament_id'] = tournament_id
        
        response = self._make_request('proMatches', params)
        
        if response is None:
            return []
        
        return response
    
    def get_match_details(self, match_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific match.
        
        Args:
            match_id: Dota 2 match ID
            
        Returns:
            Match details or None if failed
        """
        return self._make_request(f'matches/{match_id}')
    
    def get_player_details(self, player_id: int) -> Optional[Dict]:
        """
        Get player profile information.
        
        Args:
            player_id: Steam account ID
            
        Returns:
            Player details or None if failed
        """
        return self._make_request(f'players/{player_id}')
    
    def get_player_matches(self, player_id: int, limit: int = 100, 
                          offset: int = 0) -> List[Dict]:
        """
        Get recent matches for a specific player.
        
        Args:
            player_id: Steam account ID
            limit: Number of matches to retrieve
            offset: Number of matches to skip
            
        Returns:
            List of player matches
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = self._make_request(f'players/{player_id}/recentMatches', params)
        
        if response is None:
            return []
        
        return response
    
    def get_player_heroes(self, player_id: int) -> List[Dict]:
        """
        Get hero statistics for a specific player.
        
        Args:
            player_id: Steam account ID
            
        Returns:
            List of hero statistics
        """
        response = self._make_request(f'players/{player_id}/heroes')
        
        if response is None:
            return []
        
        return response
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """
        Get team information.
        
        Args:
            team_id: OpenDota team ID
            
        Returns:
            Team information or None if failed
        """
        return self._make_request(f'teams/{team_id}')
    
    def get_team_matches(self, team_id: int, limit: int = 100, 
                        offset: int = 0) -> List[Dict]:
        """
        Get recent matches for a specific team.
        
        Args:
            team_id: OpenDota team ID
            limit: Number of matches to retrieve
            offset: Number of matches to skip
            
        Returns:
            List of team matches
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = self._make_request(f'teams/{team_id}/matches', params)
        
        if response is None:
            return []
        
        return response
    
    def get_team_players(self, team_id: int) -> List[Dict]:
        """
        Get current players for a specific team.
        
        Args:
            team_id: OpenDota team ID
            
        Returns:
            List of team players
        """
        response = self._make_request(f'teams/{team_id}/players')
        
        if response is None:
            return []
        
        return response
    
    def get_heroes(self) -> List[Dict]:
        """
        Get list of all Dota 2 heroes.
        
        Returns:
            List of heroes with their IDs and names
        """
        response = self._make_request('heroes')
        
        if response is None:
            return []
        
        return response
    
    def get_hero_stats(self, hero_id: int) -> Optional[Dict]:
        """
        Get statistics for a specific hero.
        
        Args:
            hero_id: Dota 2 hero ID
            
        Returns:
            Hero statistics or None if failed
        """
        return self._make_request(f'heroes/{hero_id}/stats')
    
    def get_league_info(self, league_id: int) -> Optional[Dict]:
        """
        Get information about a specific league/tournament.
        
        Args:
            league_id: OpenDota league ID
            
        Returns:
            League information or None if failed
        """
        return self._make_request(f'leagues/{league_id}')
    
    def get_league_matches(self, league_id: int, limit: int = 100, 
                          offset: int = 0) -> List[Dict]:
        """
        Get matches from a specific league/tournament.
        
        Args:
            league_id: OpenDota league ID
            limit: Number of matches to retrieve
            offset: Number of matches to skip
            
        Returns:
            List of league matches
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = self._make_request(f'leagues/{league_id}/matches', params)
        
        if response is None:
            return []
        
        return response
    
    def search_teams(self, query: str) -> List[Dict]:
        """
        Search for teams by name.
        
        Args:
            query: Team name search query
            
        Returns:
            List of matching teams
        """
        params = {'q': query}
        response = self._make_request('teams', params)
        
        if response is None:
            return []
        
        return response
    
    def search_players(self, query: str) -> List[Dict]:
        """
        Search for players by name.
        
        Args:
            query: Player name search query
            
        Returns:
            List of matching players
        """
        params = {'q': query}
        response = self._make_request('search', params)
        
        if response is None:
            return []
        
        return response
    
    def get_metadata(self) -> Optional[Dict]:
        """
        Get OpenDota metadata including patch versions and game constants.
        
        Returns:
            Metadata or None if failed
        """
        return self._make_request('metadata')
    
    def get_rankings(self, hero_id: Optional[int] = None) -> List[Dict]:
        """
        Get player rankings, optionally filtered by hero.
        
        Args:
            hero_id: Optional hero ID filter
            
        Returns:
            List of player rankings
        """
        endpoint = 'rankings'
        params = {}
        
        if hero_id:
            endpoint = f'rankings/{hero_id}'
        
        response = self._make_request(endpoint, params)
        
        if response is None:
            return []
        
        return response
    
    def get_health_status(self) -> bool:
        """
        Check if the OpenDota API is healthy.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_api_limits(self) -> Dict[str, Any]:
        """
        Get current API rate limit information.
        
        Returns:
            Dictionary with rate limit information
        """
        headers = self.session.get(f"{self.base_url}/health").headers
        
        return {
            'remaining_requests': headers.get('X-RateLimit-Remaining', 'Unknown'),
            'reset_time': headers.get('X-RateLimit-Reset', 'Unknown'),
            'limit': headers.get('X-RateLimit-Limit', 'Unknown')
        }
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

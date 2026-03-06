"""
The Blue Alliance API module for FRC scouting
"""
import requests
from typing import List, Dict, Optional


class TBAClient:
    """Client for The Blue Alliance API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.thebluealliance.com/api/v3"
        self.headers = {
            "X-TBA-Auth-Key": api_key
        }
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make a request to the TBA API"""
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None
    
    def get_events_by_year(self, year: int) -> List[Dict]:
        """Get all events for a specific year"""
        data = self._make_request(f"events/{year}")
        return data if data else []
    
    def get_event_details(self, event_key: str) -> Optional[Dict]:
        """Get details for a specific event"""
        return self._make_request(f"event/{event_key}")
    
    def get_event_teams(self, event_key: str) -> List[Dict]:
        """Get all teams at an event"""
        data = self._make_request(f"event/{event_key}/teams")
        return data if data else []
    
    def get_event_matches(self, event_key: str) -> List[Dict]:
        """Get all matches at an event"""
        data = self._make_request(f"event/{event_key}/matches")
        return data if data else []
    
    def get_team_info(self, team_key: str) -> Optional[Dict]:
        """Get information about a specific team"""
        return self._make_request(f"team/{team_key}")
    
    def get_team_events(self, team_key: str, year: int) -> List[Dict]:
        """Get all events a team participated in for a year"""
        data = self._make_request(f"team/{team_key}/events/{year}")
        return data if data else []
    
    def get_event_rankings(self, event_key: str) -> Optional[Dict]:
        """Get rankings for an event"""
        return self._make_request(f"event/{event_key}/rankings")
    
    def get_event_oprs(self, event_key: str) -> Optional[Dict]:
        """Get OPR, DPR, and CCWM for an event"""
        return self._make_request(f"event/{event_key}/oprs")

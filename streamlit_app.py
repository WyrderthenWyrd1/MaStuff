import streamlit as st
import pandas as pd
from tba_api import TBAClient
from typing import List, Dict, Optional
import statistics

# Page configuration
st.set_page_config(
    page_title="Team 4984 Scouting",
    page_icon="📊",
    layout="wide"
)

# API Configuration
TBA_API_KEY = "oPiFVCluwFZg5D38ROs1wAFf6h2CcNpww6IAJeSJem9tp2KCwTTFouYhImL8bh2o"
MY_TEAM = "frc4984"
CURRENT_YEAR = 2026

# TBA Media URLs
def get_team_logo_url(team_number):
    """Get team logo URL from TBA"""
    return f"https://www.thebluealliance.com/avatar/2024/frc{team_number}.png"

def get_team_avatar_html(team_number, size=50):
    """Generate HTML for team avatar"""
    return f'<img src="{get_team_logo_url(team_number)}" width="{size}" style="border-radius: 5px; vertical-align: middle;">'

# Initialize session state
if 'tba_client' not in st.session_state:
    st.session_state.tba_client = TBAClient(TBA_API_KEY)

if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None

if 'events_data' not in st.session_state:
    st.session_state.events_data = None

if 'matches_data' not in st.session_state:
    st.session_state.matches_data = None

if 'my_team_events' not in st.session_state:
    st.session_state.my_team_events = None

if 'selected_team' not in st.session_state:
    st.session_state.selected_team = None

if 'view_team_history' not in st.session_state:
    st.session_state.view_team_history = False

if 'scouting_competition' not in st.session_state:
    st.session_state.scouting_competition = "San Diego Comp"


def format_event_name(event):
    """Format event name for display"""
    return f"{event.get('name', 'Unknown Event')} ({event.get('event_code', 'N/A').upper()})"


def find_scouting_event(events, competition_label):
    """Find San Diego or Orange County event from annual event list."""
    if not events:
        return None

    name_keywords = {
        "San Diego Comp": ["san diego"],
        "Orange County Comp": ["orange county"]
    }

    event_name = competition_label.lower()
    for event in events:
        event_name = event.get('name', '').lower()
        if any(keyword in event_name for keyword in name_keywords.get(competition_label, [])):
            return event

    return None


def format_team_list(team_keys):
    """Convert team keys to a readable team number list."""
    return ", ".join(team.replace('frc', '') for team in team_keys)


def get_match_score_breakdown(match, alliance):
    """Extract score breakdown for an alliance"""
    if 'score_breakdown' not in match or not match['score_breakdown']:
        return {}
    
    breakdown = match['score_breakdown'].get(alliance, {})
    return breakdown


def calculate_auto_points(breakdown):
    """Calculate autonomous points from breakdown"""
    if not breakdown:
        return 0
    
    auto_points = 0
    for key, value in breakdown.items():
        if 'auto' in key.lower() and isinstance(value, (int, float)):
            auto_points += value
    
    return auto_points


def calculate_team_performance_score(team_events):
    """Calculate historical performance score for a team"""
    if not team_events:
        return 0
    
    scores = []
    for event in team_events:
        # Consider finalist/winner status
        if event.get('event_type', 0) >= 3:  # Regional or higher
            scores.append(100)
        elif event.get('event_type', 0) >= 1:
            scores.append(50)
    
    return statistics.mean(scores) if scores else 0


def predict_finalists(teams, event_key, tba_client):
    """Predict likely finalists based on historical data"""
    team_scores = []
    
    # Limit to prevent too many API calls
    max_teams_to_analyze = min(len(teams), 30)
    
    for idx, team in enumerate(teams[:max_teams_to_analyze]):
        team_key = team.get('key', '')
        
        try:
            # Get historical events for past 2 years
            events_2025 = tba_client.get_team_events(team_key, 2025) or []
            events_2024 = tba_client.get_team_events(team_key, 2024) or []
            
            # Calculate performance metrics
            total_events = len(events_2025) + len(events_2024)
            
            if total_events > 0:
                # Simple scoring: more events = more experience
                experience_score = min(total_events * 10, 100)
                
                team_scores.append({
                    'team_key': team_key,
                    'team_number': team.get('team_number'),
                    'team_name': team.get('nickname', 'Unknown'),
                    'score': experience_score,
                    'events_count': total_events
                })
        except Exception as e:
            # Skip teams that cause errors
            continue
    
    # Sort by score
    team_scores.sort(key=lambda x: x['score'], reverse=True)
    
    return team_scores[:8]  # Top 8 predicted


# Main app
st.title("Bullseye Scouting Bot 3000")
st.caption("FRC 2026 Season Analysis")

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    st.markdown("---")
    
    page = st.radio(
        "Select View:",
        ["Scouting Home", "Team Events", "All Events", "Team Lookup", "Predictions"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if st.button("Refresh Data"):
        st.session_state.my_team_events = None
        st.session_state.events_data = None
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by The Blue Alliance API")


# Team History Modal/View
if st.session_state.view_team_history and st.session_state.selected_team:
    team_key = st.session_state.selected_team
    team_num = team_key.replace('frc', '')
    
    col1, col2 = st.columns([5, 1])
    with col1:
        st.header(f"Team {team_num} Analysis")
    with col2:
        if st.button("Close"):
            st.session_state.view_team_history = False
            st.session_state.selected_team = None
            st.rerun()
    
    with st.spinner(f"Loading Team {team_num} data..."):
        team_info = st.session_state.tba_client.get_team_info(team_key)
        team_events_2026 = st.session_state.tba_client.get_team_events(team_key, 2026)
        team_events_2025 = st.session_state.tba_client.get_team_events(team_key, 2025)
        team_events_2024 = st.session_state.tba_client.get_team_events(team_key, 2024)
    
    if team_info:
        # Display team logo and info
        col_logo, col_info = st.columns([1, 4])
        with col_logo:
            st.image(get_team_logo_url(team_num), width=120)
        with col_info:
            st.subheader(team_info.get('nickname', 'N/A'))
            st.caption(f"Team {team_num}")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rookie Year", team_info.get('rookie_year', 'N/A'))
        with col2:
            location = f"{team_info.get('city', 'N/A')}, {team_info.get('state_prov', 'N/A')}"
            st.metric("Location", location)
        with col3:
            years_active = CURRENT_YEAR - team_info.get('rookie_year', CURRENT_YEAR)
            st.metric("Years Active", years_active)
        with col4:
            total_events = len(team_events_2026) + len(team_events_2025) + len(team_events_2024)
            st.metric("Total Events (3yr)", total_events)
        
        if team_info.get('website'):
            st.markdown(f"**Website:** [{team_info['website']}]({team_info['website']})")      
        
        st.markdown("---")
        
        # Tabs for different years
        tab1, tab2, tab3 = st.tabs([f"2026 Season ({len(team_events_2026)} events)", 
                                     f"2025 Season ({len(team_events_2025)} events)", 
                                     f"2024 Season ({len(team_events_2024)} events)"])
        
        with tab1:
            if team_events_2026:
                for event in team_events_2026:
                    st.markdown(f"**{event.get('name')}** - Week {event.get('week', 'N/A')}")
                    st.caption(f"{event.get('city')}, {event.get('state_prov')} | {event.get('start_date')}")
                    if st.button(f"View Event Details", key=f"view_event_{event.get('key')}"):
                        st.session_state.selected_event = event
                        st.session_state.view_team_history = False
                        st.rerun()
                    st.markdown("---")
            else:
                st.info(f"No 2026 events found for Team {team_num}")
        
        with tab2:
            if team_events_2025:
                for event in team_events_2025:
                    st.markdown(f"**{event.get('name')}** - Week {event.get('week', 'N/A')}")
                    st.caption(f"{event.get('city')}, {event.get('state_prov')} | {event.get('start_date')}")
                    st.markdown("---")
            else:
                st.info(f"No 2025 events found for Team {team_num}")
        
        with tab3:
            if team_events_2024:
                for event in team_events_2024:
                    st.markdown(f"**{event.get('name')}** - Week {event.get('week', 'N/A')}")
                    st.caption(f"{event.get('city')}, {event.get('state_prov')} | {event.get('start_date')}")
                    st.markdown("---")
            else:
                st.info(f"No 2024 events found for Team {team_num}")
    else:
        st.error(f"Could not load data for Team {team_num}")
    
    st.stop()


# Page: Team Events
if page == "Scouting Home":
    st.header("Scouting Home")
    st.caption("Pick your event, then choose Red or Blue alliance for qualification match scouting.")

    competition = st.radio(
        "Which competition are you scouting?",
        ["San Diego Comp", "Orange County Comp"],
        horizontal=True,
        index=0 if st.session_state.scouting_competition == "San Diego Comp" else 1
    )
    st.session_state.scouting_competition = competition

    if st.session_state.events_data is None:
        with st.spinner("Loading 2026 events..."):
            st.session_state.events_data = st.session_state.tba_client.get_events_by_year(CURRENT_YEAR)

    selected_event = find_scouting_event(st.session_state.events_data, competition)

    if not selected_event:
        st.warning(f"Could not find a 2026 event matching '{competition}' yet.")
    else:
        st.success(f"Selected event: {selected_event.get('name', 'Unknown Event')}")
        st.caption(
            f"{selected_event.get('city', 'N/A')}, {selected_event.get('state_prov', 'N/A')} | "
            f"{selected_event.get('start_date', 'N/A')}"
        )

        with st.spinner("Loading qualification matches..."):
            matches = st.session_state.tba_client.get_event_matches(selected_event['key'])

        qual_matches = [m for m in matches if m.get('comp_level') == 'qm']
        qual_matches.sort(key=lambda x: x.get('match_number', 0))

        if not qual_matches:
            st.info("Qualification matches are not available yet for this event.")
        else:
            alliance_choice = st.radio(
                "Which alliance are you scouting?",
                ["Red", "Blue"],
                horizontal=True
            )

            st.subheader(f"Qualification Matches ({len(qual_matches)})")

            for match in qual_matches:
                red_alliance = match.get('alliances', {}).get('red', {})
                blue_alliance = match.get('alliances', {}).get('blue', {})

                scouting_team_keys = (
                    red_alliance.get('team_keys', [])
                    if alliance_choice == "Red"
                    else blue_alliance.get('team_keys', [])
                )

                with st.expander(f"Qual Match {match.get('match_number', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Red Alliance**")
                        st.write(format_team_list(red_alliance.get('team_keys', [])))
                        st.metric("Red Score", red_alliance.get('score', 0))
                    with col2:
                        st.markdown("**Blue Alliance**")
                        st.write(format_team_list(blue_alliance.get('team_keys', [])))
                        st.metric("Blue Score", blue_alliance.get('score', 0))

                    st.markdown(f"**Scouting Focus ({alliance_choice}):** {format_team_list(scouting_team_keys)}")

elif page == "Team Events":
    st.header("Team 4984 - 2026 Season Schedule")
    
    # Load team events
    if st.session_state.my_team_events is None:
        with st.spinner("Loading event data..."):
            st.session_state.my_team_events = st.session_state.tba_client.get_team_events(MY_TEAM, CURRENT_YEAR)
    
    our_events = st.session_state.my_team_events
    
    if our_events and len(our_events) > 0:
        st.info(f"Registered for {len(our_events)} event(s) in 2026")
        
        for idx, event in enumerate(our_events):
            with st.container():
                st.markdown(f"## {event.get('name', 'Event')}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Location", f"{event.get('city', 'N/A')}, {event.get('state_prov', 'N/A')}")
                with col2:
                    st.metric("Week", event.get('week', 'N/A'))
                with col3:
                    st.metric("Start Date", event.get('start_date', 'N/A'))
                with col4:
                    st.metric("Type", event.get('event_type_string', 'Regional'))
                
                # Show event details button
                if st.button(f"View Full Event Details", key=f"view_our_event_{idx}"):
                    st.session_state.selected_event = event
                    st.rerun()
                
                st.markdown("---")
                
                # Show teams at this event
                with st.expander(f"Competing Teams - {event.get('name')}"):
                    with st.spinner("Loading team roster..."):
                        teams = st.session_state.tba_client.get_event_teams(event['key'])
                    
                    if teams:
                        st.write(f"**{len(teams)} teams registered**")
                        
                        # Display teams in a grid with logos
                        cols_per_row = 6
                        for i in range(0, len(teams), cols_per_row):
                            cols = st.columns(cols_per_row)
                            for j, team in enumerate(teams[i:i+cols_per_row]):
                                with cols[j]:
                                    team_key = team.get('key', '')
                                    team_num = team.get('team_number', 'N/A')
                                    team_name = team.get('nickname', 'Unknown')
                                    
                                    # Highlight our team
                                    if team_key == MY_TEAM:
                                        st.markdown(f"**{team_num}** (Us)")
                                        st.caption(team_name)
                                    else:
                                        if st.button(f"{team_num}", key=f"team_{event['key']}_{team_key}"):
                                            st.session_state.selected_team = team_key
                                            st.session_state.view_team_history = True
                                            st.rerun()
                                        st.caption(team_name)
                
                st.markdown("---")
    else:
        st.warning("No events scheduled for Team 4984 in 2026.")
        st.markdown("Event registration may not be complete.")

# Page: All Events
elif page == "All Events":
    st.header("2026 FRC Events")
    
    with st.spinner("Loading events..."):
        events = st.session_state.tba_client.get_events_by_year(CURRENT_YEAR)
        st.session_state.events_data = events
    
    if events:
        st.write(f"**{len(events)} events in 2026**")
        
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("Search events by name or location", "")
        
        with col2:
            event_types = list(set([e.get('event_type_string', 'Unknown') for e in events]))
            event_types.insert(0, "All Types")
            selected_type = st.selectbox("Type", event_types)
        
        with col3:
            weeks = list(set([e.get('week', 0) for e in events if e.get('week') is not None]))
            weeks.sort()
            weeks.insert(0, "All Weeks")
            selected_week = st.selectbox("Week", weeks)
        
        # Filter events
        filtered_events = events
        
        if search_term:
            filtered_events = [
                e for e in filtered_events
                if search_term.lower() in e.get('name', '').lower()
                or search_term.lower() in e.get('city', '').lower()
                or search_term.lower() in e.get('state_prov', '').lower()
            ]
        
        if selected_type != "All Types":
            filtered_events = [e for e in filtered_events if e.get('event_type_string') == selected_type]
        
        if selected_week != "All Weeks":
            filtered_events = [e for e in filtered_events if e.get('week') == selected_week]
        
        st.markdown(f"### {len(filtered_events)} events")
        
        # Display events
        if filtered_events:
            for event in filtered_events:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{event.get('name')}**")
                with col2:
                    st.caption(f"{event.get('city')}, {event.get('state_prov')} • Week {event.get('week', 'N/A')}")
                with col3:
                    if st.button("View", key=f"view_browse_{event.get('key')}"):
                        st.session_state.selected_event = event
                        st.rerun()
        
    else:
        st.warning("No events found for 2026 yet.")

# Page: Team Lookup
elif page == "Team Lookup":
    st.header("Team Information Lookup")
    
    team_number = st.text_input("Enter team number", placeholder="e.g., 254, 1678, 118")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Search Team"):
            if team_number:
                st.session_state.selected_team = f"frc{team_number}"
                st.session_state.view_team_history = True
                st.rerun()


# Page: Predictions
elif page == "Predictions":
    st.header("Event Performance Predictions")
    st.caption("Based on historical data from 2024-2025 seasons")
    st.warning("Note: This analysis may take 30-60 seconds due to API rate limits. Analysis limited to first 30 teams.")
    
    # Load team events first
    if st.session_state.my_team_events is None:
        with st.spinner("Loading data..."):
            st.session_state.my_team_events = st.session_state.tba_client.get_team_events(MY_TEAM, CURRENT_YEAR)
    
    our_events = st.session_state.my_team_events
    
    if our_events and len(our_events) > 0:
        selected_event_name = st.selectbox(
            "Select Event for Analysis",
            [e.get('name', 'Unknown') for e in our_events]
        )
        
        selected_event = next((e for e in our_events if e.get('name') == selected_event_name), None)
        
        if selected_event and st.button("Run Prediction Analysis"):
            st.subheader(f"Predicted Finalists: {selected_event.get('name')}")
            
            try:
                with st.spinner("Analyzing historical performance data (this may take a minute)..."):
                    teams = st.session_state.tba_client.get_event_teams(selected_event['key'])
                    
                    if teams:
                        st.info(f"Analyzing {min(len(teams), 30)} of {len(teams)} teams...")
                        predictions = predict_finalists(teams, selected_event['key'], st.session_state.tba_client)
                        
                        if predictions:
                            st.success(f"Analysis complete! Top {len(predictions)} predicted performers:")
                            
                            for idx, pred in enumerate(predictions, 1):
                                col1, col2, col3, col4 = st.columns([1, 2, 3, 2])
                                with col1:
                                    st.markdown(f"**#{idx}**")
                                with col2:
                                    st.markdown(f"**Team {pred['team_number']}**")
                                with col3:
                                    st.markdown(pred['team_name'])
                                with col4:
                                    st.caption(f"{pred['events_count']} events (2024-25)")
                        else:
                            st.warning("Insufficient historical data for predictions")
                    else:
                        st.warning("No team data available yet")
            except Exception as e:
                st.error(f"Error running predictions: {str(e)}")
                st.info("This may be due to API rate limits. Please try again in a few minutes.")
    else:
        st.warning("No events scheduled for analysis")


# Show Event Details if an event is selected
if st.session_state.selected_event and not st.session_state.view_team_history:
        event = st.session_state.selected_event
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.header(format_event_name(event))
        with col2:
            if st.button("← Back"):
                st.session_state.selected_event = None
                st.rerun()
        
        # Event info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Week", event.get('week', 'N/A'))
        with col2:
            st.metric("Type", event.get('event_type_string', 'Unknown'))
        with col3:
            st.metric("Start Date", event.get('start_date', 'N/A'))
        with col4:
            st.metric("End Date", event.get('end_date', 'N/A'))
        
        st.markdown(f"**Location:** {event.get('city', 'N/A')}, {event.get('state_prov', 'N/A')}, {event.get('country', 'N/A')}")
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Matches", "Teams", "Rankings", "Statistics"])
        
        with tab1:
            st.subheader("Match Results")
            
            with st.spinner("Loading matches..."):
                matches = st.session_state.tba_client.get_event_matches(event['key'])
            
            if matches:
                matches.sort(key=lambda x: (x.get('comp_level', ''), x.get('match_number', 0)))
                
                comp_levels = list(set([m.get('comp_level', 'qm') for m in matches]))
                selected_comp = st.selectbox("Competition Level", comp_levels)
                
                filtered_matches = [m for m in matches if m.get('comp_level') == selected_comp]
                
                team_search = st.text_input("Filter by team number")
                
                if team_search:
                    filtered_matches = [
                        m for m in filtered_matches
                        if any(f"frc{team_search}" in team for team in 
                               m.get('alliances', {}).get('red', {}).get('team_keys', []) +
                               m.get('alliances', {}).get('blue', {}).get('team_keys', []))
                    ]
                
                for match in filtered_matches:
                    with st.expander(f"Match {match.get('match_number', 'N/A')} - {match.get('comp_level', 'qm').upper()}"):
                        col1, col2 = st.columns(2)
                        
                        red_alliance = match.get('alliances', {}).get('red', {})
                        blue_alliance = match.get('alliances', {}).get('blue', {})
                        
                        with col1:
                            st.markdown("**Red Alliance**")
                            red_team_keys = red_alliance.get('team_keys', [])
                            
                            # Get team info for display
                            for team_key in red_team_keys:
                                team_num = team_key.replace('frc', '')
                                # Fetch team name
                                team_info = st.session_state.tba_client.get_team_info(team_key)
                                team_name = team_info.get('nickname', 'Unknown') if team_info else 'Unknown'
                                
                                col_btn, col_name = st.columns([1, 3])
                                with col_btn:
                                    if team_key == MY_TEAM:
                                        st.markdown(f"**{team_num}** (Us)")
                                    else:
                                        if st.button(team_num, key=f"match_red_{match.get('key')}_{team_key}"):
                                            st.session_state.selected_team = team_key
                                            st.session_state.view_team_history = True
                                            st.rerun()
                                with col_name:
                                    st.caption(team_name)
                            
                            st.metric("Score", red_alliance.get('score', 0))
                            
                            red_breakdown = get_match_score_breakdown(match, 'red')
                            if red_breakdown:
                                auto_pts = calculate_auto_points(red_breakdown)
                                st.caption(f"Autonomous: {auto_pts} pts")
                        
                        with col2:
                            st.markdown("**Blue Alliance**")
                            blue_team_keys = blue_alliance.get('team_keys', [])
                            
                            # Get team info for display
                            for team_key in blue_team_keys:
                                team_num = team_key.replace('frc', '')
                                # Fetch team name
                                team_info = st.session_state.tba_client.get_team_info(team_key)
                                team_name = team_info.get('nickname', 'Unknown') if team_info else 'Unknown'
                                
                                col_btn, col_name = st.columns([1, 3])
                                with col_btn:
                                    if team_key == MY_TEAM:
                                        st.markdown(f"**{team_num}** (Us)")
                                    else:
                                        if st.button(team_num, key=f"match_blue_{match.get('key')}_{team_key}"):
                                            st.session_state.selected_team = team_key
                                            st.session_state.view_team_history = True
                                            st.rerun()
                                with col_name:
                                    st.caption(team_name)
                            
                            st.metric("Score", blue_alliance.get('score', 0))
                            
                            blue_breakdown = get_match_score_breakdown(match, 'blue')
                            if blue_breakdown:
                                auto_pts = calculate_auto_points(blue_breakdown)
                                st.caption(f"Autonomous: {auto_pts} pts")
                        
                        if match.get('winning_alliance'):
                            winner = match['winning_alliance'].upper()
                            st.success(f"Winner: {winner} Alliance")
            else:
                st.info("No match data available yet.")
        
        with tab2:
            st.subheader("Participating Teams")
            
            with st.spinner("Loading teams..."):
                teams = st.session_state.tba_client.get_event_teams(event['key'])
            
            if teams:
                st.write(f"**{len(teams)} teams registered**")
                st.caption("Click a team number to view detailed history")
                
                # Create a dataframe with team info
                teams_data = []
                for team in teams:
                    teams_data.append({
                        'Number': team.get('team_number', 'N/A'),
                        'Team Name': team.get('nickname', 'Unknown'),
                        'Location': f"{team.get('city', 'N/A')}, {team.get('state_prov', 'N/A')}",
                        'Rookie Year': team.get('rookie_year', 'N/A'),
                        'key': team.get('key', '')
                    })
                
                df = pd.DataFrame(teams_data)
                st.dataframe(df[['Number', 'Team Name', 'Location', 'Rookie Year']], use_container_width=True, hide_index=True)
                
                # Team selection for history
                st.markdown("---")
                selected_team_num = st.number_input("View team history (enter number)", min_value=1, max_value=99999, step=1, value=None)
                if st.button("View Team History") and selected_team_num:
                    st.session_state.selected_team = f"frc{int(selected_team_num)}"
                    st.session_state.view_team_history = True
                    st.rerun()
            else:
                st.info("No team data available yet.")
        
        with tab3:
            st.subheader("Event Rankings")
            
            with st.spinner("Loading rankings..."):
                rankings = st.session_state.tba_client.get_event_rankings(event['key'])
            
            if rankings and 'rankings' in rankings:
                rankings_list = rankings['rankings']
                
                rankings_df = []
                for rank in rankings_list:
                    rankings_df.append({
                        'Rank': rank.get('rank', 'N/A'),
                        'Team': rank.get('team_key', 'N/A').replace('frc', ''),
                        'Ranking Points': rank.get('sort_orders', [0])[0] if rank.get('sort_orders') else 0,
                        'Record (W-L-T)': f"{rank.get('record', {}).get('wins', 0)}-{rank.get('record', {}).get('losses', 0)}-{rank.get('record', {}).get('ties', 0)}"
                    })
                
                df = pd.DataFrame(rankings_df)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No ranking data available yet.")
        
        with tab4:
            st.subheader("OPR Statistics")
            st.caption("OPR = Offensive Power Rating | DPR = Defensive Power Rating | CCWM = Calculated Contribution to Winning Margin")
            
            with st.spinner("Loading statistics..."):
                oprs = st.session_state.tba_client.get_event_oprs(event['key'])
            
            if oprs:
                opr_data = []
                opr_dict = oprs.get('oprs', {})
                dpr_dict = oprs.get('dprs', {})
                ccwm_dict = oprs.get('ccwms', {})
                
                for team_key in opr_dict.keys():
                    opr_data.append({
                        'Team': team_key.replace('frc', ''),
                        'OPR': round(opr_dict.get(team_key, 0), 2),
                        'DPR': round(dpr_dict.get(team_key, 0), 2),
                        'CCWM': round(ccwm_dict.get(team_key, 0), 2)
                    })
                
                df = pd.DataFrame(opr_data)
                df = df.sort_values('OPR', ascending=False)
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Visualization
                st.markdown("### OPR Distribution")
                st.bar_chart(df.set_index('Team')['OPR'])
            else:
                st.info("No statistical data available for this event yet.")

st.markdown("---")
st.caption("Team 4984 Scouting System | Data provided by The Blue Alliance API | thebluealliance.com")

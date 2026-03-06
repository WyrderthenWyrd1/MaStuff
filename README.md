# FRC Scouting Tool 🤖

A comprehensive web-based scouting tool for FIRST Robotics Competition (FRC) teams to analyze competition data using The Blue Alliance API.

## 🌐 Features

- **2026 Season Events**: Browse all FRC events for the 2026 season
- **Advanced Search & Filtering**: 
  - Search by event name or location
  - Filter by event type and week
- **Detailed Event Analysis**:
  - Match results with score breakdowns
  - Autonomous points tracking
  - Team rosters and information
  - Live rankings
  - OPR/DPR/CCWM statistics with visualizations
- **Team Analysis**: Deep dive into individual team performance and event history
- **Real-time Data**: All data pulled directly from The Blue Alliance API

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- The Blue Alliance API key (already configured in the app)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run streamlit_app.py
```

3. Open your browser to the URL shown (usually `http://localhost:8501`)

## 📊 How to Use

### Events Browser

1. Navigate to the "📅 Events Browser" page (default view)
2. Browse through all 2026 FRC events
3. Use the search box to find specific events by name or location
4. Filter by event type (Regional, District, Championship, etc.) or week
5. Click on any event to view details

### Event Details

1. Select an event from the Events Browser
2. View comprehensive event information across 4 tabs:
   - **🏁 Matches**: View all match results with scores and autonomous points
     - Filter by qualification/playoff matches
     - Search for specific team numbers
   - **👥 Teams**: See all participating teams with their information
   - **📊 Rankings**: View current event standings
   - **📈 Statistics**: Analyze OPR (Offensive Power Rating), DPR (Defensive Power Rating), and CCWM statistics

### Team Analysis

1. Navigate to "📊 Team Analysis"
2. Enter a team number (e.g., 254, 1678, 118)
3. View team information:
   - Basic info (rookie year, location)
   - 2026 event schedule
   - Historical data

## 🔑 API Information

This app uses **The Blue Alliance API** to fetch all FRC data. The API key is already configured in the application.

### API Rate Limits

- The Blue Alliance has rate limits on API requests
- Data is cached in session state to minimize API calls
- If you experience slow loading, wait a few moments between requests

### Learn More

- [The Blue Alliance](https://www.thebluealliance.com)
- [TBA API Documentation](https://www.thebluealliance.com/apidocs/v3)

## 🚀 Deploy & Share

Deploy for **FREE** on Streamlit Community Cloud:

1. **Push to GitHub**:
   - Create a new repository on GitHub
   - Push this folder to the repository

2. **Deploy on Streamlit**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository, branch, and `streamlit_app.py`
   - Click "Deploy"

3. **Share the URL**: Your team can now access the scouting tool from anywhere!

## 📁 Project Structure

```
├── streamlit_app.py    # Main web application
├── tba_api.py          # The Blue Alliance API client
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔧 Technical Details

### Key Statistics Explained

- **OPR (Offensive Power Rating)**: A measure of a team's offensive contribution to their alliance's score
- **DPR (Defensive Power Rating)**: A measure of a team's defensive impact on the opponent's score
- **CCWM (Calculated Contribution to Winning Margin)**: The team's contribution to the winning margin

### Data Sources

All competition data is sourced from The Blue Alliance API in real-time, ensuring you always have the most up-to-date information.

## 🤝 Contributing

This is a community tool for FRC teams. Feel free to fork and customize for your team's specific needs!

## 📝 License

Free to use and modify for FRC scouting purposes.

## 👤 Author

Made by seb.

---

**Good luck with your scouting! 🤖🏆**

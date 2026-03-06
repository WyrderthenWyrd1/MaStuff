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

<<<<<<< HEAD
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
=======
### Deploy & Share with Friends 🚀
>>>>>>> bf4de144de7690f42b854360e742aca18587fcad

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

<<<<<<< HEAD
3. **Share the URL**: Your team can now access the scouting tool from anywhere!

## 📁 Project Structure
=======
3. **Share the URL**: Your friends can now access your app from anywhere!
>>>>>>> bf4de144de7690f42b854360e742aca18587fcad

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

<<<<<<< HEAD
**Good luck with your scouting! 🤖🏆**
=======
## 💻 Desktop App Version

The desktop version (`grade_calculator.py`) runs locally with a traditional GUI.

Desktop app includes:
- Adjustable GPA scale calculator (for example 4.0 or 5.0)
- Per-class grade preview directly in the class list
- AP checkbox per class that boosts weighted GPA scaling

### Requirements

- Python 3.6 or higher (includes Tkinter by default)

### How to Run

```bash
python grade_calculator.py
```

## How to Use

### Adding a Class

1. Click the "Add Class" button in the left panel
2. Enter the class name (e.g., "Math 101", "English Literature")
3. The class will appear in the list

### Adding Categories

1. Select a class from the left panel
2. Click "Add Category" button
3. Enter category name (e.g., "Homework", "Tests", "Quizzes")
4. Enter the weight percentage (e.g., 25 for 25%)
5. Make sure all category weights add up to 100% for accurate grading

### Adding Assignments

1. Select a class from the left panel
2. Select a category from the tree view (or click on an assignment within that category)
3. Click "Add Assignment" button
4. Enter:
   - Assignment name (e.g., "Quiz 1", "Chapter 5 Homework")
   - Total points possible (e.g., 100)
   - Points earned (e.g., 85)

### Editing Items

1. Select a category or assignment in the tree view
2. Click "Edit" button
3. Modify the information
4. Click OK to save changes

### Deleting Items

1. Select a category or assignment in the tree view
2. Click "Delete" button
3. Confirm the deletion

### Viewing Grades

- Each assignment shows its percentage score
- Each category shows its overall percentage (average of all assignments in that category)
- The overall grade is displayed at the bottom, calculated as a weighted average of all categories
- Letter grade is automatically calculated based on standard grading scale:
  - A: 93-100%, A-: 90-92%
  - B+: 87-89%, B: 83-86%, B-: 80-82%
  - C+: 77-79%, C: 73-76%, C-: 70-72%
  - D+: 67-69%, D: 63-66%, D-: 60-62%
  - F: Below 60%

## Data Storage

All data is automatically saved to `grade_data.json` in the same directory as the application. This file is created automatically and updated whenever you make changes.

## Example Usage

1. Add a class: "Biology 101"
2. Add categories:
   - Tests (50%)
   - Labs (30%)
   - Homework (20%)
3. Add assignments:
   - Under Tests: "Midterm" - 100 points total, 87 earned
   - Under Labs: "Lab 1" - 50 points total, 48 earned
   - Under Homework: "HW 1" - 20 points total, 18 earned
4. The app will automatically calculate your current grade based on the weighted averages

## Tips

- Keep category weights balanced and totaling 100% for accurate grade calculations
- Enter assignments as you complete them to track your progress throughout the semester
- You can have different category structures for different classes
- The app saves automatically, so your data is always preserved

## Troubleshooting

**App won't start**: Make sure Python is installed and Tkinter is available (it's included by default with Python)

**Data not saving**: Check that you have write permissions in the application directory

**Wrong grade calculation**: Verify that your category weights add up to 100%

## License

Free to use and modify for personal or educational purposes.
>>>>>>> bf4de144de7690f42b854360e742aca18587fcad

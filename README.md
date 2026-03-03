# Grade Calculator

A comprehensive grade calculator available as both a **web app** and **desktop app** for tracking school grades with customizable category weightings and point tracking.

## 🌐 Web App Version (Recommended for Sharing!)

The **Streamlit web app** (`streamlit_app.py`) is perfect for sharing with friends - they can access it through a URL!

### Features

- **Multiple Classes**: Manage grades for multiple classes simultaneously
- **Category Weighting**: Set custom weight percentages for different categories (e.g., Homework 20%, Tests 40%, Projects 40%)
- **Assignment Tracking**: Track points earned and total points for each assignment
- **Automatic Grade Calculation**: Calculates weighted averages and displays overall grade with letter grade
- **Data Persistence**: Automatically saves data to `grade_data.json`
- **Web-Based**: Access from any device with a browser

### Run Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run streamlit_app.py
```

3. Open your browser to the URL shown (usually `http://localhost:8501`)

### AI Chatbot Setup (Optional)

The app includes an AI-powered chatbot in the message board. To enable real AI responses:

1. Get a Hugging Face API key:
   - Go to [huggingface.co](https://huggingface.co)
   - Sign in with your GitHub account (free!)
   - Go to Settings → Access Tokens
   - Create a new token with "Read" access
2. Create a `.streamlit/secrets.toml` file (see `.streamlit/secrets.toml.example`)
3. Add your key: `HUGGINGFACE_API_KEY = "your-key-here"`

**Note**: The bot stays silent without an API key, but with Hugging Face it's sassy and free!

### Deploy & Share with Friends 🚀

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

3. **Add Hugging Face API Key (Optional for AI chatbot)**:
   - In your deployed app, click "Manage app" (bottom right)
   - Go to Settings → Secrets
   - Add: `HUGGINGFACE_API_KEY = "your-key-here"`
   - Save and the app will restart with AI enabled

4. **Share the URL**: Your friends can now access your app from anywhere!

**Note**: Data on Streamlit Cloud resets when the app restarts. For persistent data across deployments, consider using Streamlit's database integration.

---

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

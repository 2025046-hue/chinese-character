# Chinese Character Learning App

A comprehensive Chinese character learning application built with Streamlit that allows users to practice writing Chinese characters through both visual tracing and audio prompt exercises.


https://github.com/user-attachments/assets/8f018129-8934-41ed-9618-023c40695570


## 🌟 Features

### User Management
- User login and account creation
- Personalized progress tracking
- Session history logging

### Learning Modules
- **Tracing Practice**: Draw Chinese characters by following visual references
- **Audio Prompt Practice**: Listen to character pronunciation and practice writing
- **Progress Tracking**: Detailed analytics on character mastery and overall performance

### Progress Analytics
- Character-by-character progress tracking
- Overall accuracy metrics
- Attempt history and performance trends
- Session-based learning statistics

### User Experience
- Intuitive navigation between different learning modules
- Responsive UI with clear feedback after each exercise
- Clean, user-friendly interface optimized for learning

## 🛠️ Technologies Used

- **Streamlit**: Web-based UI framework
- **Python**: Core application logic
- **JSON**: Data storage for user progress and settings
- **Audio Engine**: Text-to-speech for character pronunciation
- **Canvas Widget**: Character drawing and stroke tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pipx package manager

### Installation

1. **Clone or download the repository**

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pipx install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```
## OR just use this script ^_^

**On Windows:**
- Double-click `setup_and_run.bat` (for Command Prompt) or `setup_and_run.ps1` (for PowerShell)
- The script will create a virtual environment, install dependencies, and start the app

**On macOS/Linux:**
- Make the script executable: `chmod +x setup_and_run.sh`
- Run the script: `./setup_and_run.sh`
- The script will create a virtual environment, install dependencies, and start the app

## 📖 Usage Guide

### Getting Started
1. Upon launching the app, you'll see the login screen
2. Enter a username to either log in (if existing) or create a new account
3. Access the main menu to choose between practice modules

### Main Menu Options
- **Tracing Module**: Practice writing characters by following visual references
- **Audio Prompt Module**: Listen to character pronunciation and practice writing from audio cues
- **View Progress**: See your learning statistics and character mastery
- **Exit**: Return to the login screen

### Tracing Practice
1. Select a character from the grid to practice
2. Use the canvas to trace the character
3. View reference images to guide your writing
4. Submit your attempt to receive feedback
5. Return to the grid or menu as needed

### Audio Prompt Practice
1. Select a character from the grid
2. Listen to the character pronunciation using the audio controls
3. Practice writing the character while listening
4. Submit your attempt to receive feedback
5. Navigate between options as needed

### Progress Tracking
- View overall statistics (total attempts, success rate, accuracy)
- Browse character-specific progress with expandable sections
- See detailed session history for each character
- Track your learning journey over time

## 🔧 Project Structure

```
chinese/
├── streamlit_app.py          # Main application file
├── requirements.txt         # Python dependencies
├── README.md              # This file
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── app/                  # Application modules
│   ├── __init__.py
│   ├── asset_loader.py   # Character image loading
│   ├── audio_engine.py   # Text-to-speech functionality
│   ├── auth.py          # User authentication
│   ├── canvas_widget.py # Drawing canvas implementation
│   ├── constants.py     # Application constants
│   ├── evaluation_engine.py # Character evaluation logic
│   ├── gui.py          # GUI components
│   ├── logger.py       # Logging functionality
│   ├── main.py        # Main application logic
│   ├── progress.py    # Progress tracking
├── data/              # Data storage directory
│   ├── tracing_characters.json  # Tracing practice characters
│   ├── audio_characters.json    # Audio practice characters
├── logs/             # Application logs
└── test/            # Test files
```

## 🎯 Learning Methodology

The application implements two complementary learning approaches:

### Visual Learning (Tracing Module)
- Users trace characters with visual guidance
- Helps build muscle memory and stroke order understanding
- Provides immediate feedback on accuracy

### Auditory Learning (Audio Prompt Module)
- Users hear character pronunciation and practice writing
- Strengthens connection between sound and visual form
- Enhances overall character recognition

## 📊 Progress Tracking

The application meticulously tracks learning progress:
- Character-specific statistics (attempts, accuracy, success rate)
- Overall user performance metrics
- Session history for reviewing progress over time
- Detailed feedback for each practice attempt

## 🚧 Development

### Adding New Characters
Characters are stored in JSON files in the `data/` directory:
- `tracing_characters.json` - for visual tracing practice
- `audio_characters.json` - for audio prompt practice

Each character entry includes:
- `char`: The Chinese character
- `pinyin`: Pronunciation guide
- `meaning`: English translation
- `difficulty`: Difficulty level (beginner, medium, hard)

### Extending Functionality
The modular architecture makes it easy to:
- Add new practice modules
- Enhance evaluation algorithms
- Integrate additional learning resources
- Customize user experience

## 📋 Requirements

- Python 3.11+
- Streamlit
- streamlit-drawable-canvas
- gtts (for audio features)
- Pillow (for image processing)

All required packages are listed in `requirements.txt`.



# SE Forms Questions - Flashcards

A flashcard application built with pygame that helps you study Software Engineering questions from the SE-FORMS-QUESTIONS.tex file.

## Features

- 🃏 Interactive flashcards with questions and answers
- 🔀 Random shuffle of questions
- ⌨️ Both mouse and keyboard controls
- 📊 Progress tracking (current card number)
- 🎨 Clean, modern interface

## Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the flashcard application:
```bash
python flashcards.py
```

## Controls

### Mouse Controls
- **Click on card**: Flip between question and answer
- **Previous button**: Go to previous card
- **Next button**: Go to next card
- **Shuffle button**: Randomize card order

### Keyboard Controls
- **Space**: Flip card (question ↔ answer)
- **Left Arrow / P**: Previous card
- **Right Arrow / N**: Next card
- **S**: Shuffle cards

## How It Works

1. The application parses the `SE-FORMS-QUESTIONS.tex` file
2. Extracts questions from `\begin{questionbox}...\end{questionbox}` blocks
3. Associates each question with its corresponding answer
4. Creates interactive flashcards for studying
5. Supports random shuffling for better learning

## File Structure

```
se-flashcards/
├── flashcards.py          # Main application
├── SE-FORMS-QUESTIONS.tex # Source questions file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── venv/                 # Virtual environment
```

## Requirements

- Python 3.7+
- pygame 2.6.1
- macOS (tested on Apple Silicon)

Enjoy studying! 🎓 
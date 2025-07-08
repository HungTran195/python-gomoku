# Gomoku Game
![Alt Text](https://github.com/HungTran195/python-gomoku/blob/master/static/images/screenshot.png) 

A web-based implementation of Gomoku (Five in a Row) built with FastAPI and Socket.IO. Play against an AI opponent or challenge a friend in real-time.

## What is Gomoku?

Gomoku is a strategic board game where two players take turns placing stones on a 15×15 grid. The goal is simple: be the first to get five of your stones in a row horizontally, vertically, or diagonally. It's like tic-tac-toe but more complex and strategic.

## Game Modes

### Single Player vs AI
- Play against a computer opponent using the minimax algorithm
- The AI analyzes the board and makes strategic moves
- Perfect for practicing or playing when you're alone

### Player vs Player (PvP)
- Challenge a friend in real-time using WebSocket connections
- Both players connect to the same game room
- Real-time updates show moves instantly

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8000`


## Project Structure

```
python-gomoku/
├── game/                    # Core game logic
│   ├── game.py             # Game state management
│   ├── minimax.py          # AI algorithm implementation
│   ├── views.py            # Socket.IO event handlers
│   └── helper.py           # Utility functions
├── static/                 # CSS, JS, and images
├── templates/              # HTML templates
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings
└── requirements.txt        # Dependencies
```

## Configuration

Key settings in `config.py`:
- Board size (default: 15×15)
- AI search depth
- Server host/port
- Game types and modes

## Development

### Local Development
```bash
python main.py
```

### Production
```bash
uvicorn main:socket_app --host 0.0.0.0 --port 8000
```

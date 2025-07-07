# Python Gomoku Game

A modern Gomoku (Five in a Row) game built with Django 5.3 and optimized game logic.

## Features

- **Modern Django 5.3**: Updated to the latest Django version with improved security and performance
- **Optimized Game Logic**: Enhanced minimax algorithm with alpha-beta pruning and numpy optimization
- **Real-time Gameplay**: WebSocket-based real-time game updates
- **AI Opponent**: Intelligent AI using minimax algorithm with depth-limited search
- **Player vs Player**: Support for both single-player (vs AI) and multiplayer modes
- **Responsive UI**: Modern, responsive web interface
- **Type Safety**: Full type hints and improved code quality

## Game Logic Optimizations

### Game Engine (`game.py`)
- **Numpy Integration**: Using numpy arrays for better performance in board operations
- **Optimized Win Detection**: Pre-computed direction vectors and efficient line counting
- **Type Safety**: Full type hints and null safety checks
- **Memory Efficiency**: Reduced memory usage with optimized data structures

### AI Engine (`minimax.py`)
- **Alpha-Beta Pruning**: Improved search efficiency with proper alpha-beta pruning
- **Numpy Operations**: Vectorized operations for faster board analysis
- **Smart Move Generation**: Only considers moves around existing pieces for computational efficiency
- **Configurable Depth**: Adjustable search depth for different difficulty levels
- **Early Termination**: Quick win detection to avoid unnecessary calculations

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd python-gomoku
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # Create .env file from example
   # Edit .env file with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the game**
   Open your browser and navigate to `http://localhost:8000`

## Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS_URL=localhost
```

### Game Settings
Game configuration can be modified in `python-gomoku/settings.py`:

```python
# Board size
NUMBER_OF_ROW = 15
NUMBER_OF_COL = 15

# Game types
GAME_TYPE_SINGLE = 'single'
GAME_TYPE_PVP = 'pvp'

# AI configuration
AI_ID = 'AI_0'
```

## Game Rules

- Players take turns placing stones on a 15x15 grid
- First player to get 5 stones in a row (horizontally, vertically, or diagonally) wins
- The game supports both single-player (vs AI) and two-player modes
- AI uses minimax algorithm with alpha-beta pruning for intelligent gameplay

## Technical Improvements

### Performance Optimizations
- **Numpy Arrays**: Replaced Python lists with numpy arrays for faster board operations
- **Vectorized Operations**: Used numpy's vectorized operations for win detection
- **Memory Management**: Optimized memory usage with efficient data structures
- **Algorithm Efficiency**: Improved minimax algorithm with better pruning

### Code Quality
- **Type Hints**: Added comprehensive type annotations throughout the codebase
- **Error Handling**: Improved error handling and validation
- **Documentation**: Enhanced docstrings and code comments
- **Code Structure**: Better separation of concerns and modular design

### Security Enhancements
- **Latest Django**: Updated to Django 5.3 with latest security patches
- **Security Headers**: Added comprehensive security headers
- **Input Validation**: Enhanced input validation and sanitization
- **CSRF Protection**: Proper CSRF protection implementation

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project uses PEP 8 style guidelines. You can check code style with:
```bash
pycodestyle game/
```

### Adding New Features
1. Create a feature branch
2. Implement your changes
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## Deployment

### Heroku Deployment
The project is configured for Heroku deployment with:
- `Procfile` for process management
- `runtime.txt` for Python version specification
- `django-heroku` for Heroku-specific settings

### Production Settings
For production deployment:
1. Set `DEBUG=False`
2. Configure proper `SECRET_KEY`
3. Set up production database
4. Configure static file serving
5. Set up proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django framework and community
- Numpy for efficient numerical operations
- Socket.IO for real-time communication

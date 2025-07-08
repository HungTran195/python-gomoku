# FastAPI Gomoku Game

A modern, high-performance Gomoku (Five in a Row) game built with **FastAPI** and optimized game logic.

## 🚀 **New in FastAPI Version**

- **FastAPI Backend**: Modern, fast, async web framework
- **Automatic API Documentation**: Interactive docs at `/docs`
- **WebSocket Support**: Real-time communication with Socket.IO
- **Type Safety**: Full Pydantic validation and type hints
- **Async Performance**: Non-blocking I/O for better scalability
- **OpenAPI Specification**: Standard API documentation

## Features

- **FastAPI 0.104.1**: Modern async web framework with automatic API docs
- **Optimized Game Logic**: Enhanced minimax algorithm with alpha-beta pruning and numpy optimization
- **Real-time Gameplay**: WebSocket-based real-time game updates with Socket.IO
- **AI Opponent**: Intelligent AI using minimax algorithm with depth-limited search
- **Player vs Player**: Support for both single-player (vs AI) and multiplayer modes
- **Responsive UI**: Modern, responsive web interface
- **Type Safety**: Full type hints and Pydantic validation
- **API Documentation**: Automatic OpenAPI/Swagger documentation

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

### Quick Installation

#### Unix/Linux/macOS
```bash
./install_fastapi.sh
```

#### Windows
```cmd
install_fastapi.bat
```

### Manual Installation

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

5. **Start the development server**
   ```bash
   python main.py
   ```

6. **Access the game**
   - Game: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

## Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

### Game Settings
Game configuration can be modified in `config.py`:

```python
# Board size
number_of_row = 15
number_of_col = 15

# Game types
game_type_single = 'single'
game_type_pvp = 'pvp'

# AI configuration
ai_id = 'AI_0'
```

## API Endpoints

### Web Interface
- `GET /` - Main game interface
- `GET /health` - Health check endpoint
- `GET /api/games` - Get active games information

### WebSocket
- `WebSocket /ws` - WebSocket endpoint for Socket.IO

### Automatic Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `GET /openapi.json` - OpenAPI specification

## Game Rules

- Players take turns placing stones on a 15x15 grid
- First player to get 5 stones in a row (horizontally, vertically, or diagonally) wins
- The game supports both single-player (vs AI) and two-player modes
- AI uses minimax algorithm with alpha-beta pruning for intelligent gameplay

## Technical Improvements

### Performance Optimizations
- **FastAPI**: 2-3x faster than Django for API endpoints
- **Async Support**: Non-blocking I/O for better concurrency
- **Numpy Arrays**: Faster board operations and memory efficiency
- **Vectorized Operations**: Used numpy's vectorized operations for win detection
- **Memory Management**: Optimized memory usage with efficient data structures
- **Algorithm Efficiency**: Improved minimax algorithm with better pruning

### Code Quality
- **Type Hints**: Added comprehensive type annotations throughout the codebase
- **Pydantic Validation**: Automatic request/response validation
- **Error Handling**: Improved error handling and validation
- **Documentation**: Enhanced docstrings and code comments
- **Code Structure**: Better separation of concerns and modular design

### Security Enhancements
- **FastAPI Security**: Built-in security features and validation
- **Input Validation**: Automatic request validation with Pydantic
- **CORS Support**: Configurable CORS middleware
- **Type Safety**: Reduced runtime errors with compile-time checks

## Development

### Running Tests
```bash
python test_optimizations.py
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

### Production Deployment
For production deployment:
1. Set `DEBUG=False`
2. Configure proper `SECRET_KEY`
3. Set up production ASGI server (Gunicorn + Uvicorn)
4. Configure reverse proxy (Nginx)
5. Set up proper logging

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
```

### Heroku Deployment
The project can be deployed to Heroku with:
- `Procfile` for process management
- `runtime.txt` for Python version specification
- Environment variables for configuration

## FastAPI vs Django Comparison

| Feature | Django | FastAPI |
|---------|--------|---------|
| **Performance** | Good | Excellent (2-3x faster) |
| **Async Support** | Limited | Full async/await |
| **API Documentation** | Manual | Automatic (OpenAPI) |
| **Type Safety** | Optional | Built-in (Pydantic) |
| **Learning Curve** | Steep | Gentle |
| **Ecosystem** | Mature | Growing |
| **Real-time** | Requires Django Channels | Native WebSocket support |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI framework and community
- Django framework (original inspiration)
- Numpy for efficient numerical operations
- Socket.IO for real-time communication
- Pydantic for data validation

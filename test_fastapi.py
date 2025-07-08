#!/usr/bin/env python3
"""
Test script to verify FastAPI migration and functionality
"""

import asyncio
import json
import time
from typing import Dict, Any
import numpy as np

# Import FastAPI components
try:
    from fastapi.testclient import TestClient
    from main import app, socket_app
    from config import settings
    from game.game import Game
    from game.minimax import generate_next_move
    print("✅ FastAPI imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install FastAPI dependencies: pip install -r requirements.txt")
    exit(1)

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration...")
    
    assert settings.number_of_row == 15, f"Expected 15, got {settings.number_of_row}"
    assert settings.number_of_col == 15, f"Expected 15, got {settings.number_of_col}"
    assert settings.game_type_single == 'single', f"Expected 'single', got {settings.game_type_single}"
    assert settings.game_type_pvp == 'pvp', f"Expected 'pvp', got {settings.game_type_pvp}"
    
    print("✅ Configuration tests passed")

def test_game_logic():
    """Test game logic with new config"""
    print("\n🧪 Testing Game Logic...")
    
    # Test game creation
    game = Game(game_id=1, game_type='single')
    assert game.game_id == 1
    assert game.game_type == 'single'
    assert isinstance(game.game_board, np.ndarray)
    assert game.game_board.shape == (15, 15)
    
    # Test player addition
    game.add_player("player1", "Player 1")
    game.add_player("player2", "Player 2")
    assert len(game.player_id) == 2
    assert game.player_names == ["Player 1", "Player 2"]
    
    # Test move processing
    assert game.process_move("player1", (7, 7)) == True
    assert game.game_board[7, 7] == 1
    assert game.current_turn == 2
    
    print("✅ Game logic tests passed")

def test_minimax():
    """Test minimax algorithm"""
    print("\n🧪 Testing Minimax Algorithm...")
    
    # Create test game
    game = Game(game_id=1, game_type='single')
    game.add_player("player1", "Player 1")
    
    # Make a move
    game.process_move("player1", (7, 7))
    
    # Test AI move generation
    ai_move = generate_next_move(game, (7, 7))
    assert ai_move is not None
    assert isinstance(ai_move, tuple)
    assert len(ai_move) == 2
    
    print("✅ Minimax tests passed")

def test_fastapi_routes():
    """Test FastAPI routes"""
    print("\n🧪 Testing FastAPI Routes...")
    
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    
    # Test games endpoint
    response = client.get("/api/games")
    assert response.status_code == 200
    data = response.json()
    assert "total_games" in data
    assert "games" in data
    
    print("✅ FastAPI routes tests passed")

def test_template_rendering():
    """Test template rendering"""
    print("\n🧪 Testing Template Rendering...")
    
    client = TestClient(app)
    
    # Test main page
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    # Check for key elements in the response
    content = response.text
    assert "Gomoku" in content
    assert "game-board" in content
    
    print("✅ Template rendering tests passed")

def test_socketio_integration():
    """Test Socket.IO integration"""
    print("\n🧪 Testing Socket.IO Integration...")
    
    # Test that Socket.IO app is properly configured
    assert hasattr(socket_app, 'app')
    assert hasattr(socket_app, 'socketio_server')
    
    print("✅ Socket.IO integration tests passed")

def test_performance():
    """Test performance improvements"""
    print("\n🧪 Testing Performance...")
    
    # Test multiple game creations
    start_time = time.time()
    games = []
    
    for i in range(10):
        game = Game(game_id=i, game_type='single')
        game.add_player(f"player{i}", f"Player {i}")
        games.append(game)
    
    creation_time = time.time() - start_time
    print(f"  Created 10 games in {creation_time:.4f} seconds")
    
    # Test move processing performance
    start_time = time.time()
    for game in games:
        game.process_move(f"player{game.game_id}", (7, 7))
    
    move_time = time.time() - start_time
    print(f"  Processed moves in {move_time:.4f} seconds")
    
    assert creation_time < 1.0, f"Game creation too slow: {creation_time}s"
    assert move_time < 1.0, f"Move processing too slow: {move_time}s"
    
    print("✅ Performance tests passed")

def main():
    """Run all tests"""
    print("🚀 Starting FastAPI Migration Tests...\n")
    
    try:
        test_config()
        test_game_logic()
        test_minimax()
        test_fastapi_routes()
        test_template_rendering()
        test_socketio_integration()
        test_performance()
        
        print("\n🎉 All FastAPI migration tests passed!")
        print("\nKey Improvements:")
        print("  • FastAPI framework with async support")
        print("  • Pydantic configuration management")
        print("  • Automatic API documentation")
        print("  • Improved performance and type safety")
        print("  • Socket.IO integration with FastAPI")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
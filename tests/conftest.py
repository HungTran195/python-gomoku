"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from game.game import Game
from config import settings


@pytest.fixture
def sample_game():
    """Create a sample game for testing"""
    game = Game(game_id=12345, game_type=settings.game_type_pvp)
    game.add_player("player1_sid", "Player 1")
    game.add_player("player2_sid", "Player 2")
    return game


@pytest.fixture
def empty_game():
    """Create an empty game for testing"""
    return Game(game_id=12345, game_type=settings.game_type_single)


@pytest.fixture
def winning_game_horizontal():
    """Create a game with a horizontal winning line setup"""
    game = Game(game_id=12345, game_type=settings.game_type_pvp)
    game.add_player("player1_sid", "Player 1")
    game.add_player("player2_sid", "Player 2")
    
    # Set up horizontal winning scenario for player 1
    moves = [(7, 7), (8, 8), (7, 8), (8, 9), (7, 9), (8, 10), (7, 10)]
    for i, move in enumerate(moves):
        player_id = "player1_sid" if i % 2 == 0 else "player2_sid"
        game.process_move(player_id, move)
    
    return game


@pytest.fixture
def winning_game_vertical():
    """Create a game with a vertical winning line setup"""
    game = Game(game_id=12345, game_type=settings.game_type_pvp)
    game.add_player("player1_sid", "Player 1")
    game.add_player("player2_sid", "Player 2")
    
    # Set up vertical winning scenario for player 1
    moves = [(7, 7), (7, 8), (8, 7), (8, 8), (9, 7), (9, 8), (10, 7)]
    for i, move in enumerate(moves):
        player_id = "player1_sid" if i % 2 == 0 else "player2_sid"
        game.process_move(player_id, move)
    
    return game 
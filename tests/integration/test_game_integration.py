"""
Integration tests for the Game class
Testing complete game scenarios and interactions
"""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from game.game import Game
from game.minimax import generate_next_move
from config import settings


class TestGameIntegration(unittest.TestCase):
    """Integration tests for complete game scenarios"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.game = Game(game_id=12345, game_type=settings.game_type_pvp)
        self.player1_id = "player1_sid"
        self.player2_id = "player2_id"
        
        self.game.add_player(self.player1_id, "Player 1")
        self.game.add_player(self.player2_id, "Player 2")

    def test_complete_game_winning_scenario(self):
        """Test a complete game from start to finish with a winner"""
        # Simulate a complete game where player 1 wins
        moves = [
            (self.player1_id, (7, 7)),   # Player 1 center
            (self.player2_id, (8, 8)),   # Player 2 diagonal
            (self.player1_id, (7, 8)),   # Player 1 horizontal
            (self.player2_id, (8, 9)),   # Player 2 diagonal
            (self.player1_id, (7, 9)),   # Player 1 horizontal
            (self.player2_id, (8, 10)),  # Player 2 diagonal
            (self.player1_id, (7, 10)),  # Player 1 horizontal
            (self.player2_id, (8, 11)),  # Player 2 diagonal
            (self.player1_id, (7, 11)),  # Player 1 wins!
        ]
        
        for i, (player_id, move) in enumerate(moves):
            result = self.game.process_move(player_id, move)
            self.assertTrue(result, f"Move {i+1} failed: {move}")
            
            if i == len(moves) - 1:  # Last move
                self.assertTrue(self.game.game_over)
                self.assertEqual(len(self.game.winning_line), 5)
                self.assertTrue(all(pos in self.game.winning_line for pos in [(7, 7), (7, 8), (7, 9), (7, 10), (7, 11)]))

    def test_game_with_ai_integration(self):
        """Test game integration with AI moves"""
        # Create a single player game
        ai_game = Game(game_id=12346, game_type=settings.game_type_single)
        ai_game.add_player(self.player1_id, "Player 1")
        ai_game.add_player(settings.ai_id, "Computer")
        
        # Player makes first move
        result = ai_game.process_move(self.player1_id, (7, 7))
        self.assertTrue(result)
        
        # AI should make a move
        ai_move = generate_next_move(ai_game, (7, 7))
        self.assertIsNotNone(ai_move)
        
        # Process AI move
        if ai_move is not None:
            result = ai_game.process_move(settings.ai_id, ai_move)
            self.assertTrue(result)
            
            # Check that AI move was recorded
            self.assertEqual(ai_game.game_board[ai_move[0], ai_move[1]], 2)

    def test_rematch_functionality(self):
        """Test complete rematch functionality"""
        # Play a game to completion
        moves = [
            (self.player1_id, (7, 7)), (self.player2_id, (8, 8)),
            (self.player1_id, (7, 8)), (self.player2_id, (8, 9)),
            (self.player1_id, (7, 9)), (self.player2_id, (8, 10)),
            (self.player1_id, (7, 10)), (self.player2_id, (8, 11)),
            (self.player1_id, (7, 11)),  # Player 1 wins
        ]
        
        for player_id, move in moves:
            self.game.process_move(player_id, move)
        
        # Verify game is over
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.number_of_games, 1)
        
        # Start rematch
        self.game.rematch()
        
        # Verify game state is reset
        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.current_turn, 1)
        self.assertEqual(self.game.number_of_moves, 0)
        self.assertEqual(len(self.game.winning_line), 0)
        self.assertEqual(self.game.number_of_games, 2)
        
        # Verify board is cleared
        self.assertTrue(np.all(self.game.game_board == 0))

    def test_multiple_games_same_instance(self):
        """Test playing multiple games with the same game instance"""
        # First game
        moves1 = [
            (self.player1_id, (7, 7)), (self.player2_id, (8, 8)),
            (self.player1_id, (7, 8)), (self.player2_id, (8, 9)),
            (self.player1_id, (7, 9)), (self.player2_id, (8, 10)),
            (self.player1_id, (7, 10)), (self.player2_id, (8, 11)),
            (self.player1_id, (7, 11)),  # Player 1 wins
        ]
        
        for player_id, move in moves1:
            self.game.process_move(player_id, move)
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.number_of_games, 1)
        
        # Rematch
        self.game.rematch()
        
        # Second game - different pattern
        moves2 = [
            (self.player2_id, (0, 0)), (self.player1_id, (1, 1)),
            (self.player2_id, (0, 1)), (self.player1_id, (1, 2)),
            (self.player2_id, (0, 2)), (self.player1_id, (1, 3)),
            (self.player2_id, (0, 3)), (self.player1_id, (1, 4)),
            (self.player2_id, (0, 4)),  # Player 2 wins
        ]
        
        for player_id, move in moves2:
            self.game.process_move(player_id, move)
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.number_of_games, 2)

    def test_game_state_consistency(self):
        """Test that game state remains consistent throughout a game"""
        # Track game state at each move
        states = []
        
        moves = [
            (self.player1_id, (7, 7)), (self.player2_id, (8, 8)),
            (self.player1_id, (7, 8)), (self.player2_id, (8, 9)),
            (self.player1_id, (7, 9)), (self.player2_id, (8, 10)),
        ]
        
        for player_id, move in moves:
            # Record state before move
            state_before = {
                'current_turn': self.game.current_turn,
                'number_of_moves': self.game.number_of_moves,
                'game_over': self.game.game_over,
                'board_sum': np.sum(self.game.game_board)
            }
            
            # Make move
            result = self.game.process_move(player_id, move)
            self.assertTrue(result)
            
            # Record state after move
            state_after = {
                'current_turn': self.game.current_turn,
                'number_of_moves': self.game.number_of_moves,
                'game_over': self.game.game_over,
                'board_sum': np.sum(self.game.game_board)
            }
            
            states.append((state_before, state_after))
        
        # Verify state consistency
        for i, (before, after) in enumerate(states):
            # Turn should switch
            self.assertNotEqual(before['current_turn'], after['current_turn'])
            
            # Move count should increase
            self.assertEqual(after['number_of_moves'], before['number_of_moves'] + 1)
            
            # Board sum should increase by player value
            expected_increase = 1 if i % 2 == 0 else 2  # Player 1 = 1, Player 2 = 2
            self.assertEqual(after['board_sum'], before['board_sum'] + expected_increase)

    def test_edge_case_corner_winning(self):
        """Test winning scenario starting from corner"""
        # Create winning scenario from top-left corner
        moves = [
            (self.player1_id, (0, 0)), (self.player2_id, (1, 1)),
            (self.player1_id, (0, 1)), (self.player2_id, (2, 2)),
            (self.player1_id, (0, 2)), (self.player2_id, (3, 3)),
            (self.player1_id, (0, 3)), (self.player2_id, (4, 4)),
            (self.player1_id, (0, 4)),  # Player 1 wins horizontally from corner
        ]
        
        for player_id, move in moves:
            result = self.game.process_move(player_id, move)
            self.assertTrue(result)
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(len(self.game.winning_line), 5)
        self.assertTrue(all(pos in self.game.winning_line for pos in [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]))

    def test_game_status_method(self):
        """Test the get_game_status method"""
        # Make some moves
        self.game.process_move(self.player1_id, (7, 7))
        self.game.process_move(self.player2_id, (8, 8))
        
        status = self.game.get_game_status()
        
        # Verify status structure
        self.assertIn('game_over', status)
        self.assertIn('current_turn', status)
        self.assertIn('number_of_moves', status)
        self.assertIn('winning_line', status)
        self.assertIn('board', status)
        
        # Verify values
        self.assertFalse(status['game_over'])
        self.assertEqual(status['current_turn'], 1)
        self.assertEqual(status['number_of_moves'], 2)
        self.assertEqual(len(status['winning_line']), 0)
        self.assertEqual(len(status['board']), 15)  # 15x15 board


if __name__ == '__main__':
    unittest.main() 
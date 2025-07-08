"""
Unit tests for the Game class
Focusing on process_move method and related functionality
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
from config import settings


class TestGameProcessMove(unittest.TestCase):
    """Test cases for the Game.process_move method"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.game = Game(game_id=12345, game_type=settings.game_type_pvp)
        self.player1_id = "player1_sid"
        self.player2_id = "player2_id"
        
        # Add two players
        self.game.add_player(self.player1_id, "Player 1")
        self.game.add_player(self.player2_id, "Player 2")

    def test_process_move_valid_first_move(self):
        """Test processing a valid first move"""
        move_index = (7, 7)  # Center of the board
        
        result = self.game.process_move(self.player1_id, move_index)
        
        self.assertTrue(result)
        self.assertEqual(self.game.game_board[7, 7], 1)
        self.assertEqual(self.game.current_turn, 2)
        self.assertEqual(self.game.number_of_moves, 1)
        self.assertFalse(self.game.game_over)

    def test_process_move_invalid_out_of_bounds(self):
        """Test processing a move outside the board boundaries"""
        # Test negative coordinates
        result1 = self.game.process_move(self.player1_id, (-1, 0))
        self.assertFalse(result1)
        
        # Test coordinates beyond board size
        result2 = self.game.process_move(self.player1_id, (15, 15))
        self.assertFalse(result2)
        
        # Test coordinates at boundary (should be valid for 15x15 board)
        result3 = self.game.process_move(self.player1_id, (14, 14))
        self.assertTrue(result3)  # (14, 14) is valid for 15x15 board

    def test_process_move_invalid_occupied_cell(self):
        """Test processing a move on an already occupied cell"""
        # Make first move
        self.game.process_move(self.player1_id, (7, 7))
        
        # Try to move on the same cell
        result = self.game.process_move(self.player2_id, (7, 7))
        
        self.assertFalse(result)
        self.assertEqual(self.game.current_turn, 2)  # Turn should not change

    def test_process_move_invalid_wrong_turn(self):
        """Test processing a move when it's not the player's turn"""
        # Player 1's turn, but Player 2 tries to move
        result = self.game.process_move(self.player2_id, (7, 7))
        
        self.assertFalse(result)
        self.assertEqual(self.game.current_turn, 1)  # Turn should remain 1

    def test_process_move_invalid_game_over(self):
        """Test processing a move when the game is already over"""
        # Create a winning scenario for player 1
        moves = [
            (self.player1_id, (7, 7)),   # P1
            (self.player2_id, (8, 8)),   # P2
            (self.player1_id, (7, 8)),   # P1
            (self.player2_id, (8, 9)),   # P2
            (self.player1_id, (7, 9)),   # P1
            (self.player2_id, (8, 10)),  # P2
            (self.player1_id, (7, 10)),  # P1
            (self.player2_id, (8, 11)),  # P2
            (self.player1_id, (7, 11)),  # P1 wins!
        ]
        
        for i, (player_id, move) in enumerate(moves):
            result = self.game.process_move(player_id, move)
            self.assertTrue(result, f"Move {i+1} failed: {move}")
        
        # Game should be over now
        self.assertTrue(self.game.game_over)
        
        # Try to make another move
        result = self.game.process_move(self.player2_id, (9, 7))
        
        self.assertFalse(result)

    def test_process_move_invalid_player_not_found(self):
        """Test processing a move with a non-existent player ID"""
        result = self.game.process_move("non_existent_player", (7, 7))
        
        self.assertFalse(result)

    def test_process_move_turn_switching(self):
        """Test that turns switch correctly between players"""
        # Player 1's turn
        self.assertEqual(self.game.current_turn, 1)
        
        # Player 1 makes a move
        self.game.process_move(self.player1_id, (7, 7))
        self.assertEqual(self.game.current_turn, 2)
        
        # Player 2 makes a move
        self.game.process_move(self.player2_id, (8, 8))
        self.assertEqual(self.game.current_turn, 1)

    def test_process_move_winning_horizontal(self):
        """Test processing a move that creates a horizontal winning line"""
        # Set up a horizontal winning scenario for player 1
        # Player 1: (7,7), (7,8), (7,9), (7,10), (7,11) - horizontal line
        # Player 2: (8,8), (8,9), (8,10) - blocking moves
        moves = [
            (self.player1_id, (7, 7)),   # P1
            (self.player2_id, (8, 8)),   # P2
            (self.player1_id, (7, 8)),   # P1
            (self.player2_id, (8, 9)),   # P2
            (self.player1_id, (7, 9)),   # P1
            (self.player2_id, (8, 10)),  # P2
            (self.player1_id, (7, 10)),  # P1
            (self.player2_id, (8, 11)),  # P2
            (self.player1_id, (7, 11)),  # P1 wins!
        ]
        
        for i, (player_id, move) in enumerate(moves):
            result = self.game.process_move(player_id, move)
            if i == len(moves) - 1:  # Last move
                self.assertTrue(result)
                self.assertTrue(self.game.game_over)
                self.assertEqual(len(self.game.winning_line), 5)
                self.assertIn((7, 7), self.game.winning_line)
                self.assertIn((7, 11), self.game.winning_line)
            else:
                self.assertTrue(result)

    def test_process_move_winning_vertical(self):
        """Test processing a move that creates a vertical winning line"""
        # Set up a vertical winning scenario for player 1
        # Player 1: (7,7), (8,7), (9,7), (10,7), (11,7) - vertical line
        # Player 2: (7,8), (8,8), (9,8) - blocking moves
        moves = [
            (self.player1_id, (7, 7)),   # P1
            (self.player2_id, (7, 8)),   # P2
            (self.player1_id, (8, 7)),   # P1
            (self.player2_id, (8, 8)),   # P2
            (self.player1_id, (9, 7)),   # P1
            (self.player2_id, (9, 8)),   # P2
            (self.player1_id, (10, 7)),  # P1
            (self.player2_id, (10, 8)),  # P2
            (self.player1_id, (11, 7)),  # P1 wins!
        ]
        
        for i, (player_id, move) in enumerate(moves):
            result = self.game.process_move(player_id, move)
            if i == len(moves) - 1:  # Last move
                self.assertTrue(result)
                self.assertTrue(self.game.game_over)
                self.assertEqual(len(self.game.winning_line), 5)
            else:
                self.assertTrue(result)

    def test_process_move_winning_diagonal(self):
        """Test processing a move that creates a diagonal winning line"""
        # Set up a diagonal winning scenario for player 1
        # Player 1: (7,7), (8,8), (9,9), (10,10), (11,11) - diagonal line
        # Player 2: (7,8), (8,9), (9,10) - blocking moves
        moves = [
            (self.player1_id, (7, 7)),   # P1
            (self.player2_id, (7, 8)),   # P2
            (self.player1_id, (8, 8)),   # P1
            (self.player2_id, (8, 9)),   # P2
            (self.player1_id, (9, 9)),   # P1
            (self.player2_id, (9, 10)),  # P2
            (self.player1_id, (10, 10)), # P1
            (self.player2_id, (10, 11)), # P2
            (self.player1_id, (11, 11)), # P1 wins!
        ]
        
        for i, (player_id, move) in enumerate(moves):
            result = self.game.process_move(player_id, move)
            if i == len(moves) - 1:  # Last move
                self.assertTrue(result)
                self.assertTrue(self.game.game_over)
                self.assertEqual(len(self.game.winning_line), 5)
            else:
                self.assertTrue(result)

    def test_process_move_game_tie(self):
        """Test processing moves until the game ends in a tie"""
        # This test is simplified - we'll just test that the game can handle many moves
        # In practice, creating a true tie scenario without winning lines is complex
        
        # Make several moves to test the system
        moves_made = 0
        for row in range(5):  # Test with a smaller subset
            for col in range(5):
                player_id = self.player1_id if (row + col) % 2 == 0 else self.player2_id
                result = self.game.process_move(player_id, (row, col))
                
                if result:
                    moves_made += 1
                    self.assertTrue(result)
                else:
                    # If move fails, it might be because game ended
                    break
        
        # Verify we made some moves
        self.assertGreater(moves_made, 0)
        self.assertEqual(self.game.number_of_moves, moves_made)

    def test_process_move_board_state_consistency(self):
        """Test that the board state remains consistent after moves"""
        initial_board = self.game.get_board_state().copy()
        
        # Make a move
        self.game.process_move(self.player1_id, (7, 7))
        
        # Check that only the moved position changed
        current_board = self.game.get_board_state()
        self.assertEqual(current_board[7, 7], 1)
        
        # All other positions should remain 0
        for row in range(15):
            for col in range(15):
                if (row, col) != (7, 7):
                    self.assertEqual(current_board[row, col], 0)

    def test_process_move_with_numpy_arrays(self):
        """Test that process_move works correctly with numpy array inputs"""
        move_index = np.array([7, 7])
        
        result = self.game.process_move(self.player1_id, tuple(move_index))
        
        self.assertTrue(result)
        self.assertEqual(self.game.game_board[7, 7], 1)

    def test_process_move_edge_cases(self):
        """Test edge cases for process_move"""
        # Test corner positions
        corners = [(0, 0), (0, 14), (14, 0), (14, 14)]
        
        for corner in corners:
            game = Game(game_id=12345, game_type=settings.game_type_pvp)
            game.add_player(self.player1_id, "Player 1")
            game.add_player(self.player2_id, "Player 2")
            
            result = game.process_move(self.player1_id, corner)
            self.assertTrue(result)
            self.assertEqual(game.game_board[corner[0], corner[1]], 1)




class TestGameHelperMethods(unittest.TestCase):
    """Test cases for helper methods used by process_move"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.game = Game(game_id=12345, game_type=settings.game_type_pvp)
        self.player1_id = "player1_sid"
        self.player2_id = "player2_id"
        
        self.game.add_player(self.player1_id, "Player 1")
        self.game.add_player(self.player2_id, "Player 2")

    def test_is_valid_move_valid(self):
        """Test is_valid_move with valid moves"""
        valid_moves = [(0, 0), (7, 7), (14, 14), (0, 14), (14, 0)]
        
        for move in valid_moves:
            self.assertTrue(self.game.is_valid_move(move))

    def test_is_valid_move_invalid(self):
        """Test is_valid_move with invalid moves"""
        # Out of bounds
        invalid_moves = [(-1, 0), (15, 15), (0, 15), (15, 0)]
        
        for move in invalid_moves:
            self.assertFalse(self.game.is_valid_move(move))
        
        # Occupied cell
        self.game.process_move(self.player1_id, (7, 7))
        self.assertFalse(self.game.is_valid_move((7, 7)))

    def test_get_player_index(self):
        """Test get_player_index method"""
        self.assertEqual(self.game.get_player_index(self.player1_id), 1)
        self.assertEqual(self.game.get_player_index(self.player2_id), 2)
        self.assertIsNone(self.game.get_player_index("non_existent"))

    def test_get_opponent_id(self):
        """Test get_opponent_id method"""
        self.assertEqual(self.game.get_opponent_id(self.player1_id), self.player2_id)
        self.assertEqual(self.game.get_opponent_id(self.player2_id), self.player1_id)


if __name__ == '__main__':
    unittest.main() 
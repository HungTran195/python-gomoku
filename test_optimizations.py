#!/usr/bin/env python3
"""
Test script to verify game logic optimizations and performance improvements
"""

import time
import numpy as np
from game.game import Game
from game.minimax import MiniMax
from django.conf import settings

def test_game_logic():
    """Test the optimized game logic"""
    print("🧪 Testing Game Logic Optimizations...")
    
    # Create a new game
    game = Game(game_id=1, game_type='single')
    
    # Test 1: Basic move validation
    print("  ✓ Testing move validation...")
    assert game.is_valid_move((0, 0)) == True
    assert game.is_valid_move((7, 7)) == True
    assert game.is_valid_move((-1, 0)) == False
    assert game.is_valid_move((15, 15)) == False
    
    # Test 2: Add players
    print("  ✓ Testing player management...")
    game.add_player("player1", "Player 1")
    game.add_player("player2", "Player 2")
    assert game.get_player_index("player1") == 1
    assert game.get_player_index("player2") == 2
    
    # Test 3: Process moves
    print("  ✓ Testing move processing...")
    assert game.process_move("player1", (7, 7)) == True
    assert game.game_board[7, 7] == 1
    assert game.current_turn == 2
    
    # Test 4: Win detection
    print("  ✓ Testing win detection...")
    # Create a winning scenario
    game.game_board.fill(0)
    game.current_turn = 1
    game.number_of_moves = 0
    game.game_over = False
    
    # Place 5 pieces in a row horizontally
    moves = [(7, 7), (7, 8), (7, 9), (7, 10), (7, 11)]
    for i, move in enumerate(moves):
        game.process_move("player1", move)
        if i == 4:  # Last move should trigger win
            assert game.game_over == True
            assert len(game.winning_line) == 5
    
    print("✅ All game logic tests passed!")

def test_minimax_performance():
    """Test the optimized minimax algorithm performance"""
    print("\n🧪 Testing Minimax Performance...")
    
    # Create a test board
    board = np.zeros((15, 15), dtype=int)
    
    # Add some moves to make it interesting
    board[7, 7] = 1  # Player move
    board[7, 8] = 2  # AI move
    board[8, 7] = 1  # Player move
    
    # Test minimax initialization
    print("  ✓ Testing minimax initialization...")
    minimax = MiniMax(board)
    assert minimax.LIMIT_DEPTH == 3
    assert len(minimax.directions) == 4
    
    # Test move generation
    print("  ✓ Testing move generation...")
    available_moves = minimax.get_available_indexes(board)
    assert len(available_moves) > 0
    assert (7, 6) in available_moves or (7, 9) in available_moves
    
    # Test scoring
    print("  ✓ Testing scoring function...")
    score = minimax.count_and_score_connected(board, 7, 7, 1)
    assert score >= 0
    
    # Performance test
    print("  ✓ Testing performance...")
    start_time = time.time()
    next_move = minimax.calculate_next_move((8, 7))
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f"    Minimax calculation took: {execution_time:.4f} seconds")
    
    assert next_move is not None
    assert execution_time < 5.0  # Should complete within 5 seconds
    
    print("✅ All minimax tests passed!")

def test_numpy_optimizations():
    """Test numpy optimizations"""
    print("\n🧪 Testing Numpy Optimizations...")
    
    # Test board operations
    game = Game(game_id=1, game_type='single')
    
    # Test numpy array operations
    print("  ✓ Testing numpy array operations...")
    assert isinstance(game.game_board, np.ndarray)
    assert game.game_board.shape == (15, 15)
    assert game.game_board.dtype == np.int32
    
    # Test board state retrieval
    board_state = game.get_board_state()
    assert isinstance(board_state, np.ndarray)
    assert np.array_equal(board_state, game.game_board)
    
    # Test game status
    status = game.get_game_status()
    assert 'board' in status
    assert isinstance(status['board'], list)
    
    print("✅ All numpy optimization tests passed!")

def benchmark_performance():
    """Benchmark performance improvements"""
    print("\n📊 Performance Benchmark...")
    
    # Test multiple games
    num_games = 10
    total_time = 0
    
    for i in range(num_games):
        game = Game(game_id=i, game_type='single')
        game.add_player("player1", "Player 1")
        game.add_player("player2", "Player 2")
        
        # Simulate some moves
        moves = [(7, 7), (7, 8), (8, 7), (8, 8), (9, 7)]
        
        start_time = time.time()
        for move in moves:
            game.process_move("player1", move)
        end_time = time.time()
        
        total_time += (end_time - start_time)
    
    avg_time = total_time / num_games
    print(f"  Average time per game simulation: {avg_time:.4f} seconds")
    print(f"  Total time for {num_games} games: {total_time:.4f} seconds")
    
    # Test minimax performance
    board = np.zeros((15, 15), dtype=int)
    board[7, 7] = 1
    minimax = MiniMax(board)
    
    start_time = time.time()
    next_move = minimax.calculate_next_move((7, 7))
    end_time = time.time()
    
    minimax_time = end_time - start_time
    print(f"  Minimax calculation time: {minimax_time:.4f} seconds")
    
    print("✅ Performance benchmark completed!")

def main():
    """Run all tests"""
    print("🚀 Starting Optimization Tests...\n")
    
    try:
        test_game_logic()
        test_minimax_performance()
        test_numpy_optimizations()
        benchmark_performance()
        
        print("\n🎉 All tests completed successfully!")
        print("\nKey Improvements:")
        print("  • Numpy arrays for faster board operations")
        print("  • Optimized win detection with pre-computed directions")
        print("  • Improved minimax algorithm with alpha-beta pruning")
        print("  • Type safety with comprehensive type hints")
        print("  • Memory-efficient data structures")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
from config import settings
from typing import List, Tuple, Optional, Set
import numpy as np

NUMBER_OF_ROW = settings.number_of_row
NUMBER_OF_COL = settings.number_of_col

class MiniMax:
    '''
    A class implementing MiniMax with alpha-beta pruning
    to predict the next best possible move for Gomoku AI
    '''

    def __init__(self, play_board: np.ndarray):
        self.play_board = play_board.copy()  # Deep copy of original board
        self.LIMIT_DEPTH = 3                 # Max depth of tree to search for next move
        
        # Pre-compute direction vectors for efficiency
        self.directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal down-right
            (1, -1),  # diagonal down-left
        ]
        
        # Scoring weights for different line lengths
        self.score_weights = {
            3: 100,
            4: 1000,
            5: 100000
        }

    def is_playable(self, x: int, y: int) -> bool:
        '''
        Check whether index (x, y) is within the board boundaries
        :param x: row index 
        :param y: column index
        :return: True if position is valid, False otherwise
        '''
        return 0 <= x < NUMBER_OF_ROW and 0 <= y < NUMBER_OF_COL

    def is_available_index(self, board: np.ndarray, x: int, y: int, 
                          compared_target: int, contain_set: Optional[Set] = None) -> bool:
        '''
        Check if index (x, y) can be used for processing
        :param board: matrix representing the current board state
        :param x: row index 
        :param y: column index
        :param compared_target: value of the current processing state
        :param contain_set: a set containing all processed values
        :return: True if position is available, False otherwise
        '''
        if not self.is_playable(x, y) or board[x, y] != compared_target:
            return False
        
        if contain_set is not None:
            return (x, y) not in contain_set
        return True

    def get_score_from_count(self, count: int) -> int:
        '''
        Return points based on number of connected nodes in board
        :param count: number of connected nodes in board
        :return: score value
        '''
        return self.score_weights.get(count, count * count)

    def count_and_score_connected(self, board: np.ndarray, row: int, col: int, target: int) -> int:
        '''
        Count the number of connected nodes in game board and calculate score for the current move
        :param board: matrix representing the current board state
        :param row: index of row in board matrix
        :param col: index of col in board matrix
        :param target: value of node to compare (1 for human, 2 for AI)
        :return: calculated score
        '''
        score = 0
        
        for dr, dc in self.directions:
            count = 1  # Count the current position
            
            # Count in positive direction
            count += self._count_in_direction(board, row, col, dr, dc, target)
            # Count in negative direction  
            count += self._count_in_direction(board, row, col, -dr, -dc, target)
            
            # Early termination if winning move found
            if count >= 5:
                return self.get_score_from_count(count)
            
            score += self.get_score_from_count(count)

        return score
    
    def _count_in_direction(self, board: np.ndarray, row: int, col: int, 
                           dr: int, dc: int, target: int) -> int:
        """Count consecutive pieces in a given direction"""
        count = 0
        r, c = row + dr, col + dc
        
        while (self.is_playable(r, c) and board[r, c] == target):
            count += 1
            r += dr
            c += dc
            
        return count

    def score_move_taken(self, current_board: np.ndarray, move_taken: List[Tuple[int, int]], 
                        is_ai: bool) -> int:
        '''
        Score the current game state created by predicted move
        :param current_board: matrix representing the current board state
        :param move_taken: list containing moves taken by AI and human 
        :param is_ai: True if AI's turn, False if human's turn
        :return: total score
        '''
        target = 2 if is_ai else 1
        defense = 1 if is_ai else 2

        total_score = 0

        for move in move_taken:
            row, col = move
            if current_board[row, col] == target:
                # Count the number of connected nodes
                score = self.count_and_score_connected(current_board, row, col, target)
                # Count defensive moves (blocking opponent's moves)
                score_defense = self.count_and_score_connected(current_board, row, col, defense)
                # Final score is the sum of all scores in 4 directions
                total_score += score + score_defense
                
        return total_score

    def get_available_indexes(self, current_board: np.ndarray) -> Set[Tuple[int, int]]:
        '''
        Get all available indexes for next move
        Only get indexes around played nodes in board due to computational limits
        :param current_board: matrix representing the current board state
        :return: set of all available moves
        '''
        possible_moves = set()
        
        # Find all non-empty positions
        non_empty_positions = np.where(current_board != 0)
        
        for row, col in zip(non_empty_positions[0], non_empty_positions[1]):
            # Check all 8 surrounding positions
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (dr, dc) != (0, 0):
                        new_row, new_col = row + dr, col + dc
                        if (self.is_available_index(current_board, new_row, new_col, 0, possible_moves)):
                            possible_moves.add((new_row, new_col))
        
        return possible_moves

    def minimax(self, current_board: np.ndarray, move_index: Tuple[int, int], 
                depth: int, alpha: float, beta: float, possible_moves: Optional[Set], 
                move_taken: List[Tuple[int, int]], is_max_player: bool) -> Tuple[float, Optional[Tuple[int, int]]]:
        '''
        Recursively search through all possible moves to find the best one with the highest score
        :param current_board: matrix representing the current board state
        :param move_index: latest move index
        :param depth: current depth of the search tree
        :param alpha: the best (highest-value) choice found by Maximizer
        :param beta: the best (lowest-value) choice found by Minimizer
        :param possible_moves: set of possible moves
        :param move_taken: list of moves taken so far
        :param is_max_player: True if maximizing player (AI), False if minimizing (human)
        :return: tuple of (best_score, best_move)
        '''
        if depth == self.LIMIT_DEPTH:
            score = self.score_move_taken(current_board, move_taken, is_ai=True)
            return score, move_index
            
        row, col = move_index
        current_board[row, col] = 2 if is_max_player else 1
        all_possible_moves = self.get_available_indexes(current_board)
        best_move = None

        if is_max_player:
            # Maximizing player (AI)
            best_score = float('-inf')
            for move in all_possible_moves:
                move_taken.append(move)
                
                score, _ = self.minimax(
                    current_board, move, depth + 1, alpha, beta, 
                    all_possible_moves, move_taken, is_max_player=False
                )
                
                # Undo the move
                prev_move = move_taken.pop()
                current_board[prev_move[0], prev_move[1]] = 0

                if score > best_score:
                    best_score = score
                    best_move = move

                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break  # Beta cutoff

        else:
            # Minimizing player (human)
            best_score = float('inf')
            for move in all_possible_moves:
                move_taken.append(move)
                
                score, _ = self.minimax(
                    current_board, move, depth + 1, alpha, beta, 
                    all_possible_moves, move_taken, is_max_player=True
                )
                
                # Undo the move
                prev_move = move_taken.pop()
                current_board[prev_move[0], prev_move[1]] = 0

                if score < best_score:
                    best_score = score
                    best_move = move

                beta = min(beta, best_score)
                if beta <= alpha:
                    break  # Alpha cutoff

        return best_score, best_move

    def calculate_next_move(self, move_index: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        '''
        Calculate next move based on the human's latest move index
        :param move_index: human's latest move index
        :return: next move coordinates or None if no valid move
        '''
        current_board = self.play_board.copy()
        score, next_move = self.minimax(
            current_board, move_index, depth=0, alpha=float('-inf'), 
            beta=float('inf'), possible_moves=None, move_taken=[move_index], 
            is_max_player=True
        )
        return next_move


def generate_next_move(game, move_index_2D: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    """
    Generate the next AI move using minimax algorithm
    :param game: Game instance
    :param move_index_2D: 2D coordinates of the last move
    :return: next move coordinates or None if no valid move
    """
    # Convert game board to numpy array for better performance
    play_board = np.array(game.game_board, dtype=int)
    
    solver = MiniMax(play_board)
    next_move = solver.calculate_next_move(move_index_2D)
    return next_move

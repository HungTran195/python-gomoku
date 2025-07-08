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
            2: 10,
            3: 100,
            4: 10000,    # Much higher for 4-in-a-row (immediate threat)
            5: 1000000   # Winning move gets highest priority
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

    def count_consecutive_with_openings(self, board: np.ndarray, row: int, col: int, 
                                      dr: int, dc: int, target: int) -> Tuple[int, bool, bool]:
        '''
        Count consecutive pieces in a direction and check if ends are open
        :param board: game board
        :param row: starting row
        :param col: starting column
        :param dr: row direction
        :param dc: column direction
        :param target: piece type to count
        :return: (count, left_open, right_open)
        '''
        count = 1  # Count the current position
        
        # Count in positive direction
        pos_count = 0
        r, c = row + dr, col + dc
        while self.is_playable(r, c) and board[r, c] == target:
            pos_count += 1
            r += dr
            c += dc
        right_open = self.is_playable(r, c) and board[r, c] == 0
        
        # Count in negative direction
        neg_count = 0
        r, c = row - dr, col - dc
        while self.is_playable(r, c) and board[r, c] == target:
            neg_count += 1
            r -= dr
            c -= dc
        left_open = self.is_playable(r, c) and board[r, c] == 0
        
        total_count = count + pos_count + neg_count
        return total_count, left_open, right_open

    def evaluate_line(self, board: np.ndarray, row: int, col: int, target: int) -> int:
        '''
        Evaluate a position for a specific player, considering line formations
        :param board: game board
        :param row: row position
        :param col: column position
        :param target: player (1 for human, 2 for AI)
        :return: evaluation score
        '''
        if board[row, col] != 0:
            return 0
            
        # Temporarily place the piece
        board[row, col] = target
        total_score = 0
        
        for dr, dc in self.directions:
            count, left_open, right_open = self.count_consecutive_with_openings(
                board, row, col, dr, dc, target
            )
            
            # Winning move gets maximum priority
            if count >= 5:
                board[row, col] = 0  # Undo temporary placement
                return 1000000
            
            # Score based on count and openings
            base_score = self.get_score_from_count(count)
            
            # Bonus for open lines (can extend in both directions)
            if left_open and right_open:
                base_score *= 2
            elif left_open or right_open:
                base_score *= 1.5
            
            # Special bonus for 4-in-a-row (immediate threat/opportunity)
            if count == 4:
                base_score *= 10
                
            total_score += base_score
        
        board[row, col] = 0  # Undo temporary placement
        return int(total_score)

    def evaluate_board_state(self, board: np.ndarray) -> int:
        '''
        Evaluate the entire board state from AI's perspective
        :param board: current board state
        :return: evaluation score (positive favors AI, negative favors human)
        '''
        possible_moves = self.get_available_indexes(board)
        
        ai_score = 0
        human_score = 0
        
        for row, col in possible_moves:
            # Evaluate this position for AI (target=2)
            ai_score += self.evaluate_line(board, row, col, 2)
            
            # Evaluate this position for human (target=1)
            human_score += self.evaluate_line(board, row, col, 1)
        
        # AI score is positive, human score reduces it
        # But give more weight to AI's offensive moves
        return ai_score * 1.2 - human_score

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
        
        # If board is empty, start from center
        if len(non_empty_positions[0]) == 0:
            center_row, center_col = NUMBER_OF_ROW // 2, NUMBER_OF_COL // 2
            return {(center_row, center_col)}
        
        for row, col in zip(non_empty_positions[0], non_empty_positions[1]):
            # Check all 8 surrounding positions
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (dr, dc) != (0, 0):
                        new_row, new_col = row + dr, col + dc
                        if (self.is_available_index(current_board, new_row, new_col, 0, possible_moves)):
                            possible_moves.add((new_row, new_col))
        
        return possible_moves

    def check_immediate_win_or_block(self, board: np.ndarray) -> Optional[Tuple[int, int]]:
        '''
        Check for immediate winning moves or critical blocking moves
        :param board: current board state
        :return: move coordinates if found, None otherwise
        '''
        possible_moves = self.get_available_indexes(board)
        
        # First check for winning moves for AI
        for row, col in possible_moves:
            if self.evaluate_line(board, row, col, 2) >= 1000000:
                return (row, col)
        
        # Then check for blocking critical human moves
        for row, col in possible_moves:
            if self.evaluate_line(board, row, col, 1) >= 1000000:
                return (row, col)
        
        return None

    def minimax(self, current_board: np.ndarray, depth: int, alpha: float, beta: float, 
                is_max_player: bool) -> Tuple[float, Optional[Tuple[int, int]]]:
        '''
        Recursively search through all possible moves to find the best one with the highest score
        :param current_board: matrix representing the current board state
        :param depth: current depth of the search tree
        :param alpha: the best (highest-value) choice found by Maximizer
        :param beta: the best (lowest-value) choice found by Minimizer
        :param is_max_player: True if maximizing player (AI), False if minimizing (human)
        :return: tuple of (best_score, best_move)
        '''
        # Base case: reached max depth or game over
        if depth == self.LIMIT_DEPTH:
            return self.evaluate_board_state(current_board), None
        
        # Check for immediate win/block at root level
        if depth == 0:
            immediate_move = self.check_immediate_win_or_block(current_board)
            if immediate_move:
                return 1000000, immediate_move
        
        possible_moves = self.get_available_indexes(current_board)
        if not possible_moves:
            return self.evaluate_board_state(current_board), None
        
        best_move = None
        
        if is_max_player:
            # Maximizing player (AI)
            best_score = float('-inf')
            for move in possible_moves:
                row, col = move
                current_board[row, col] = 2
                
                score, _ = self.minimax(current_board, depth + 1, alpha, beta, False)
                
                # Undo the move
                current_board[row, col] = 0
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break  # Beta cutoff
        else:
            # Minimizing player (human)
            best_score = float('inf')
            for move in possible_moves:
                row, col = move
                current_board[row, col] = 1
                
                score, _ = self.minimax(current_board, depth + 1, alpha, beta, True)
                
                # Undo the move
                current_board[row, col] = 0
                
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
        
        # Place the human's move
        if move_index:
            row, col = move_index
            current_board[row, col] = 1
        
        score, next_move = self.minimax(
            current_board, depth=0, alpha=float('-inf'), 
            beta=float('inf'), is_max_player=True
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
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
        self.play_board = play_board.copy()
        self.LIMIT_DEPTH = 3
        
        self.directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal down-right
            (1, -1),  # diagonal down-left
        ]
        

        
        self.eval_cache = {}
        self.threat_cache = {}

    def is_playable(self, x: int, y: int) -> bool:
        '''Check whether index (x, y) is within the board boundaries'''
        return 0 <= x < NUMBER_OF_ROW and 0 <= y < NUMBER_OF_COL

    def analyze_line_pattern(self, board: np.ndarray, row: int, col: int, 
                           dr: int, dc: int, target: int) -> Tuple[str, int]:
        '''
        Analyze the pattern in a specific direction
        '''
        consecutive = 1
        
        r, c = row + dr, col + dc
        while self.is_playable(r, c) and board[r, c] == target:
            consecutive += 1
            r += dr
            c += dc
        pos_end_open = self.is_playable(r, c) and board[r, c] == 0
        
        r, c = row - dr, col - dc
        while self.is_playable(r, c) and board[r, c] == target:
            consecutive += 1
            r -= dr
            c -= dc
        neg_end_open = self.is_playable(r, c) and board[r, c] == 0
        if consecutive >= 5:
            return 'win', consecutive
        elif consecutive == 4:
            if pos_end_open and neg_end_open:
                return 'open_four', consecutive
            elif pos_end_open or neg_end_open:
                return 'four', consecutive
            else:
                return 'blocked_four', consecutive
        elif consecutive == 3:
            if pos_end_open and neg_end_open:
                return 'open_three', consecutive
            elif pos_end_open or neg_end_open:
                return 'three', consecutive
            else:
                return 'blocked_three', consecutive
        elif consecutive == 2:
            if pos_end_open and neg_end_open:
                return 'open_two', consecutive
            elif pos_end_open or neg_end_open:
                return 'two', consecutive
            else:
                return 'blocked_two', consecutive
        else:
            return 'one', consecutive

    def find_threats(self, board: np.ndarray, target: int) -> List[Tuple[int, int, str]]:
        '''
        Find all threats for a player
        '''
        threats = []
        possible_moves = self.get_available_indexes(board)
        
        for row, col in possible_moves:
            board[row, col] = target
            
            for dr, dc in self.directions:
                pattern_type, _ = self.analyze_line_pattern(board, row, col, dr, dc, target)
                if pattern_type in ['win', 'open_four', 'four', 'open_three']:
                    threats.append((row, col, pattern_type))
                    break  # Found a threat, no need to check other directions
            
            board[row, col] = 0  # Undo placement
        
        return threats

    def evaluate_position_advanced(self, board: np.ndarray, row: int, col: int, target: int) -> int:
        '''
        Simple position evaluation based on consecutive pieces
        '''
        if board[row, col] != 0:
            return 0
        
        board[row, col] = target  # Temporarily place piece
        total_score = 0
        
        for dr, dc in self.directions:
            pattern_type, count = self.analyze_line_pattern(board, row, col, dr, dc, target)
            
            # Simple scoring based on pattern type
            if pattern_type == 'win':
                total_score += 1000000
            elif pattern_type == 'open_four':
                total_score += 100000
            elif pattern_type == 'four':
                total_score += 50000
            elif pattern_type == 'open_three':
                total_score += 10000
            elif pattern_type == 'three':
                total_score += 5000
            elif pattern_type == 'open_two':
                total_score += 1000
            elif pattern_type == 'two':
                total_score += 100
            else:
                total_score += count
        
        board[row, col] = 0
        return total_score



    def evaluate_board_state(self, board: np.ndarray) -> float:
        '''
        Simple board state evaluation
        :param board: current board state
        :return: evaluation score (positive favors AI, negative favors human)
        '''
        # Check cache first
        board_hash = self.get_board_hash(board)
        if board_hash in self.eval_cache:
            return self.eval_cache[board_hash]
        
        ai_score = 0
        human_score = 0
        
        # Evaluate potential moves
        possible_moves = self.get_available_indexes(board)
        for row, col in possible_moves:
            ai_score += self.evaluate_position_advanced(board, row, col, 2)
            human_score += self.evaluate_position_advanced(board, row, col, 1)
        
        # Simple evaluation: AI score minus human score
        result = ai_score - human_score
        
        # Cache the result
        self.eval_cache[board_hash] = result
        return result

    def get_board_hash(self, board: np.ndarray) -> str:
        '''Create a hash of the board state for memoization'''
        return str(board.tobytes())

    def get_available_indexes(self, current_board: np.ndarray) -> Set[Tuple[int, int]]:
        '''Get all available indexes for next move with adaptive radius'''
        possible_moves = set()
        
        # Find all non-empty positions
        non_empty_positions = np.where(current_board != 0)
        
        # If board is empty, start from center
        if len(non_empty_positions[0]) == 0:
            center_row, center_col = NUMBER_OF_ROW // 2, NUMBER_OF_COL // 2
            return {(center_row, center_col)}
        
        # Adaptive search radius based on number of pieces
        num_pieces = len(non_empty_positions[0])
        if num_pieces <= 4:
            search_radius = 1  # Close moves in early game
        elif num_pieces <= 10:
            search_radius = 2  # Medium range in mid game
        else:
            search_radius = 2  # Keep it manageable in late game
        
        for row, col in zip(non_empty_positions[0], non_empty_positions[1]):
            # Check within radius
            for dr in range(-search_radius, search_radius + 1):
                for dc in range(-search_radius, search_radius + 1):
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < NUMBER_OF_ROW and 
                        0 <= new_col < NUMBER_OF_COL and 
                        current_board[new_row, new_col] == 0):
                        possible_moves.add((new_row, new_col))
        
        return possible_moves

    def get_strategic_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        '''
        Get strategically prioritized moves for better move ordering
        :param board: current board state
        :return: list of moves sorted by strategic value
        '''
        possible_moves = self.get_available_indexes(board)
        num_pieces = np.count_nonzero(board)
        
        move_scores = []
        
        for row, col in possible_moves:
            # Base scores for AI and human
            ai_score = self.evaluate_position_advanced(board, row, col, 2)
            human_score = self.evaluate_position_advanced(board, row, col, 1)
            
            # Proximity bonus in early game
            if num_pieces <= 6:
                proximity_bonus = self.calculate_proximity_bonus(board, row, col)
                ai_score += proximity_bonus
            
            # Bonus for moves that respond to opponent's last move
            if num_pieces > 0:
                response_bonus = self.calculate_response_bonus(board, row, col)
                ai_score += response_bonus
            
            # Combine scores (prioritize blocking threats)
            total_score = ai_score + human_score * 1.2  # Give more weight to blocking
            move_scores.append((total_score, (row, col)))
        
        # Sort by score and return top moves
        move_scores.sort(reverse=True)
        
        # Return top 5 moves for simplicity
        return [move for _, move in move_scores[:5]]

    def calculate_proximity_bonus(self, board: np.ndarray, row: int, col: int) -> int:
        '''Calculate bonus for moves that are close to existing pieces'''
        bonus = 0
        non_empty_positions = np.where(board != 0)
        
        for piece_row, piece_col in zip(non_empty_positions[0], non_empty_positions[1]):
            distance = abs(row - piece_row) + abs(col - piece_col)
            if distance == 1:
                bonus += 50
            elif distance == 2:
                bonus += 20
            elif distance == 3:
                bonus += 5
        
        return bonus

    def calculate_response_bonus(self, board: np.ndarray, row: int, col: int) -> int:
        '''Calculate bonus for moves that respond to opponent's recent moves'''
        bonus = 0
        non_empty_positions = np.where(board != 0)
        
        # Find the most recent opponent move (assuming it's the last piece placed)
        if len(non_empty_positions[0]) > 0:
            # Get the last piece (assuming it's the opponent's move)
            last_piece_row = non_empty_positions[0][-1]
            last_piece_col = non_empty_positions[1][-1]
            
            # Calculate distance to the last move
            distance = abs(row - last_piece_row) + abs(col - last_piece_col)
            
            # Bonus for moves close to opponent's last move
            if distance == 1:
                bonus += 100  # Adjacent to opponent's move
            elif distance == 2:
                bonus += 50   # Close to opponent's move
            elif distance == 3:
                bonus += 20   # Near opponent's move
        
        return bonus

    def find_winning_move(self, board: np.ndarray) -> Optional[Tuple[int, int]]:
        '''Find immediate winning move for AI'''
        possible_moves = self.get_available_indexes(board)
        
        for row, col in possible_moves:
            # Check if this move creates a win
            board[row, col] = 2  # Temporarily place AI piece
            for dr, dc in self.directions:
                pattern_type, count = self.analyze_line_pattern(board, row, col, dr, dc, 2)
                if pattern_type == 'win':
                    board[row, col] = 0  # Undo placement
                    return (row, col)
            board[row, col] = 0  # Undo placement
        
        return None

    def find_ai_winning_move(self, board: np.ndarray) -> Optional[Tuple[int, int]]:
        '''Find immediate winning move for AI (alternative method)'''
        possible_moves = self.get_available_indexes(board)
        
        for row, col in possible_moves:
            # Check if this move creates a win by counting consecutive pieces
            board[row, col] = 2  # Temporarily place AI piece
            
            # Check all directions
            for dr, dc in self.directions:
                count = 1  # Count the current position
                
                # Count in positive direction
                r, c = row + dr, col + dc
                while self.is_playable(r, c) and board[r, c] == 2:
                    count += 1
                    r += dr
                    c += dc
                
                # Count in negative direction
                r, c = row - dr, col - dc
                while self.is_playable(r, c) and board[r, c] == 2:
                    count += 1
                    r -= dr
                    c -= dc
                
                if count >= 5:
                    board[row, col] = 0  # Undo placement
                    return (row, col)
            
            board[row, col] = 0  # Undo placement
        
        return None

    def find_blocking_move(self, board: np.ndarray) -> Optional[Tuple[int, int]]:
        '''Find move to block opponent's immediate win'''
        possible_moves = self.get_available_indexes(board)
        
        for row, col in possible_moves:
            # Check if this move blocks opponent's win
            board[row, col] = 1  # Temporarily place opponent piece
            for dr, dc in self.directions:
                pattern_type, count = self.analyze_line_pattern(board, row, col, dr, dc, 1)
                if pattern_type == 'win':
                    board[row, col] = 0  # Undo placement
                    return (row, col)
            board[row, col] = 0  # Undo placement
        
        return None

    def find_critical_move(self, board: np.ndarray) -> Optional[Tuple[int, int]]:
        '''Find critical strategic moves (win or block)'''
        
        # 1. Check for immediate win (try both methods)
        win_move = self.find_winning_move(board)
        if win_move:
            return win_move
        
        # Try alternative method
        win_move = self.find_ai_winning_move(board)
        if win_move:
            return win_move
        
        # 2. Check for necessary blocks
        block_move = self.find_blocking_move(board)
        if block_move:
            return block_move
        
        return None

    def minimax(self, current_board: np.ndarray, depth: int, alpha: float, beta: float, 
                is_max_player: bool) -> Tuple[float, Optional[Tuple[int, int]]]:
        '''
        Enhanced minimax with strategic move ordering
        '''
        # Terminal state check
        if depth == self.LIMIT_DEPTH:
            return self.evaluate_board_state(current_board), None
        
        # Check for critical moves at root level
        if depth == 0:
            critical_move = self.find_critical_move(current_board)
            if critical_move:
                return 999999, critical_move
        
        # Get strategically ordered moves
        possible_moves = self.get_strategic_moves(current_board)
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
                
                current_board[row, col] = 0
                
                if score < best_score:
                    best_score = score
                    best_move = move
                
                beta = min(beta, best_score)
                if beta <= alpha:
                    break  # Alpha cutoff
        
        return best_score, best_move

    def calculate_next_move(self, move_index: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        '''Calculate next move based on the human's latest move index'''
        # Clear caches for new move calculation
        self.eval_cache.clear()
        self.threat_cache.clear()
        
        current_board = self.play_board.copy()
        
        # The human's move should already be on the board, but let's ensure it's there
        if move_index:
            row, col = move_index
            if current_board[row, col] == 0:  # If not already placed
                current_board[row, col] = 1
        
        # First, check for immediate critical moves
        critical_move = self.find_critical_move(current_board)
        if critical_move:
            return critical_move
        
        # Use minimax to find the best move
        score, next_move = self.minimax(
            current_board, depth=0, alpha=float('-inf'), 
            beta=float('inf'), is_max_player=True
        )
        
        # If minimax fails to find a move, use strategic fallback
        if next_move is None:
            strategic_moves = self.get_strategic_moves(current_board)
            if strategic_moves:
                return strategic_moves[0]
        
        return next_move


def generate_next_move(game, move_index_2D: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    """
    Generate the next AI move using enhanced minimax algorithm
    :param game: Game instance
    :param move_index_2D: 2D coordinates of the last move
    :return: next move coordinates or None if no valid move
    """
    # Convert game board to numpy array for better performance
    # The board should already contain the player's move
    play_board = np.array(game.game_board, dtype=int)
    
    # Verify the player's move is on the board
    if move_index_2D:
        row, col = move_index_2D
        if play_board[row, col] != 1:
            print(f"Warning: Player's move {move_index_2D} not found on board")
            # Place it if missing
            play_board[row, col] = 1
    
    solver = MiniMax(play_board)
    next_move = solver.calculate_next_move(move_index_2D)
    
    # Debug output
    if next_move:
        # Convert NumPy types to native Python types for output
        if isinstance(next_move, tuple):
            converted_move = tuple(int(x) if hasattr(x, 'item') else x for x in next_move)
            print(f"AI move: {converted_move} (after player move: {move_index_2D})")
        else:
            print(f"AI move: {next_move} (after player move: {move_index_2D})")
    else:
        print(f"No AI move found (after player move: {move_index_2D})")
    
    return next_move
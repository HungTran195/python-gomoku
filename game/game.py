from .helper import Helper
from config import settings
from typing import List, Tuple, Optional, Set
import numpy as np

NUMBER_OF_ROW = settings.number_of_row
NUMBER_OF_COL = settings.number_of_col

GAME_TYPE_SINGLE = settings.game_type_single
GAME_TYPE_PVP = settings.game_type_pvp

class Game:
    """
    Game class used to create new game, process move and decide winner
    Optimized for better performance and cleaner code
    """

    def __init__(self, game_id: int, game_type: str):
        self.game_id = game_id      # Unique game ID of each game
        self.game_type = game_type  # game type: single or PvP(player vs player)
        self.player_id: List[str] = []         # sid of player created by socket IO module 
        self.player_names: List[str] = []      # Contains all player's names
        self.player_index: dict = {}      # Player's order: 1 or 2
        self.current_turn = 1       # Decide player's turn (1 or 2)
        # Use numpy array for better performance
        self.game_board = np.zeros((NUMBER_OF_ROW, NUMBER_OF_COL), dtype=int)
        self.game_over = False     # decide whether game is ended
        self.winning_line: List[Tuple[int, int]] = []      # store the indexes forming a winning line
        self.number_of_moves = 0    # count the number of taken move 
        self.number_of_games = 1    # count the number of games

        # Pre-compute direction vectors for winning line detection
        self.directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal down-right
            (1, -1),  # diagonal down-left
        ]

    def add_player(self, player_id: str, player_name: str) -> None:
        """
        Add new player in PvP game
        When the second player is added, its turn will be 2
        
        @param player_id: player's ID created by socket IO
        @param player_name: player's name
        """
        if not player_name:
            player_name = 'Default'
            
        self.player_id.append(player_id)
        self.player_index[player_id] = len(self.player_id)
        self.player_names.append(player_name)

    def get_opponent_id(self, player_id: str) -> str:
        """Get the opponent's ID for a given player"""
        index = self.player_index[player_id]
        return self.player_id[1] if index == 1 else self.player_id[0]

    def get_player_index(self, player_id: str) -> Optional[int]:
        """Return player's order according to its id"""
        return self.player_index.get(player_id)

    def rematch(self) -> None:
        """
        Reset game states: game over, game board and turn for a rematch
        """
        self.game_over = False
        self.current_turn = 1
        self.winning_line = []
        self.number_of_moves = 0
        self.number_of_games += 1
        self.game_board.fill(0)

    def process_move(self, player_id: str, move_index: Tuple[int, int]) -> bool:
        """
        Play all moves in board (PvP or single).
        Return True if move index is valid else False

        @param player_id: player's ID
        @param move_index: 2D-array indexed of move
        
        @return: Bool
        """
        player_index = self.get_player_index(player_id)
        if (player_index is not None and 
            player_index == self.current_turn and 
            self.is_valid_move(move_index) and not self.game_over):
            
            row, col = move_index
            move_value = player_index
            self.number_of_moves += 1
            self.game_board[row, col] = move_value
            
            if self.is_winning_move(row, col, move_value):
                self.game_over = True
            elif self.number_of_moves == NUMBER_OF_COL * NUMBER_OF_ROW:
                # Game tie
                self.game_over = True
            else:
                # Switch turns
                self.current_turn = 3 - self.current_turn  # 1 -> 2, 2 -> 1
            return True

        return False
    
    def is_valid_move(self, move_index: Tuple[int, int]) -> bool:
        """
        Check if the move index is valid
        """
        row, col = move_index
        return (0 <= row < NUMBER_OF_ROW and 
                0 <= col < NUMBER_OF_COL and 
                self.game_board[row, col] == 0)

    def is_winning_move(self, row: int, col: int, target: int) -> bool:
        """
        Check if current move is the winning move using optimized algorithm
        """
        for dr, dc in self.directions:
            count = 1  # Count the current position
            
            # Count in positive direction
            count += self._count_in_direction(row, col, dr, dc, target)
            # Count in negative direction
            count += self._count_in_direction(row, col, -dr, -dc, target)
            
            if count >= 5:
                self._store_winning_line(row, col, dr, dc, target)
                return True
        return False
    
    def _count_in_direction(self, row: int, col: int, dr: int, dc: int, target: int) -> int:
        """Count consecutive pieces in a given direction"""
        count = 0
        r, c = row + dr, col + dc
        
        while (0 <= r < NUMBER_OF_ROW and 
               0 <= c < NUMBER_OF_COL and 
               self.game_board[r, c] == target):
            count += 1
            r += dr
            c += dc
            
        return count

    def _store_winning_line(self, row: int, col: int, dr: int, dc: int, target: int) -> None:
        """Store the winning line coordinates"""
        winning_cells = [(row, col)]
        
        # Add cells in positive direction
        r, c = row + dr, col + dc
        while (0 <= r < NUMBER_OF_ROW and 
               0 <= c < NUMBER_OF_COL and 
               self.game_board[r, c] == target):
            winning_cells.append((r, c))
            r += dr
            c += dc
        
        # Add cells in negative direction
        r, c = row - dr, col - dc
        while (0 <= r < NUMBER_OF_ROW and 
               0 <= c < NUMBER_OF_COL and 
               self.game_board[r, c] == target):
            winning_cells.append((r, c))
            r -= dr
            c -= dc
        
        self.winning_line = winning_cells

    def get_board_state(self) -> np.ndarray:
        """Get current board state as numpy array"""
        return self.game_board.copy()

    def get_game_status(self) -> dict:
        """Get current game status"""
        return {
            'game_over': self.game_over,
            'current_turn': self.current_turn,
            'number_of_moves': self.number_of_moves,
            'winning_line': self.winning_line,
            'board': self.game_board.tolist()
        }

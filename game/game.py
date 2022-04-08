from .helper import Helper
from django.conf import settings

NUMBER_OF_ROW=settings.NUMBER_OF_ROW
NUMBER_OF_COL=settings.NUMBER_OF_COL

GAME_TYPE_SINGLE=settings.GAME_TYPE_SINGLE
GAME_TYPE_PVP=settings.GAME_TYPE_PVP
class Game:
    """
    Game class used to create new game, process move and decide winner
    """

    def __init__(self, game_id, game_type):
        self.game_id = game_id      # Unique game ID of each game
        self.game_type = game_type  # game type: single or PvP(player vs player)
        self.player_id = []         # sid of player created by socket IO module 
        self.player_names = []      # Contains all player's names
        self.player_index = {}      # Player's order: 1 or 2
        self.current_turn = 1       # Decide player's turn (1 or 2)
        self.game_board = [[0 for _ in range(NUMBER_OF_ROW)] for _ in range(NUMBER_OF_COL)]     # 2D matrix represents game board
        self.game_over  = False     # decide whether game is ended
        self.winning_line = []      # store the indexes forming a winning line
        self.number_of_moves = 0    # count the number of taken move 
        self.number_of_games = 1    # count the number of games

    def add_player(self, id, player_name):
        """
        Add new player in PvP game
        When the second player is added, its turn will be 2
        
        @param id: player's ID created by socket IO
        @param player_name: player's name

        @return: None
        """
        if not player_name:
            player_name = 'Default'
            
        self.player_id.append(id)
        self.player_index[id] = len(self.player_id)
        self.player_names.append(player_name)

    def get_opponent_id(self, player_id):
        index = self.player_index[player_id]
        if index == 1:
            return self.player_id[index]
        else: 
            return self.player_id[0]   

    def get_player_index(self, player_id):
        """Return player's order according to its id"""
        return self.player_index.get(player_id)

    def rematch(self):
        """
        Reset game states: game over, game board and  turn for a rematch
        
        @return: None
        """
        self.game_over = False
        self.current_turn = 1
        self.winning_line = []
        self.number_of_moves = 0
        self.number_of_games += 1
        for row in range(NUMBER_OF_ROW):
            for col in range(NUMBER_OF_COL):
                self.game_board[row][col] = 0

    def process_move(self, player_id, move_index):
        """
        Play all moves in board (PvP or single).
        Return True if move index is valid else False

        @param sid: player's ID
        @param move_index: 2D-array indexed of move
        
        @return: Bool
        """
        if self.get_player_index(player_id) == self.current_turn \
            and self.is_valid_move(move_index):
            row, col = move_index
            move_value = self.get_player_index(player_id)
            self.number_of_moves += 1
            self.game_board[row][col] = move_value
            print(f'processing {player_id} {move_value} {move_index}')
            if self.is_winning_move(row, col, move_value):
                self.game_over = True

            elif self.number_of_moves == NUMBER_OF_COL * NUMBER_OF_ROW:
                # Game tie
                self.game_over = True
                
            else:
                if self.current_turn == 1:
                    self.current_turn = 2
                else:
                    self.current_turn = 1
            return True

        return False
    
    def is_valid_move(self,move_index):
        """
        Check if the move index is valid
        """
        row, col = move_index
        if row >= 0 and col >= 0 and row < NUMBER_OF_ROW and col < NUMBER_OF_COL \
            and self.game_board[row][col] == 0:
            return True
        return False

    def is_winning_move(self, row, col, target):
        """
        Check if current move is the winning move 
        by count all surrounding nodes that has the same target value
        """
        for direction in ['up_down', 'left_right', 'up_left', 'down_right']:
            if self.count_connected(row, col, target, direction) == 5:
                return True
        return False
    

    def is_available_index(self, row, col, target, contain_set):
        """
        Check if current move index is valid
        """
        if row >= 0 and col >= 0 and row < NUMBER_OF_ROW and col < NUMBER_OF_COL \
            and self.game_board[row][col] == target and (row, col) not in contain_set:
            return True
        return False

    def count_connected(self, row, col, target, direction):
        """
        Count number of connected nodes in game matrix in one direction

        @param row: row index 
        @param col: column index
        @param target: 1 or 2. Represent whose move
        @param direction: direction to look for connected nodes   
        
        @return: int
        """
        count = 1
        stack = []
        seen = set()
        if direction == 'left_right':
            stack.append((row, col))
            seen.add((row, col))
            while stack:
                if self.is_available_index(row, col - 1, target, seen):
                    stack.append((row, col-1))
                    seen.add((row, col-1))
                    count += 1

                if self.is_available_index(row, col + 1, target, seen):
                    stack.append((row, col+1))
                    seen.add((row, col+1))
                    count += 1
                row, col = stack.pop()

        if direction == 'up_down':
            stack.append((row, col))
            seen.add((row, col))
            while stack:
                if self.is_available_index(row-1, col, target, seen):
                    stack.append((row-1, col))
                    seen.add((row-1, col))
                    count += 1

                if self.is_available_index(row + 1, col, target, seen):
                    stack.append((row+1, col))
                    seen.add((row+1, col))
                    count += 1
                row, col = stack.pop()

        if direction == 'up_left':
            stack.append((row, col))
            seen.add((row, col))
            while stack:
                if self.is_available_index(row+1, col + 1, target, seen):
                    stack.append((row+1, col+1))
                    seen.add((row+1, col+1))
                    count += 1

                if self.is_available_index(row-1, col - 1, target, seen):
                    stack.append((row-1, col-1))
                    seen.add((row-1, col-1))
                    count += 1

                row, col = stack.pop()

        if direction == 'down_right':
            stack.append((row, col))
            seen.add((row, col))
            while stack:
                if self.is_available_index(row - 1, col + 1, target, seen):
                    stack.append((row-1, col+1))
                    seen.add((row-1, col+1))
                    count += 1

                if self.is_available_index(row+1, col - 1, target, seen):
                    stack.append((row+1, col-1))
                    seen.add((row+1, col-1))
                    count += 1
                row, col = stack.pop()

        if count == 5:
            self.winning_line = list(seen)
            return count
        return None

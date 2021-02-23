from random import random

NUM_ROW = 20
NUM_COL = 20

id = 0


def generate_game_id():
    id = random()
    return int(id*100000000)


def get_room_id(room_name):
    return 1


class Game:
    def __init__(self, game_id):
        self.game_id = game_id
        self.turn = 0
        self.player_id = {}
        self.play_board = [[0 for _ in range(NUM_COL)] for _ in range(NUM_ROW)]
        self.winner = 0
        self.winning_line = []
        # self.current_player = 0
        self.turn = 1

    def create_new_game(self, game_id, id):
        if not self.player_id:
            self.player_id[id] = True
        else:
            self.player_id[id] = False
        pass

    def process_move(self, sid, move_index):
        row, col = self.convert_index_to_2D(move_index)
        self.play_board[row][col] = self.turn + 1
        is_winner = self.is_winning_move(row, col)

        data = {'move_index': move_index,
                'is_winner': is_winner, 'winning_line': [],
                'turn': self.player_id[sid]}

        self.turn = not(self.turn)
        return data

    def is_winning_move(self, row, col):
        return False

    def get_current_game_state(self):
        current_game_state = []
        for i in range(len(self.play_board)):
            for j in range(len(self.play_board[0])):
                current_game_state.append(self.play_board[i][j])
        return current_game_state

    def convert_index_to_2D(self, index):
        index = int(index)
        row = index // NUM_COL
        col = index % NUM_COL
        return [row, col]

    def convert_index_to_1D(self, index):
        return index[0] * NUM_COL + index[1]

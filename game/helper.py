from random import random

NUM_ROW = 18
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
        self.player_id = {}
        self.player_opponent = {}
        self.player_name = {}
        self.play_board = [[0 for _ in range(NUM_COL)] for _ in range(NUM_ROW)]
        self.winner = None
        self.stat_board = {}
        self.winning_line = []
        self.turn = 1

    def create_new_game(self, game_id, id, player_name):
        if not self.player_id:
            self.player_id[id] = 1
            self.stat_board[id] = 0
            self.player_opponent[id] = 0
        else:
            self.player_id[id] = 0
            self.stat_board[id] = 0
            for sid, val in self.player_opponent.items():
                self.player_opponent[sid] = id
                self.player_opponent[id] = sid
                break
        self.player_name[id] = player_name

    def reset_game(self):
        self.turn = 1
        self.winning_line = []
        self.winner = None
        self.play_board = [[0 for _ in range(NUM_COL)] for _ in range(NUM_ROW)]

    def process_move(self, sid, move_index):
        row, col = self.convert_index_to_2D(move_index)
        winning_line = []
        if self.play_board[row][col] == 0:
            self.play_board[row][col] = self.turn + 1
            if self.is_winning_move(row, col, self.turn+1):
                for index in self.winning_line:
                    winning_line.append(self.convert_index_to_1D(index))
                self.winning_line = winning_line
                self.winner = sid
                self.stat_board[sid] += 1
                self.turn = 2

            else:
                self.turn = not(self.turn)
            return True
        return False

    def is_winning_move(self, x, y, target):
        for direction in ['up_down', 'left_right', 'up_left', 'down_right']:
            if self.count_connected(x, y, target, direction) == 5:
                return True
        return False

    def count_connected(self, x, y, target, direction):
        count = 1
        stack = []
        seen = set()
        if direction == 'up_down':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if y > 0 and self.play_board[x][y-1] == target and (x, y-1) not in seen:
                    stack.append((x, y-1))
                    seen.add((x, y-1))
                    count += 1

                if y + 1 < NUM_COL and self.play_board[x][y+1] == target and (x, y+1) not in seen:
                    stack.append((x, y+1))
                    seen.add((x, y+1))
                    count += 1
                x, y = stack.pop()

        if direction == 'left_right':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x > 0 and self.play_board[x-1][y] == target and (x-1, y) not in seen:
                    stack.append((x-1, y))
                    seen.add((x-1, y))
                    count += 1

                if x + 1 < NUM_ROW and self.play_board[x+1][y] == target and (x+1, y) not in seen:
                    stack.append((x+1, y))
                    seen.add((x+1, y))
                    count += 1
                x, y = stack.pop()

        if direction == 'up_left':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x + 1 < NUM_COL and y + 1 < NUM_ROW and self.play_board[x+1][y+1] == target and (x+1, y+1) not in seen:
                    stack.append((x+1, y+1))
                    seen.add((x+1, y+1))
                    count += 1

                if x > 0 and y > 0 and self.play_board[x-1][y-1] == target and (x-1, y-1) not in seen:
                    stack.append((x-1, y-1))
                    seen.add((x-1, y-1))
                    count += 1
                x, y = stack.pop()

        if direction == 'down_right':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x > 0 and y + 1 < NUM_ROW and self.play_board[x-1][y+1] == target and (x-1, y+1) not in seen:
                    stack.append((x-1, y+1))
                    seen.add((x-1, y+1))
                    count += 1

                if x + 1 < NUM_COL and y > 0 and self.play_board[x+1][y-1] == target and (x+1, y-1) not in seen:
                    stack.append((x+1, y-1))
                    seen.add((x+1, y-1))
                    count += 1
                x, y = stack.pop()

        if count == 5:
            self.winning_line = list(seen)
            return count
        return None

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

    def close_game(self):
        self.turn = 2
        return

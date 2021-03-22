from .config import Config


class Game:
    def __init__(self, game_id):
        self.game_id = game_id
        self.id_to_turn = {}
        self.id_to_opponent = {}
        self.id_to_name = {}
        self.play_board = [
            [0 for _ in range(Config.NUM_COL)] for _ in range(Config.NUM_ROW)]
        self.winner_id = None
        self.stat_board = {}
        self.winning_line_index = []
        self.current_turn = 1

    def create_new_game(self, id, player_name):
        if not self.id_to_turn:
            self.id_to_turn[id] = 1
            self.stat_board[id] = 0
            self.id_to_opponent[id] = 0
        else:
            self.id_to_turn[id] = 0
            self.stat_board[id] = 0
            for sid, val in self.id_to_opponent.items():
                self.id_to_opponent[sid] = id
                self.id_to_opponent[id] = sid
                break
        self.id_to_name[id] = player_name

    def reset_game(self):
        self.current_turn = 1
        self.winning_line_index = []
        self.winner_id = None
        self.play_board = [
            [0 for _ in range(Config.NUM_COL)] for _ in range(Config.NUM_ROW)]

    def process_move(self, sid, move_index):
        row, col = self.convert_index_to_2D(move_index)
        winning_line_index = []
        if self.play_board[row][col] == 0:
            self.play_board[row][col] = self.current_turn + 1
            if self.is_winning_move(row, col, self.current_turn+1):
                for index in self.winning_line_index:
                    winning_line_index.append(self.convert_index_to_1D(index))
                self.winning_line_index = winning_line_index
                self.winner_id = sid
                self.stat_board[sid] += 1
                self.current_turn = 2
            else:
                self.current_turn = not(self.current_turn)
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

                if y + 1 < Config.NUM_ROW and self.play_board[x][y+1] == target and (x, y+1) not in seen:
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

                if x + 1 < Config.NUM_COL and self.play_board[x+1][y] == target and (x+1, y) not in seen:
                    stack.append((x+1, y))
                    seen.add((x+1, y))
                    count += 1
                x, y = stack.pop()

        if direction == 'up_left':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x + 1 < Config.NUM_COL and y + 1 < Config.NUM_ROW and self.play_board[x+1][y+1] == target and (x+1, y+1) not in seen:
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
                if x > 0 and y + 1 < Config.NUM_ROW and self.play_board[x-1][y+1] == target and (x-1, y+1) not in seen:
                    stack.append((x-1, y+1))
                    seen.add((x-1, y+1))
                    count += 1

                if x + 1 < Config.NUM_COL and y > 0 and self.play_board[x+1][y-1] == target and (x+1, y-1) not in seen:
                    stack.append((x+1, y-1))
                    seen.add((x+1, y-1))
                    count += 1
                x, y = stack.pop()

        if count == 5:
            self.winning_line_index = list(seen)
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
        row = index // Config.NUM_COL
        col = index % Config.NUM_COL
        return [row, col]

    def convert_index_to_1D(self, index):
        return index[0] * Config.NUM_COL + index[1]

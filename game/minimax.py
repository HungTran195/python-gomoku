from django.conf import settings

NUMBER_OF_ROW=settings.NUMBER_OF_ROW
NUMBER_OF_COL=settings.NUMBER_OF_COL

class MiniMax:
    '''
    A class used MiniMax with alpha, beta pruning
    to predict the next best possible move
    '''

    def __init__(self, play_board):
        self.play_board = play_board    # a deep-copy of original board
        self.LIMIT_DEPTH = 3            # Max depth of tree to search for next move

    def is_playable(self, x, y):
        '''
        Check whether index (x, y) is out of the board
        :param x: row index 
        :param y: column index
        Return true/false
        '''
        if x >= 0 and y >= 0 and x < NUMBER_OF_ROW and y < NUMBER_OF_COL:
            return True
        return False

    def is_available_index(self, board, x, y, compared_target, contain_set=None):
        '''
        Check if index (x, y) can be used for processing
        :param board: matrix represent the current board state
        :param x: row index 
        :param y: column index
        :param compared_target: value of the current processing state
        :param contain_set: a set type variable contain all processed value
        :Return: true/false
        '''
        if self.is_playable(x, y) and board[x][y] == compared_target:
            if contain_set:
                if (x, y) not in contain_set:
                    return True
            else:
                return True
        return False

    def get_score_from_count(self, count):
        '''
        Return points based on number of connected node in board
        :param count: number of connected node in board
        :return: int
        '''
        if count == 3:
            return 100
        if count == 4:
            return 1000
        if count == 5:
            return 100000
        return count*count

    def count_and_score_connected(self, board, row, col, target):
        '''
        Count the number of connected node in game board and decide point for the current move
        :param board: matrix represent the current board state
        :param row: index of row in board matrix
        :param col: index of col in board matrix
        :param target: value of node to compared (1 is for human and 2 is for ai)
        :return: int
        '''
        score = 0
        directions = [[(0, -1), (0, 1)],   # vertical coeff
                      [(-1, 0), (1, 0)],   # horizontal coeff
                      [(-1, -1), (1, 1)],  # diagonal coeff - left -> right
                      [(-1, 1), (1, -1)]]  # diagonal coeff - right -> left
        for direction in directions:
            # Set count to 0 before looping any direction
            count = 1
            # Loop through the coefficients of each direction(vertical, horizontal and diagonals)
            # Each direction will be checked 2 times from 2 sides
            # started from the starting point with 2 different coefficients
            # (check_1)     _                _           _             _
            #     _      (check_1)           _           _             _
            #     _         _       (starting point)     _             _
            #     _         _                _        (check_2)        _
        #     _         _                    _           _         (check_2)
            for coeffs in direction:
                # get coefficient of x and y from coeffs tupple
                coeff_x, coeff_y = coeffs
                # reset co-ordinate (x, y) to starting point
                x, y = row + coeff_x, col + coeff_y
                # if the current node belongs to other's player, this connected line is blocked
                # then it is not valuable as other none blocked line
                if self.is_playable(x, y) and board[x][y] != 0 and board[x][y] != target:
                    # count -= 1
                    continue
                # while it's not winning move and neither of x and y index is available
                # loop through one side of the direction and count the connected nodes
                while self.is_available_index(board, x, y, target):
                    count += 1
                    x = x + coeff_x
                    y = y + coeff_y
                    # if count is 5, this mean that game is over
                    # the current move is the winning move
                    # no need to check for any other possible moves
                    if count == 5:
                        return self.get_score_from_count(count)
                
            score += self.get_score_from_count(count)

        return score

    def score_move_taken(self, current_board, move_taken, is_ai):
        '''
        Score the current game state created by predicted move
        :param current_board: matrix represent the current board state
        :param move_taken: list that contain move taken by ai and human 
        :param is_ai: true AI's turn, false - human's turn

        :return: int
        '''
        target = 2 if is_ai else 1
        defense = 1 if is_ai else 2

        total_score = 0

        for move in move_taken:
            row, col = move
            if current_board[row][col] == target:
                # Count the number of connected node
                score = self.count_and_score_connected(
                    current_board, row, col, target)
                # Incase the move is to defense (block other's move from either side)
                # Count the number of nodes that are blocked
                # Move that block more nodes generates higher score
                score_defense = self.count_and_score_connected(
                    current_board, row, col, defense)

                # Final score is the sum of all scores in 4 directions
                total_score += score + score_defense
        return total_score

    def get_available_indexes(self, current_board):
        '''
        Get all available index for next move
        Only get index around played node in board due to limited computability
        :param current_board: matrix represent the current board state
        :return: set of all available moves
        '''
        possible_moves = set()
        for row in range(NUMBER_OF_ROW):
            for col in range(NUMBER_OF_COL):
                if current_board[row][col] != 0:
                    for i in (-1, 0,  1):
                        for j in (-1, 0, 1):
                            if (i, j) != (0, 0) and self.is_available_index(current_board, row + i, col + j, 0, possible_moves):
                                possible_moves.add((row + i, col + j))
        return possible_moves

    def minimax(self, current_board, move_index, depth, alpha, beta, possible_moves, move_taken, is_max_player):
        '''
        Recursively loop through all possible move to find the best one with the highest score
        :param current_board: matrix represent the current board state
        :param move_index: human's latest move index
        :param depth: current depth of the search tree
        :param alpha: the best (highest-value) choice found by Maximizer
        :param beta: the best (lowest-value) choice found by Minimizer
        :return: list type
        '''
        if depth == self.LIMIT_DEPTH:
            score = self.score_move_taken(
                current_board, move_taken, is_ai=True)
            return score, move_index
        best_move = None
        row, col = move_index

        current_board[row][col] = 2 if is_max_player else 1
        all_possible_moves = self.get_available_indexes(current_board)

        # Use max score when it is AI's turn
        if is_max_player:
            # Initialise best_score with small value, - inf
            best_score = 0
            for move in all_possible_moves:
                move_taken.append(move)

                score, good_move = self.minimax(
                    current_board, move, depth + 1, alpha, beta, all_possible_moves, move_taken, is_max_player=False)
                previous_move = move_taken.pop()
                current_board[previous_move[0]][previous_move[1]] = 0

                if score > best_score:
                    best_score = score
                    best_move = move

                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break

        # Use min score to simulate human's turn
        else:
            # Initialise best_score with high value, + inf
            best_score = 10000000
            for move in all_possible_moves:
                move_taken.append(move)

                score, good_move = self.minimax(
                    current_board, move, depth + 1, alpha, beta, all_possible_moves, move_taken, is_max_player=True)
                previous_move = move_taken.pop()
                current_board[previous_move[0]][previous_move[1]] = 0

                if score < best_score:
                    best_score = score
                    best_move = move

                beta = min(beta, best_score)
                if beta <= alpha:
                    break

        return best_score, best_move

    def calculate_next_move(self, move_index):
        '''
        Calculate next move based on the human's latest move index
        :param move_index: human's latest move index
        :return: list type
        '''
        current_board = self.play_board
        score, next_move = self.minimax(
            current_board, move_index, depth=0, alpha=-1, beta=1000000, possible_moves=None, move_taken=[move_index], is_max_player=True)

        return next_move


def generate_next_move(game, move_index_2D):
    play_board = [[0 for _ in range(NUMBER_OF_COL)]
                  for _ in range(NUMBER_OF_ROW)]
    for row in range(NUMBER_OF_ROW):
        for col in range(NUMBER_OF_COL):
            play_board[row][col] = game.game_board[row][col]

    solver = MiniMax(play_board)
    next_move = solver.calculate_next_move(move_index_2D)
    return next_move

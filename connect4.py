import pygame


class MyWindow:
    def __init__(self, win_size, num_of_rows, num_of_cols):
        super().__init__()
        self.UNIT_RADIUS = 25
        self.BACKGROUND_COLOR = (192, 192, 192)  # Silver
        self.NODE_COLOR = (128, 128, 128)  # Grey
        self.POINTING_NODE_COLOR = (211, 211, 211)  # Light Grey
        self.PLAYER1_COLOR = (224, 226, 75)  # Light Yellow
        self.PLAYER2_COLOR = (250, 103, 103)  # Light red
        self.CONNECT_LINE_COLOR = (0, 255, 255)  # Cyan
        self.num_of_rows = num_of_rows
        self.num_of_cols = num_of_cols
        self.reset_button_pos = [800, 600]
        self.font = pygame.font.SysFont('comic Sans MS', 30, True)
        self.isWinner = False
        self.isTurn = True
        self.nodes = {}
        for i in range(self.num_of_rows):
            for j in range(self.num_of_cols):
                self.nodes[(i, j)] = [self.NODE_COLOR, 0]
        # Set up the drawing window
        self.screen = pygame.display.set_mode(win_size)

    def run_game(self):

        running = True
        prev_pointed = ()

        while running:
            pygame.time.delay(50)

            self.screen.fill(self.BACKGROUND_COLOR)

            # check for all event happened in game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = self.get_node_index()
                    if x is not None and y is not None and not self.nodes[(x, y)][1] and not self.isWinner:
                        if self.isTurn:
                            self.nodes[(x, y)] = [self.PLAYER1_COLOR, 1]
                            self.isWinner = self.check_winner(x, y, 1)
                        else:
                            self.nodes[(x, y)] = [self.PLAYER2_COLOR, 2]
                            self.isWinner = self.check_winner(x, y, 2)

                        self.isTurn = not(self.isTurn)

                if event.type == pygame.MOUSEMOTION:
                    x, y = self.get_node_index()
                    if x is not None and y is not None:
                        if self.nodes.get(prev_pointed) and not self.nodes[prev_pointed][1]:
                            self.nodes[prev_pointed] = [self.NODE_COLOR, 0]
                        if not self.nodes[(x, y)][1]:
                            self.nodes[(x, y)] = [self.POINTING_NODE_COLOR, 0]
                        prev_pointed = (x, y)
            self.draw_nodes()
            self.draw_side_bar(self.isTurn)

            if self.isWinner:
                if not self.isTurn:
                    self.draw_winner('Player 1')
                else:
                    self.draw_winner('Player 2')

            # Updates the contents of the display to the screen
            # pygame.display.flip()
            pygame.display.update()
        # Quit game
        pygame.quit()

    def get_node_index(self):
        x, y = pygame.mouse.get_pos()
        if x >= 800 and x <= 990 and y >= 599 and y <= 650:
            self.reset_game()
            return None, None
        x = x // 52
        y = y // 52
        if x < self.num_of_rows and y < self.num_of_cols:
            return x, y
        return None, None

    def draw_nodes(self):
        for i in range(self.num_of_rows):
            for j in range(self.num_of_cols):
                color = self.nodes[(i, j)][0]
                pygame.draw.circle(self.screen, color,
                                   (52*i + 30, 52*j + 30), self.UNIT_RADIUS)

    def draw_side_bar(self, isTurn=True):
        player1 = self.font.render('Player 1', 1, (0, 0, 0))
        player2 = self.font.render('Player 2', 1, (0, 0, 0))
        reset = self.font.render('Reset Game', 1, (0, 0, 0))
        if isTurn:
            color1 = self.PLAYER1_COLOR
            color2 = (50, 90, 90)
        else:
            color1 = (50, 90, 90)
            color2 = self.PLAYER2_COLOR
        pygame.draw.rect(self.screen, color1, (840, 100, 135, 50))
        pygame.draw.rect(self.screen, color2, (840, 200, 135, 50))
        pygame.draw.rect(self.screen, (50, 90, 190), (800, 600, 190, 50))
        self.screen.blit(player1, (850, 100))
        self.screen.blit(player2, (850, 200))
        self.screen.blit(reset, (810, 600))

    def draw_winner(self, name):
        playerName = self.font.render(name, 1, (0, 0, 0))
        text = self.font.render('is the Winner', 1, (0, 0, 0))
        if name == 'Player 1':
            color = self.PLAYER1_COLOR
        else:
            color = self.PLAYER2_COLOR

        pygame.draw.rect(self.screen, color, (790, 400, 205, 100))
        self.screen.blit(playerName, (850, 400))
        self.screen.blit(text, (790, 450))

    def check_winner(self, x, y, target):
        if self.count_connected(x, y, target, 'up_down') == 4:
            return True
        if self.count_connected(x, y, target, 'left_right') == 4:
            return True
        if self.count_connected(x, y, target, 'up_left') == 4:
            return True
        if self.count_connected(x, y, target, 'down_right') == 4:
            return True
        return False

    def count_connected(self, x, y, target, dir):
        count = 1
        stack = []
        seen = set()
        if dir == 'up_down':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if y > 0 and self.nodes[(x, y-1)][1] == target and (x, y-1) not in seen:
                    stack.append((x, y-1))
                    seen.add((x, y-1))
                    count += 1

                if y + 1 < self.num_of_cols and self.nodes[(x, y+1)][1] == target and (x, y+1) not in seen:
                    stack.append((x, y+1))
                    seen.add((x, y+1))
                    count += 1
                x, y = stack.pop()
            return count

        if dir == 'left_right':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x > 0 and self.nodes[(x-1, y)][1] == target and (x-1, y) not in seen:
                    stack.append((x-1, y))
                    seen.add((x-1, y))
                    count += 1

                if x + 1 < self.num_of_rows and self.nodes[(x+1, y)][1] == target and (x+1, y) not in seen:
                    stack.append((x+1, y))
                    seen.add((x+1, y))
                    count += 1
                x, y = stack.pop()
            return count

        if dir == 'up_left':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x + 1 < self.num_of_cols and y + 1 < self.num_of_cols and self.nodes[(x+1, y+1)][1] == target and (x+1, y+1) not in seen:
                    stack.append((x+1, y+1))
                    seen.add((x+1, y+1))
                    count += 1

                if x > 0 and y > 0 and self.nodes[(x-1, y-1)][1] == target and (x-1, y-1) not in seen:
                    stack.append((x-1, y-1))
                    seen.add((x-1, y-1))
                    count += 1
                x, y = stack.pop()
            return count

        if dir == 'down_right':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x > 0 and y + 1 < self.num_of_cols and self.nodes[(x-1, y+1)][1] == target and (x-1, y+1) not in seen:
                    stack.append((x-1, y+1))
                    seen.add((x-1, y+1))
                    count += 1

                if x + 1 < self.num_of_cols and y > 0 and self.nodes[(x+1, y-1)][1] == target and (x+1, y-1) not in seen:
                    stack.append((x+1, y-1))
                    seen.add((x+1, y-1))
                    count += 1
                x, y = stack.pop()
            return count

        return count

    def reset_game(self):
        for i in range(self.num_of_rows):
            for j in range(self.num_of_cols):
                self.nodes[(i, j)] = [self.NODE_COLOR, 0]
        self.isWinner = False
        self.isTurn = True

    def find_best_move(self, x, y):
        pass


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Connect 4")
    win_size = [1000, 790]

    num_of_rows = 15
    num_of_cols = 15
    new_game = MyWindow(win_size, num_of_rows, num_of_cols)
    new_game.run_game()

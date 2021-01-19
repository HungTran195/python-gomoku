import pygame


class MyWindow:
    def __init__(self, win_size, num_of_horizontal_nodes, num_of_vertical_nodes):
        super().__init__()
        self.UNIT_RADIUS = 35
        self.BACKGROUND_COLOR = (192, 192, 192)  # Silver
        self.NODE_COLOR = (128, 128, 128)  # Grey
        self.POINTING_NODE_COLOR = (211, 211, 211)  # Light Grey
        self.PLAYER1_COLOR = (224, 226, 75)  # Light Yellow
        self.PLAYER2_COLOR = (250, 103, 103)  # Light red
        self.CONNECT_LINE_COLOR = (0, 255, 255)  # Cyan
        self.nodes = {}
        for i in range(num_of_vertical_nodes):
            for j in range(num_of_horizontal_nodes):
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
                    if not self.nodes[(x, y)][1]:
                        self.nodes[(x, y)] = [self.PLAYER1_COLOR, 1]

                if event.type == pygame.MOUSEMOTION:
                    x, y = self.get_node_index()
                    if self.nodes.get(prev_pointed) and not self.nodes[prev_pointed][1]:
                        self.nodes[prev_pointed] = [self.NODE_COLOR, 0]
                    if not self.nodes[(x, y)][1]:
                        self.nodes[(x, y)] = [self.POINTING_NODE_COLOR, 0]
                    prev_pointed = (x, y)
            self.draw_nodes()
            # Updates the contents of the display to the screen
            pygame.display.flip()
        # Quit game
        pygame.quit()

    def get_node_index(self):
        x, y = pygame.mouse.get_pos()
        x = x // 75
        y = y // 75
        return x, y

    def draw_nodes(self):
        for i in range(10):
            for j in range(10):
                color = self.nodes[(i, j)][0]
                pygame.draw.circle(self.screen, color,
                                   (75*i + 35, 75*j + 35), self.UNIT_RADIUS)


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Connect 4")
    win_size = [745, 745]
    num_of_horizontal_nodes = 10
    num_of_vertical_nodes = 10
    new_game = MyWindow(win_size, num_of_horizontal_nodes,
                        num_of_vertical_nodes)
    new_game.run_game()

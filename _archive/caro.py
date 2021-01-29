import pygame
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep


class MyWindow(ConnectionListener):
    def Network_startgame(self, data):
        print(data)
        self.running = True
        self.player_id = data["player"]
        self.game_id = data["game_id"]

    def Network_connected(self, data):
        print("connected to the server")

    def Network_disconnected(self, data):
        print("disconnected from the server")

    def Network_yourturn(self, data):
        # torf = short for true or false
        self.isTurn = data["torf"]

    def Network_place(self, data):
        x = data["x"]
        y = data["y"]
        player_id = data["player_id"]

        if player_id == 0:
            self.nodes[(x, y)] = [self.PLAYER1_COLOR, 1]
        else:
            self.nodes[(x, y)] = [self.PLAYER2_COLOR, 2]

    def Network_close(self, data):
        print("close from the server")
        exit()

    def Network_win(self, data):
        print('winner', data)
        self.isWinner = True
        self.isTurn = data["torf"]
        self.winning_line = data['winning_line']
        # self.draw_winner()

    def Network_lose(self, data):
        print('loser', data)
        self.isTurn = data["torf"]
        self.isWinner = True
        self.winning_line = data['winning_line']
        # self.draw_loser()

    def __init__(self, win_size, num_of_rows, num_of_cols):
        super().__init__()
        self.UNIT_RADIUS = 20
        self.BACKGROUND_COLOR = (192, 192, 192)  # Silver
        self.NODE_COLOR = (128, 128, 128)  # Grey
        self.POINTING_NODE_COLOR = (211, 211, 211)  # Light Grey
        self.PLAYER1_COLOR = (224, 226, 75)  # Light Yellow
        self.PLAYER2_COLOR = (250, 103, 103)  # Light red
        self.WINNER_COLOR = (0, 255, 255)  # Cyan
        self.num_of_rows = num_of_rows
        self.num_of_cols = num_of_cols
        self.coff = self.UNIT_RADIUS*2+2
        self.reset_button_pos = [800, 600]
        self.font = pygame.font.SysFont('comic Sans MS', 30, True)
        self.isWinner = False
        self.isTurn = True
        self.nodes = {}
        self.winning_line = []
        self.game_id = None
        self.player_id = None

        for i in range(self.num_of_rows):
            for j in range(self.num_of_cols):
                self.nodes[(i, j)] = [self.NODE_COLOR, 0]
        # Set up the drawing window
        self.screen = pygame.display.set_mode(win_size, flags=pygame.RESIZABLE)

        address = input("Address of Server: ")
        try:
            if not address:
                host, port = "localhost", 8000
            else:
                host, port = address.split(":")
            self.Connect((host, int(port)))
        except:
            print("Error Connecting to Server")
            print("Usage:", "host:port")
            print("e.g.", "localhost:31425")
            exit()
        print("Boxes client started")

        self.running = False
        while not self.running:
            self.Pump()
            connection.Pump()
            sleep(0.001)

        if self.player_id == 0:
            self.isTurn = True
            self.player_color = self.PLAYER1_COLOR
        else:
            self.isTurn = False
            self.player_color = self.PLAYER2_COLOR

        # print('Done')

    def run_game(self):
        running = True
        prev_pointed = (0, 0)
        clock = pygame.time.Clock()

        while running:

            # make sure games doesn't run faster than 24 frames per second.
            clock.tick(24)

            self.screen.fill(self.BACKGROUND_COLOR)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            x, y = pygame.mouse.get_pos()
            # if x >= 800 and x <= 985 and y >= 600 and y <= 650 and pygame.mouse.get_pressed()[0]:
            #     self.reset_game()
            x, y = x // self.coff, y // self.coff
            if x < self.num_of_rows and y < self.num_of_cols:
                if not self.nodes[(x, y)][1]:
                    if not self.nodes[prev_pointed][1]:
                        self.nodes[prev_pointed] = [self.NODE_COLOR, 0]
                    self.nodes[(x, y)] = [self.POINTING_NODE_COLOR, 0]
                    prev_pointed = (x, y)
                if pygame.mouse.get_pressed()[0] and self.isTurn and not self.isWinner and not self.nodes[(x, y)][1]:

                    self.Send({"action": "place", "x": x, "y": y,
                               "game_id": self.game_id, "player_id": self.player_id})

            if self.isWinner:
                if self.isTurn:
                    self.draw_winner()
                else:
                    self.draw_loser()

            self.draw_nodes()
            self.draw_side_bar(self.isTurn)

            # Updates the contents of the display to the screen
            # pygame.display.flip()
            pygame.display.update()
            connection.Pump()
            self.Pump()
        # Quit game
        pygame.quit()

    def draw_nodes(self):
        for i in range(self.num_of_rows):
            for j in range(self.num_of_cols):
                color = self.nodes[(i, j)][0]

                pygame.draw.circle(self.screen, color,
                                   (self.coff*i + self.UNIT_RADIUS + 5,
                                    self.coff*j + self.UNIT_RADIUS + 5),
                                   self.UNIT_RADIUS)

    def draw_side_bar(self, isTurn):
        if isTurn:
            color = self.player_color
        else:
            color = (50, 90, 90)

        text = self.font.render('Your Turn', 1, (0, 0, 0))
        pygame.draw.rect(self.screen, color, (848, 100, 148, 50))
        self.screen.blit(text, (850, 100))

    def draw_winner(self, name=None):
        for node in self.winning_line:
            self.nodes[node][0] = self.WINNER_COLOR

        text = self.font.render('You Win!', 1, (0, 0, 0))

        pygame.draw.rect(self.screen, self.player_color, (850, 400, 140, 50))
        self.screen.blit(text, (855, 400))

    def draw_loser(self):
        for node in self.winning_line:
            self.nodes[node][0] = self.WINNER_COLOR

        text = self.font.render('You Lose!', 1, (0, 0, 0))

        pygame.draw.rect(self.screen, self.player_color, (850, 400, 142, 50))
        self.screen.blit(text, (855, 400))

    def reset_game(self):
        for i in range(self.num_of_rows):
            for j in range(self.num_of_cols):
                self.nodes[(i, j)] = [self.NODE_COLOR, 0]
        self.isWinner = False
        self.isTurn = True
        self.winning_line = []

    def find_best_move(self, x, y):
        pass


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Connect 4")
    num_of_rows = 20
    num_of_cols = 20
    win_size = [1000, 850]

    new_game = MyWindow(win_size, num_of_rows, num_of_cols)
    new_game.run_game()

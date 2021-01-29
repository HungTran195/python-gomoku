from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep


class ClientChannel(Channel):
    def Network(self, data):
        print(data)

    def Network_place(self, data):
        # player number (1 or 0)
        player_id = data["player_id"]

        x = data["x"]
        y = data["y"]

        # id of game given by server at start of game
        self.game_id = data["game_id"]

        self._server.placeDot(x, y, data, self.game_id, player_id)

    def Close(self):
        self._server.close(self.game_id)


class MyServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.games = []
        self.queue = None
        self.current_index = 0

    def Connected(self, channel, addr):
        print('new connection:', channel)
        if self.queue == None:
            self.current_index += 1
            channel.game_id = self.current_index
            self.queue = Game(channel, self.current_index)
        else:
            channel.game_id = self.current_index
            self.queue.player1 = channel
            self.queue.player0.Send(
                {"action": "startgame", "player": 0, "game_id": self.queue.game_id})
            self.queue.player1.Send(
                {"action": "startgame", "player": 1, "game_id": self.queue.game_id})
            self.games.append(self.queue)
            self.queue = None

    def placeDot(self, x, y, data, game_id, player_id):
        game = [a for a in self.games if a.game_id == game_id]
        if len(game) == 1:
            game[0].placeDot(x, y, data, player_id)

    def close(self, game_id):
        try:
            game = [a for a in self.games if a.game_id == game_id][0]
            game.player0.Send({"action": "close"})
            game.player1.Send({"action": "close"})
        except:
            pass


class Game:
    def __init__(self, player, current_index):
        self.turn = 0
        self.player0 = player
        self.player1 = None
        self.game_id = current_index
        self.num_of_rows = 20
        self.num_of_cols = 20
        self.winning_line = []
        self.nodes = {}
        for i in range(self.num_of_rows):
            for j in range(self.num_of_cols):
                self.nodes[(i, j)] = 0

    def placeDot(self, x, y, data, player_id):
        if player_id == self.turn:
            self.nodes[(x, y)] = player_id + 1
            if self.isWinningMove(x, y, player_id+1):
                if player_id:
                    self.player1.Send(
                        {"action": "win", "winning_line": self.winning_line, "torf": True})
                    self.player0.Send(
                        {"action": "lose", "winning_line": self.winning_line, "torf": False})
                else:
                    self.player0.Send(
                        {"action": "win", "winning_line": self.winning_line, "torf": True})
                    self.player1.Send(
                        {"action": "lose", "winning_line": self.winning_line, "torf": False})

            else:
                self.turn = 0 if self.turn else 1
                self.player1.Send(
                    {"action": "yourturn", "torf": True if self.turn == 1 else False})
                self.player0.Send(
                    {"action": "yourturn", "torf": True if self.turn == 0 else False})
                # send data and turn data to each player
                self.player0.Send(data)
                self.player1.Send(data)

    def isWinningMove(self, x, y, target):
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
                if y > 0 and self.nodes[(x, y-1)] == target and (x, y-1) not in seen:
                    stack.append((x, y-1))
                    seen.add((x, y-1))
                    count += 1

                if y + 1 < self.num_of_cols and self.nodes[(x, y+1)] == target and (x, y+1) not in seen:
                    stack.append((x, y+1))
                    seen.add((x, y+1))
                    count += 1
                x, y = stack.pop()

        if direction == 'left_right':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x > 0 and self.nodes[(x-1, y)] == target and (x-1, y) not in seen:
                    stack.append((x-1, y))
                    seen.add((x-1, y))
                    count += 1

                if x + 1 < self.num_of_rows and self.nodes[(x+1, y)] == target and (x+1, y) not in seen:
                    stack.append((x+1, y))
                    seen.add((x+1, y))
                    count += 1
                x, y = stack.pop()

        if direction == 'up_left':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x + 1 < self.num_of_cols and y + 1 < self.num_of_cols and self.nodes[(x+1, y+1)] == target and (x+1, y+1) not in seen:
                    stack.append((x+1, y+1))
                    seen.add((x+1, y+1))
                    count += 1

                if x > 0 and y > 0 and self.nodes[(x-1, y-1)] == target and (x-1, y-1) not in seen:
                    stack.append((x-1, y-1))
                    seen.add((x-1, y-1))
                    count += 1
                x, y = stack.pop()

        if direction == 'down_right':
            stack.append((x, y))
            seen.add((x, y))
            while stack:
                if x > 0 and y + 1 < self.num_of_cols and self.nodes[(x-1, y+1)] == target and (x-1, y+1) not in seen:
                    stack.append((x-1, y+1))
                    seen.add((x-1, y+1))
                    count += 1

                if x + 1 < self.num_of_cols and y > 0 and self.nodes[(x+1, y-1)] == target and (x+1, y-1) not in seen:
                    stack.append((x+1, y-1))
                    seen.add((x+1, y-1))
                    count += 1
                x, y = stack.pop()

        if count == 5:
            self.winning_line = list(seen)
            return count
        return None


print("STARTING SERVER ON LOCALHOST")
address = input("Host:Port (localhost:8000): ")
if not address:
    host, port = "localhost", 8000
else:
    host, port = address.split(":")

myserver = MyServer(localaddr=(host, int(port)))
while True:
    myserver.Pump()
    sleep(0.01)

from django.test import TestCase
from django.conf import settings

NUMBER_OF_ROW=settings.NUMBER_OF_ROW
NUMBER_OF_COL=settings.NUMBER_OF_COL

GAME_TYPE_SINGLE=settings.GAME_TYPE_SINGLE
GAME_TYPE_PVP=settings.GAME_TYPE_PVP

AI_ID=settings.AI_ID

def create_empty_playboard():
    return [[0 for _ in range(NUMBER_OF_COL)] for _ in range(NUMBER_OF_ROW)]

class GameObjectTests(TestCase):
    def test_create_game(self):
        game_board = create_empty_playboard()
        self.assertEqual(len(game_board), NUMBER_OF_ROW)
        self.assertEqual(len(game_board[0]), NUMBER_OF_COL)
        pass

    def test_winning_line(self):
        pass
    def test_validate_move(self):
        pass
    def test_(self):
        pass
    def test_(self):
        pass


class MinimaxAlgorithmTests(TestCase):
    def test_create_game(self):
        pass

class SocketIOTests(TestCase):
    def test_start_game(self):
        pass


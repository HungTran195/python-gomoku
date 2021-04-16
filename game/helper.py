from random import random
from .config import Config
from .minimax import *
import re


class Helper:
    def __init__(self) -> None:
        pass

    def convert_index_to_2D(index):
        index = int(index)
        row = index // Config.NUM_COL
        col = index % Config.NUM_COL
        return [row, col]

    def convert_index_to_1D(index):
        return index[0] * Config.NUM_COL + index[1]

    def generate_game_id():
        id = random()
        return int(id*100000000)

    def next_move_minimax(game, move_index):
        return generate_next_move(game, move_index)

    def get_game_id_from_raw_text(game_id):
        '''Get game id by removing special characters and verify that room exists'''
        # remove some special charaters used in referenced url
        game_id = re.sub(r"[?|#]+.*", "", game_id)
        # convert game_id to integer and remove any non-number characters
        game_id = int(re.sub(r"[^0-9]+", " ", game_id))
        return game_id

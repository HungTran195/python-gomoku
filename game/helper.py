from random import random
from .config import Config
from .game import Game
import re


def generate_game_id():
    id = random()
    return int(id*100000000)


def get_game_id(game_id, all_games):
    '''Get game id by removing special characters and verify that room exists'''
    # remove some special charaters used in referenced url
    game_id = re.sub(r"[?|#]+.*", "", game_id)
    # convert game_id to integer and remove any non-number characters
    game_id = int(re.sub(r"[^0-9]+", " ", game_id))
    if all_games.get(game_id) is not None:
        return game_id
    return False

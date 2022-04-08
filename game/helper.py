from random import random
from .minimax import generate_next_move
from django.conf import settings

NUMBER_OF_ROW=settings.NUMBER_OF_ROW
NUMBER_OF_COL=settings.NUMBER_OF_COL
MAX_NUMBER_OF_ROOM=settings.MAX_NUMBER_OF_ROOM
AI_ID= settings.AI_ID

class Helper:
    def __init__(self) -> None:
        pass

    def generate_random_number():
        """
        Generate a random number from 0 -> 100.000.000
        """
        number = random()
        return int(number*MAX_NUMBER_OF_ROOM)

    def next_move_minimax(game, move_index):
        return generate_next_move(game, move_index)
    
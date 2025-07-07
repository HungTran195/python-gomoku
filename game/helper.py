from random import random
from typing import Optional, Tuple
from .minimax import generate_next_move
from django.conf import settings

NUMBER_OF_ROW = settings.NUMBER_OF_ROW
NUMBER_OF_COL = settings.NUMBER_OF_COL
MAX_NUMBER_OF_ROOM = settings.MAX_NUMBER_OF_ROOM
AI_ID = settings.AI_ID

class Helper:
    """Helper class for game utilities and AI move generation"""
    
    def __init__(self) -> None:
        pass

    @staticmethod
    def generate_random_number() -> int:
        """
        Generate a random number from 0 to MAX_NUMBER_OF_ROOM
        :return: random integer
        """
        number = random()
        return int(number * MAX_NUMBER_OF_ROOM)

    @staticmethod
    def next_move_minimax(game, move_index: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Generate next AI move using minimax algorithm
        :param game: Game instance
        :param move_index: 2D coordinates of the last move
        :return: next move coordinates or None if no valid move
        """
        return generate_next_move(game, move_index)
    
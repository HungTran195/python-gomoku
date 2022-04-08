from ctypes.wintypes import WIN32_FIND_DATAA
from random import random

from .minimax import *
import re
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

    def closed_game(active_games, player_id):
        """
        If player leaves a game, remove that game id from list of active games and destroy that game object
        """
        for game_id, game in active_games.items():
            if game.id_to_turn.get(player_id) is not None:
                active_games.pop(game_id)
                del game
                return True, game_id

    @classmethod
    def generate_new_room_id(cls, active_games):
        """
        Generate a new game ID
        """
        pass

    def is_valid_move(move_index):
        pass

    def next_move_minimax(game, move_index):
        return generate_next_move(game, move_index)

    def get_game_id_from_raw_text(game_id):
        """
        Get game id by removing special characters and verify that room exists
        """
        # remove some special charaters used in referenced url
        game_id = re.sub(r"[?|#]+.*", "", game_id)
        # convert game_id to integer and remove any non-number characters
        game_id = int(re.sub(r"[^0-9]+", " ", game_id))
        return game_id
    
    def play_with_ai(game,player_id, move_index):
        """
        Process move from user and predict the next move of AI
        Return AI's next move and status of current game: ended/continue
        """
        if game.process_move(player_id, move_index):
            # Check if player's move is valid and decide whether it is a winning move
            if game.game_over:
                data = {
                    'status': 'success',
                    'game_over': True,
                    'winner': 1 if game.winning_line != [] else 0,
                    'winning_line': game.winning_line,
                    'move_index': [],
                }

            else:
                # Calculate next move of AI
                move_index = Helper.next_move_minimax(game, move_index)
                game.process_move(AI_ID, move_index)
                if game.game_over:
                    # AI won
                    data = {
                        'status': 'success',
                        'game_over': True,
                        'winner': 2,
                        'winning_line': game.winning_line,
                        'move_index': move_index,
                        
                    }
                else:
                    data = {
                        'status': 'success',
                        'game_over': False,
                        'your_turn': True,
                        'move_index': move_index,
                        
                    }
            return data
        else:
            process_error = {
                'status': 'failed',
                'msg': 'Invalid Move',
            }
            return process_error
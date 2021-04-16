from django.http.response import HttpResponseNotFound
from django.http import HttpResponse
from django.shortcuts import render
from .helper import Helper
from .game import Game
from .config import Config

from urllib.parse import urljoin
import socketio
import re
import os

# Create your views here.
HOST = os.environ.get('HOST_URL', Config.SERVER)
# Used for game sync and user communication
sio = socketio.Server(async_mode=Config.ASYNC_MODE)
ai_id = 'ai0'
# Store all current games
games = {}

'''
Main view when someone visit webpage
'''


def index(request):
    global games  # get full access to global variable games

    # variable to decide how many game ids have been used
    try_times = 0
    while True:
        try_times += 1
        game_id = Helper.generate_game_id()
        # Game id is not in the game list so break the loop
        if games.get(game_id) is None:
            break
        # We only maintain at most 100,000,000 games at a time
        # so we try at most 100000000 times
        if try_times > 100000000:
            game_id = -1
            break
    if game_id > 0:
        url = urljoin(HOST, str(game_id))
    else:
        url = ''

    context = {'room_url': url,
               'board_index': range(Config.NUM_COL * Config.NUM_ROW),
               'host': HOST,
               'is_start_page': True}

    return HttpResponse(render(request, 'game/index.html', context))


'''
Invited view for guest, used in PvP mode
'''


def invited_game(request, game_id):
    global games  # get full access to global variable games
    player_name = ''

    if games.get(int(game_id)) is None:
        return HttpResponseNotFound('<h1>Page not found! Check your link</h1>')

    game = games[int(game_id)]  # get game object from the list of all games

    # get player name to display on screen for invited player
    for _, name in game.id_to_name.items():
        player_name = name

    context = {'host': HOST,
               'board_index': range(Config.NUM_COL * Config.NUM_ROW),
               'player_name': player_name,
               'is_start_page': False}

    return HttpResponse(render(request, 'game/invited.html', context))


'''
Socket listener function
Handle start game event for PvP mode or AI mode
:param sid: player's ID
:param data: dict. Contain informatione:
    - game_type: 'ai' or 'human'
    - game_id: unique game id
    - player_name: player's nick name (in PvP mode)
    - is_host: true/false. Decide who created the room and has 1st turn (in PvP mode)
'''


@sio.event
def start_game(sid, data):
    global games  # get full access to global variable games
    game_type = data.get('game_type')

    # Remove any non-number charater in received game_id
    game_id = Helper.get_game_id_from_raw_text(
        data.get('game_id'))
    err_msg = ''

    if not game_id:
        err_msg = 'Room does not exist!'
    else:
        if game_type == 'ai':
            player_name = 'Default'
            game = Game(game_id)
            game.type_opponent = 'ai'
            game.create_new_game(sid, player_name)
            game.create_new_game(ai_id, 'Computer')
            sio.enter_room(sid, game_id)

            games[game_id] = game

        elif game_type == 'human':
            player_name = data['player_name']
            is_host = data['is_host']

            # If there is no player name, create one
            if not player_name:
                player_name = 'Default'

            # First player(host) will create new game object with an unique game ID
            # this game object will be added to list all games variable
            if is_host and games.get(game_id) is None:
                games[game_id] = Game(game_id)

            game = games[game_id]

            # If room has more than 2 players, raise error
            if len(game.id_to_turn) > 1:
                err_msg = 'Room is full!'

            #  Create or update current game with player name and turn
            else:
                # assign player's id with its name
                game.create_new_game(sid, player_name)
                sio.enter_room(sid, game_id)

                # start game when we have 2 players
                if len(game.id_to_turn) == 2:
                    for id, turn in game.id_to_turn.items():
                        sid_opponent = game.id_to_opponent[id]
                        send_data = {'is_turn': turn,
                                     'opponent_name': game.id_to_name[sid_opponent]
                                     }
                        # Send data to player's address to start game
                        sio.emit('start_PvP_game', send_data, room=id)

    # Send a message with information of error
    # if there is an error in processing received data
    if err_msg:
        sio.emit('start_PvP_game', {'err_msg': err_msg}, room=sid)


'''
Socket listener function
Function used to process all moves happening in game (PvP or AI).
Send move index to each player's device and end game if there is any winner.
:param sid: address of the sender
:param data: dict. Contain information:
    - move_index: 1D-array indexed move
    - game_id: unique game id
'''


@ sio.event
def move(sid, data):
    game_id, move_index_1D = int(data['game_id']), int(data['move_index'])
    is_winner = 0
    err_msg = ''
    # Number of replied message sent to player
    # when a message is received
    loop_counter = 1
    # No game object can be found, send a error message
    if not games.get(game_id):
        err_msg = 'Something went wrong'
        sio.emit('move', err_msg, room=game_id)
    else:
        game = games[game_id]

        is_play_with_ai = game.type_opponent == 'ai'
        # In AI mode, each move of player will received 2 message
        # 1st msg is the current move and 2nd msg is AI's move
        if is_play_with_ai:
            loop_counter = 2

        # variable decide the current move is "X" or "O"
        turn_of_current_move = game.id_to_turn[sid]

        # Convert 1-D array indexed to 2-D array indexed
        move_index_2D = Helper.convert_index_to_2D(move_index_1D)

        # Procees move to decide whether it is a valid move
        if game.process_move(sid, move_index_2D):
            while loop_counter > 0:
                # Process move for 2 player
                for id, turn in game.id_to_turn.items():
                    if turn < 2:
                        turn = 1 if game.current_turn == turn else 0
                    #  Current turn is 2 when one player won
                    #  stop process any other move
                    if game.current_turn == 2:
                        if id == game.winner_id:
                            is_winner = 1
                        else:
                            is_winner = 0
                        turn = 2

                    send_data = {'move_index': move_index_1D,
                                 'is_winner': is_winner,
                                 'winning_line_index': game.winning_line_index,
                                 'turn_of_current_move': turn_of_current_move,
                                 'is_turn': turn}

                    # Only send message via socketIO if the destination is player's ID
                    if id != ai_id:
                        sio.emit('move', send_data, room=id)

                loop_counter -= 1
                # Predict computer's next move in AI mode
                if is_play_with_ai and loop_counter > 0 and game.current_turn < 2:
                    # Generate next move using MiniMax with alpha beta pruning algorithm
                    next_move_index_2D = Helper.next_move_minimax(
                        game, move_index_2D)

                    # Procees next AI's move to decide whether it is a valid move
                    if game.process_move(ai_id, next_move_index_2D):
                        # Convert predicted index to 1-D to displayed on web page
                        move_index_1D = Helper.convert_index_to_1D(
                            next_move_index_2D)
                        # variable decide the current move is "X" or "O"
                        turn_of_current_move = game.id_to_turn[ai_id]
                    # Handle in case of invalid move
                    else:
                        pass


'''
Socket listener function
Function used to request for a replay match
:param sid: address of the sender
:param data: dict. Contain information :
    - game_id: unique game id
'''


@ sio.event
def request_replay(sid, data):
    # Remove any non-number charater in received game_id
    game_id = Helper.get_game_id_from_raw_text(
        data.get('game_id'))
    status = err_msg = ''

    if not game_id:
        status = 'failed'
        err_msg = 'There is something wrong, please reload page!'

    elif games.get(game_id) is None:
        status = 'failed'
        err_msg = 'Room does not exist!'
    else:
        status = 'success'
        game = games[game_id]
        if game.type_opponent == 'human':
            opponent_id = game.id_to_opponent[sid]
            sio.emit('request_replay', '', room=opponent_id)
        else:
            game.reset_game()
            send_data = {'is_turn': 1}
            sio.emit('replay', send_data, room=sid)

    if err_msg:
        sio.emit('request_replay', {'status:': status,
                                    'err_msg': err_msg}, room=sid)


'''
Socket listener function
Function used to create a replay match of PvP game
:param sid: address of the sender
:param data: dict. Contain information :
    - game_id: unique game id
'''


@ sio.event
def accept_replay(sid, data):
    game_id = data['game_id']
    game_id = int(re.sub("[^0-9]+", " ", game_id))
    status = err_msg = ''

    if not game_id:
        status = 'failed'
        err_msg = 'There is something wrong, please reload page!'

    elif games.get(game_id) is None:
        status = 'failed'
        err_msg = 'Room does not exist!'
    else:
        status = 'success'
        game = games[game_id]
        # Reset game turn and game's matrix
        game.reset_game()

        # Reverse turn
        # Player 2 plays first instead of player 1
        for id_to_turn, player_turn in game.id_to_turn.items():
            turn = 0 if player_turn else 1
            game.id_to_turn[id_to_turn] = turn

            send_data = {'is_turn': turn}
            sio.emit('replay', send_data, room=id_to_turn)

    if err_msg:
        sio.emit('request_replay', {'status:': status,
                                    'err_msg': err_msg}, room=sid)


@ sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


@ sio.event
def connect(sid, environ):
    pass


@ sio.event
def disconnect(sid):
    global games
    for game_id, game in games.items():
        if game.id_to_turn.get(sid) is not None:
            games.pop(game_id)
            msg = 'Your friend just left the game!'
            send_data = {'is_turn': 2,
                         'msg': msg}
            sio.emit('end_game', send_data, room=game_id)
            break
    # print('Client disconnected', sid)

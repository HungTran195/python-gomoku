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


def index(request):
    global games

    try_times = 0
    while True:
        try_times += 1
        game_id = Helper.generate_game_id()
        if games.get(game_id) is None:
            break
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


def invited_game(request, game_id):
    global games
    player_name = ''
    if games.get(int(game_id)) is None:
        return HttpResponseNotFound('<h1>Page not found! Check your link</h1>')

    game = games[int(game_id)]

    for _, name in game.id_to_name.items():
        player_name = name

    context = {'host': HOST,
               'board_index': range(Config.NUM_COL * Config.NUM_ROW),
               'player_name': player_name,
               'is_start_page': False}

    return HttpResponse(render(request, 'game/invited.html', context))


@ sio.event
def play_with_ai(sid, data):
    ''' Socket listener function
    Function used to create a "Player vs AI" game object
    Input:
        - sid: player's ID
        - data['player_name']: player name
        - data['game_id']: unique game ID
    '''
    global games

    # player_name = data['player_name']
    player_name = 'Default'
    # Get game id from received data
    game_id = Helper.get_game_id_from_raw_text(
        data['game_id'], all_games=games)
    if not game_id:
        status = 'failed'
        err_msg = 'Room does not exist!'
        sio.emit('play_with_ai', {'status:': status,
                                  'err_msg': err_msg}, room=sid)
        return

    game = Game(game_id)
    game.type_opponent = 'ai'
    game.create_new_game(sid, player_name)
    game.create_new_game(ai_id, 'Your Computer')
    sio.enter_room(sid, game_id)

    games[game_id] = game


@ sio.event
def start_PvP_game(sid, data):
    ''' Socket listener function
    This function is used to create a new "player vs player"(PvP) game
    After process data, emit a message to player's device.
    Start the game if there are 2 players.
    Input:
        - sid: player's ID
        - data['player_name']: player name
        - data['is_host']: true/false, specify who create the room
        - data['game_id']: unique game ID
    '''
    global games
    err_msg = ''
    player_name = data['player_name']
    is_host = data['is_host']

    if not player_name:
        player_name = 'Default'

    # Get game ID from received data
    game_id = Helper.get_game_id_from_raw_text(
        data['game_id'], all_games=games)

    if not game_id:
        # If game_id is not a number, raise error
        status = 'failed'
        err_msg = 'Room does not exist!'

    else:
        if is_host and games.get(game_id) is None:
            # Create new game object when game ID is unique and there is a Host
            games[game_id] = Game(game_id)

        game = games[game_id]
        if len(game.id_to_turn) > 1:
            # If more than 2 players, raise error
            status = 'failed'
            err_msg = 'Room is full!'
        else:
            status = 'success'

            ''' Create a new game with player name and turn
                or update existing game with the second opponent'''
            game.create_new_game(sid, player_name)
            sio.enter_room(sid, game_id)

            if len(game.id_to_turn) == 2:
                for id, turn in game.id_to_turn.items():
                    sid_opponent = game.id_to_opponent[id]
                    send_data = {'status:': status,
                                 'is_turn': turn,
                                 'opponent': game.id_to_name[sid_opponent]
                                 }
                    sio.emit('start_PvP_game', send_data, room=id)

    if err_msg:
        sio.emit('start_PvP_game', {'status:': status,
                                    'err_msg': err_msg}, room=sid)


@ sio.event
def move(sid, data):
    ''' Socket listener function
    Function used to process all moves happening in game (PvP or Player vs AI).
    Send move index to each player's device and end game if there is any winner.
    Input:
        - sid: player's ID
        - data['move_index']: 1D-array indexed move
        - data['game_id']: unique game ID
    '''
    game_id, move_index_1D = int(data['game_id']), int(data['move_index'])
    is_winner = 0
    err_msg = ''
    loop_counter = 1
    if not games.get(game_id):
        err_msg = 'Something went wrong'
        sio.emit('move', err_msg, room=game_id)
    else:
        game = games[game_id]
        is_play_with_ai = game.type_opponent == 'ai'
        if is_play_with_ai:
            loop_counter = 2
        turn_of_current_move = game.id_to_turn[sid]
        move_index_2D = Helper.convert_index_to_2D(move_index_1D)

        if game.process_move(sid, move_index_2D):
            while loop_counter > 0:
                # Process move for PvP game
                for id, turn in game.id_to_turn.items():
                    if turn < 2:
                        turn = 1 if game.current_turn == turn else 0
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
                    if id != ai_id:
                        sio.emit('move', send_data, room=id)

                loop_counter -= 1

                if is_play_with_ai and loop_counter > 0:
                    # Generate next move for "vs AI" game
                    next_move_index_2D = Helper.next_move_minimax(
                        game, move_index_2D)
                    move_index_1D = Helper.convert_index_to_1D(
                        next_move_index_2D)
                    turn_of_current_move = game.id_to_turn[ai_id]


@ sio.event
def request_replay(sid, data):
    ''' Socket listener function
    Function used to request for a replay match of PvP game
    Input:
        - sid: player's ID
        - data['game_id']: unique game ID
    '''
    global games

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


@ sio.event
def accept_replay(sid, data):
    ''' Socket listener function
    Function used to create a replay match of PvP game
    Turn will be reversed.
    Input:
        - sid: player's ID
        - data['game_id']: unique game ID
    '''
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

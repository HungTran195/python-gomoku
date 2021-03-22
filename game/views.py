from django.http.response import HttpResponseNotFound
from django.http import HttpResponse
from django.shortcuts import render
from .helper import generate_game_id, get_game_id
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

# Store all available games
games = {}


def index(request):
    global games

    while True:
        game_id = generate_game_id()
        if games.get(game_id) is None:
            game = Game(game_id)
            games[game_id] = game
            break
    url = urljoin(HOST, str(game_id))

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

    return HttpResponse(render(request, 'game/index.html', context))


@ sio.event
def start_game(sid, data):
    global games
    err_msg = ''
    player_name = data['player_name']
    if not player_name:
        player_name = 'Default'
    # Get game id from received data
    game_id = get_game_id(data['game_id'], all_games=games)

    if not game_id:
        status = 'failed'
        err_msg = 'Room does not exist!'

    else:
        game = games[game_id]
        if len(game.id_to_turn) > 1:
            # There are 2 players => room is full
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
                                 'turn': turn,
                                 'opponent': game.id_to_name[sid_opponent]
                                 }
                    sio.emit('start_game', send_data, room=id)

    if err_msg:
        sio.emit('start_game', {'status:': status,
                                'err_msg': err_msg}, room=sid)


@ sio.event
def move(sid, data):
    game_id, move_index = int(data['game_id']), int(data['move_index'])
    is_winner = 0
    err_msg = ''

    if not games.get(game_id):
        err_msg = 'Something went wrong'
        sio.emit('move', err_msg, room=game_id)
    else:
        game = games[game_id]
        if sid in game.id_to_turn and game.id_to_turn[sid] == game.current_turn:
            if game.process_move(sid, move_index):
                for id, turn in game.id_to_turn.items():
                    if turn < 2:
                        turn = 1 if game.current_turn == turn else 0
                    if game.winning_line_index is not None:
                        if id == game.winner_id:
                            is_winner = 1
                        else:
                            is_winner = 0
                    data = {'move_index': move_index,
                            'is_winner': is_winner,
                            'winning_line_index': game.winning_line_index,
                            'move_id': game.id_to_turn[sid],
                            'turn': turn}
                    sio.emit('move', data, room=id)


@ sio.event
def request_replay(sid, data):
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
        opponent_id = game.id_to_opponent[sid]
        sio.emit('request_replay', '', room=opponent_id)

    if err_msg:
        sio.emit('request_replay', {'status:': status,
                                    'err_msg': err_msg}, room=sid)


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
        game.reset_game()
        # Reverse turn
        # Player 2 plays first instead of player 1

        for id_to_turn, player_turn in game.id_to_turn.items():
            turn = 0 if player_turn else 1
            game.id_to_turn[id_to_turn] = turn
            data = {'turn': turn}
            sio.emit('replay', data, room=id_to_turn)

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
            data = {'turn': 2,
                    'msg': msg}
            sio.emit('end_game', data, room=game_id)
            break
    # print('Client disconnected', sid)

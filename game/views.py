from django.http.response import HttpResponseNotFound
from django.shortcuts import render
from django.http import HttpResponse
import socketio
from django.http import HttpResponseNotFound
from urllib.parse import urljoin
from .helper import Game, generate_game_id
import re
import os

# Create your views here.

NUM_COL = 18
NUM_ROW = 20
HOST = os.environ.get('HOST_URL', 'http://127.0.0.1:8000/')
turn = 1
board = [[0 for _ in range(NUM_COL)] for _ in range(NUM_ROW)]

ASYNC_MODE = 'eventlet'
sio = socketio.Server(async_mode=ASYNC_MODE)
thread = None

games = {}

play_board_1D_array = {}
for i in range(NUM_ROW):
    for j in range(NUM_COL):
        play_board_1D_array[i*NUM_ROW + j] = ''


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(20)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')


def index(request):
    global thread
    global games

    if thread is None:
        thread = sio.start_background_task(background_thread)

    while True:
        game_id = generate_game_id()
        if games.get(game_id) is None:
            game = Game(game_id)
            games[game_id] = game
            break
    url = urljoin(HOST, str(game_id))

    context = {'play_board_1D_array': play_board_1D_array,
               'turn': turn,
               'room_url': url,
               'is_start_page': True}

    return HttpResponse(render(request, 'game/index.html', context))


def invited_game(request, game_id):
    global games

    if games.get(int(game_id)) is None:
        return HttpResponseNotFound('<h1>Page not found! Check your link</h1>')

    game = games[int(game_id)]
    player_name = 'Tony'

    context = {'play_board_1D_array': play_board_1D_array,
               'turn': turn,
               'player_name': player_name,
               'is_start_page': False}

    return HttpResponse(render(request, 'game/index.html', context))


@ sio.event
def start_game(sid, game_id):
    global games
    err_msg = ''
    game_id = int(re.sub("[^0-9]+", " ", game_id))
    data = None
    if not game_id:
        status = 'failed'
        err_msg = 'There is something wrong, please reload page!'

    elif games.get(game_id) is None:
        status = 'failed'
        err_msg = 'Room does not exist!'

    else:
        status = 'success'
        game = games[game_id]

        if len(game.player_id) > 1:
            err_msg = 'Room is full!'
        else:
            game.create_new_game(game_id, sid)
            sio.enter_room(sid, game_id)

            if len(game.player_id) == 2:
                for id, turn in game.player_id.items():
                    data = {'status:': status,
                            'turn': turn}
                    sio.emit('start_game', data, room=id)

    if err_msg:
        sio.emit('start_game', {'status:': status,
                                'err_msg': err_msg}, room=sid)


@ sio.event
def move(sid, data):
    game_id, move_index = int(data['game_id']), int(data['move_index'])
    is_winner = 0
    if not games.get(game_id):
        err_msg = 'Something went wrong'
        sio.emit('move', err_msg, room=game_id)
    else:
        game = games[game_id]
        if sid in game.player_id and game.player_id[sid] == game.turn:
            if game.process_move(sid, move_index):
                for id, turn in game.player_id.items():
                    if turn < 2:
                        turn = 1 if game.turn == turn else 0
                    if game.winning_line is not None:
                        if id == game.winner:
                            is_winner = 1
                        else:
                            is_winner = 0
                    data = {'move_index': move_index,
                            'is_winner': is_winner,
                            'winning_line': game.winning_line,
                            'move_id': game.player_id[sid],
                            'turn': turn}
                    sio.emit('move', data, room=id)


@ sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


@ sio.event
def connect(sid, environ):
    category = 'connect'
    data = {'category': category, 'status': 'Connected',
            'count': 0}
    sio.emit('my_response', {'data': data}, room=sid)


@ sio.event
def disconnect(sid):
    global games
    for game_id, game in games.items():
        if game.player_id.get(sid) is not None:
            game.close_game()
            msg = 'Your friend just left the game!'
            data = {'turn': 2,
                    'msg': msg}
            sio.emit('end_game', data, room=game_id)
            break
    # print('Client disconnected', sid)

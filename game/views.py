from django.http.response import HttpResponseNotFound
from django.shortcuts import render
from django.http import HttpResponse
# from .models import Game
import socketio
from django.http import HttpResponseNotFound
from urllib.parse import urljoin
from .helper import Game, get_room_id, generate_game_id
import os
import re

# Create your views here.

NUM_ROW = 20
NUM_COL = 20
HOST = 'http://127.0.0.1:8000/'
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

basedir = os.path.dirname(os.path.realpath(__file__))


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(20)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')
        print('COUNT', count)
        if count == 100:
            break


def index(request):
    global thread
    global games

    if thread is None:
        thread = sio.start_background_task(background_thread)

    while True:
        id = generate_game_id()
        if games.get(id) is None:
            game = Game(id)
            games[id] = game
            break
    url = urljoin(HOST, str(id))

    context = {'play_board_1D_array': play_board_1D_array,
               'turn': turn,
               'room_url': url,
               'is_start_page': True, }

    return HttpResponse(render(request, 'game/index.html', context))
    # return HttpResponse(open(os.path.join(basedir, 'templates/game/index.html')))


def invited_game(request, game_id):
    global games

    if games.get(int(game_id)) is None:
        return HttpResponseNotFound('<h1>Page not found! Check your link</h1>')

    game = games[int(game_id)]
    player_name = 'Tony'

    play_status = True
    context = {'play_board_1D_array': play_board_1D_array,
               'turn': turn,
               'play_status': play_status,
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

        print('\n Game', game.player_id, err_msg)

    if err_msg:
        sio.emit('start_game', {'status:': status,
                                'err_msg': err_msg}, room=sid)


@ sio.event
def move(sid, data):
    print('\nmove', sid,  data)
    game_id, move_index = int(data['game_id']), int(data['move_index'])

    if not games.get(game_id):
        err_msg = 'Something went wrong'
        sio.emit('move', err_msg, room=game_id)

    else:
        game = games[game_id]
        print('\ngame', game.player_id, game.turn)
        if sid in game.player_id and game.player_id[sid] == game.turn:
            if game.process_move(sid, move_index):
                for id, turn in game.player_id.items():
                    if turn < 2:
                        turn = 1 if game.turn == turn else 0
                    data = {'move_index': move_index,
                            'is_winner': game.winner,
                            'winning_line': game.winning_line,
                            'move_id': game.player_id[sid],
                            'turn': turn}
                    print('\n data', data, turn)
                    sio.emit('move', data, room=id)

    # sio.emit('move', {'data': data}, room=message['room'])


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
    # global game
    # if game:
    #     if sid in game.player_id:
    #         # game.player_id.remove(sid)
    #         game.player_id.pop(sid, None)
    print('\nDis', sid)
    print('Client disconnected')


# For future use

@ sio.event
def my_event(sid, message):
    print('my_evetn')
    sio.emit('my_response', {'data': message['data']}, room=sid)


@ sio.event
def my_broadcast_event(sid, message):
    print(message['data'])
    sio.emit('my_response', {'data': message['data']})


@ sio.event
def leave(sid, message):
    sio.leave_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Left room: ' + message['room']},
             room=sid)


@ sio.event
def close_room(sid, message):
    sio.emit('my_response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'])
    sio.close_room(message['room'])


# @ sio.event
# def join(sid, message):
#     print('\njoin', sid)
#     current_game_state = []
#     category = 'join_room'
#     room_name = message['room_name']
#     game_id = get_room_id(room_name)
#     global game
#     if not game:
#         game = Game(game_id)
#     if game_id != game.game_id:
#         status = 'Wrong Room!'
#     elif len(game.player_id) > 2:
#         status = 'Room is full!'
#     else:
#         game.create_new_game(game_id, sid)
#         status = 'Entered room ' + message['room_name']
#         current_game_state = game.get_current_game_state()

#     data = {'category': category,
#             'status:': status, 'game_state': current_game_state}

#     sio.enter_room(sid, message['room_name'])
#     sio.emit('my_response', {'data': data},
#              room=sid)

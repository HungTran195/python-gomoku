from django.http.response import HttpResponseNotFound
from django.http import HttpResponse
from django.shortcuts import render
from .helper import Helper
from .game import Game
import socketio

from django.conf import settings

NUMBER_OF_ROW=settings.NUMBER_OF_ROW
NUMBER_OF_COL=settings.NUMBER_OF_COL

GAME_TYPE_SINGLE=settings.GAME_TYPE_SINGLE
GAME_TYPE_PVP=settings.GAME_TYPE_PVP
MAX_NUMBER_OF_ROOM=settings.MAX_NUMBER_OF_ROOM

REMATCH_REQUEST_COMMAND = 'request'
REMATCH_ACCEPT_COMMAND = 'accept'
REMATCH_START_COMMAND = 'start_rematch'

AI_ID=settings.AI_ID

HOST = settings.SERVER

# Used for game sync and user communication
sio = socketio.Server(async_mode=settings.ASYNC_MODE)

# Store all current games
games = {}

def index(request):
    """
    Main view when someone visit webpage
    """
    global games  
    # variable to decide how many game ids have been used
    try_times = 0
    while True:
        try_times += 1
        game_id = Helper.generate_random_number()

        if games.get(game_id) is None:
            break
    
        if try_times >= MAX_NUMBER_OF_ROOM:
            game_id= -1       

    context = {
        'game_id': game_id,
        'num_of_cells_background': range(14),
        'num_of_cells_board': range(15),
    }

    return HttpResponse(render(request, 'game/board_game.html', context))


@sio.event
def init_game(sid, data):
    """
    Socket listener function
    Handle start game event for PvP mode or AI mode

    @param sid: address of the sender created by socket IO
    @param data: dictionary. Contains:
        - game_type: 'single' or 'PvP'
        - game_id: unique game id
        - player_name: player's nick name
    """
    global games  
    game_type = data.get('gameType')
    player_name = data.get('playerName')

    # Remove any non-number charater in received game_id
    # game_id = Helper.get_game_id_from_raw_text(
    #     data.get('game_id'))
    game_id= data.get('gameID')
    error_msg = ''

    if not game_id:
        error_msg = 'Missing room ID'
    elif games.get(game_id):
        error_msg = 'Cannot create, room exist'
    else:
        if game_type == GAME_TYPE_SINGLE:
            # Create game object 
            game = Game(game_id, game_type)
            game.add_player(sid, player_name)
            game.add_player(AI_ID, 'Computer')
            sio.enter_room(sid, game_id)

            games[game_id] = game
            sio.emit('start_game', {'status':'success'}, room=sid)
            return None

        elif game_type == GAME_TYPE_PVP:
            player_name = data['playerName']

            # Create game object 
            game = Game(game_id, game_type)
            game.add_player(sid, player_name)
            games[game_id] = game

            sio.enter_room(sid, game_id)
        else:
            error_msg = 'Unrecognized game type'

    if error_msg:
        data= {
            'status': 'failed',
            'error_msg': error_msg,
        }
        sio.emit('error', data, room=sid)
    

@sio.event
def join_current_game(sid, data):
    """
    Socket listener function
    Join current PvP game
    @param sid: address of the sender created by socket IO
    @param data: dictionary. Contains:
        - game_id: unique game id
        - player_name: player's nick name
    """

    global games 
    game_id= data.get('gameID')
    player_name = data.get('playerName')
    error_msg = ''

    if not game_id:
        error_msg = 'Missing room ID'

    elif not games.get(game_id):
        error_msg = 'Cannot join, room does not exist'

    else:
        game = games.get(game_id)
        game.add_player(sid, player_name)
        sio.enter_room(sid, game_id)
        data = {
            'status':'success',
            'player_names': {
                'player_1': game.player_names[0],
                'player_2': game.player_names[1],
            },
            'turn': game.current_turn
        }
        
        sio.emit('start_game', data, room=game_id)

    if error_msg:
        data= {
            'status': 'failed',
            'error_msg': error_msg,
        }
        sio.emit('error', data, room=sid)


@ sio.event
def move(sid, data):
    """
    Socket listener function
    Function used to process all moves happening in game (PvP or AI).
    Send move index to each player's device and end game if there is any winner.
    @param sid: address of the sender
    @param data: dict. Contains information:
        - move_index: 2D-array indexed move
        - game_id: unique game id
    """

    game_id = data['gameID']
    player_id = sid
    error_msg = ''

    if not games.get(game_id):
        # No game object can be found, send an error message
        error_msg = 'Room is not exist',
    elif 'moveIndex' not in data:
        error_msg = 'No move recorded'
    else:
        game = games[game_id]
        move_index = data['moveIndex']
        if game.game_type == GAME_TYPE_SINGLE:
            # AI mode
            data = Helper.play_with_ai(game,player_id,move_index)
            if data['status'] == 'success':
            
                sio.emit('move', data,room=player_id)
            else:
                error_msg = data['msg']
        else:
            if game.process_move(player_id, move_index):
                if game.game_over:
                    # variable store the player index which is the winner
                    winner_index = game.get_player_index(player_id) 
                    data = {
                        'status': 'success',
                        'game_over': True,
                        'winner': winner_index if game.winning_line else False,
                        'winning_line': game.winning_line,
                        'move_index': move_index,
                    }
                    sio.emit('move', data, game_id)

                else:
                    opponent_id = game.get_opponent_id(player_id)
                    data = {
                        'status': 'success',
                        'game_over': False,
                        'move_index': move_index,
                    }
                    sio.emit('move', data, opponent_id)
            else: 
                error_msg = 'Invalid Move'
    
    if error_msg:
        data= {
            'status': 'failed',
            'error_msg': error_msg,
        }
        sio.emit('error', data, room=game_id)


@ sio.event
def rematch(sid, data):
    """
    Socket listener function
    Function used to handel rematch request and response
    @param sid: address of the sender
    @param data: dict. Contains information :
        - game_id: unique game id
        - command: request/accept a rematch
    """
    # Remove any non-number charater in received game_id

    game_id = data.get('gameID')
    command = data.get('command')
    player_id = sid
    error_msg = ''

    if not game_id:
        error_msg = 'There is something wrong, please reload page!'

    elif games.get(game_id) is None:
        error_msg = 'Room does not exist!'
    else:
        game = games[game_id]
        if game.game_type == GAME_TYPE_SINGLE:
            if command == REMATCH_REQUEST_COMMAND: 
                game.rematch()
                data = {
                    'status': 'success',
                    'your_turn': True,
                }
            sio.emit('rematch', data, room=player_id)

        elif game.game_type == GAME_TYPE_PVP:   
            opponent_id = game.get_opponent_id(player_id)
            if command == REMATCH_REQUEST_COMMAND: 
                data = {
                    'status': 'success',
                    'command': REMATCH_REQUEST_COMMAND,
                }
                sio.emit('rematch', data, room=opponent_id)
            elif command == REMATCH_ACCEPT_COMMAND:
                game.rematch()
                if game.number_of_games % 2:
                    # Swap turn between the 2 players base on the number of games
                    # If the number of games is odd, turn will be on player 1
                    # Otherwise, turn will be on player 2
                    player_turn = 1
                    game.current_turn = 1
                else: 
                    player_turn = 2 
                    game.current_turn = 2

                data = {
                    'status': 'success',
                    'command': REMATCH_START_COMMAND,
                    'player_turn': player_turn
                }
                sio.emit('rematch', data, room=game_id)
            else:
                error_msg = 'Unknown command'

    if error_msg:
        data= {
            'status': 'failed',
            'error_msg': error_msg,
        }
        sio.emit('error', data, room=sid)

@ sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


@ sio.event
def connect(sid, environ):
    pass


@ sio.event
def disconnect(sid):
    """
    Socket listener function
    Handle any disconnect of players
    """
    global games
    for game_id, game in games.items():
        if game.player_index.get(sid) is not None:
            games.pop(game_id)
            sio.emit('end_game','', room=game_id)
            break

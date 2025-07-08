"""
FastAPI-compatible game views and Socket.IO event handlers
This module contains all the game logic and Socket.IO event handlers for the Gomoku game
"""

import socketio
import numpy as np
from typing import Dict, Any, Optional, Tuple
from .helper import Helper
from .game import Game
from .minimax import generate_next_move
from config import settings

# Game constants
REMATCH_REQUEST_COMMAND = 'request'
REMATCH_ACCEPT_COMMAND = 'accept'
REMATCH_START_COMMAND = 'start_rematch'

def convert_numpy_types(obj):
    """Convert NumPy types to JSON-serializable types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    return obj

# Store all current games
games: Dict[int, Game] = {}
sio: Optional[socketio.AsyncServer] = None

def set_socketio_server(socketio_server: socketio.AsyncServer) -> None:
    """Set the Socket.IO server instance for use in event handlers"""
    global sio
    sio = socketio_server
async def handle_connect(sid: str, environ: Dict[str, Any]) -> None:
    """Handle client connection"""
    print(f"Client connected: {sid}")
    print(f"Connection environment: {environ}")

async def handle_disconnect(sid: str) -> None:
    """Handle client disconnection"""
    print(f"Client disconnected: {sid}")
    # Clean up games when player disconnects
    for game_id, game in list(games.items()):
        if game.player_index.get(sid) is not None:
            del games[game_id]
            if sio:
                await sio.emit('end_game', '', room=game_id)
            break

async def handle_init_game(sid: str, data: Dict[str, Any]) -> None:
    """
    Handle game initialization
    """
    print(f"init_game called with sid: {sid}, data: {data}")
    if not sio:
        print("Socket.IO server not available")
        return
        
    game_type = data.get('gameType')
    player_name = data.get('playerName')
    game_id = data.get('gameID')
    error_msg = ''

    if not game_id:
        error_msg = 'Missing room ID'
    elif not game_type:
        error_msg = 'Missing game type'
    elif not player_name:
        error_msg = 'Missing player name'
    elif games.get(game_id):
        error_msg = 'Cannot create, room exists'
    else:
        if game_type == settings.game_type_single:
            # Create single player game
            game = Game(game_id, game_type)
            game.add_player(sid, player_name)
            game.add_player(settings.ai_id, 'Computer')
            await sio.enter_room(sid, game_id)
            
            games[game_id] = game
            await sio.emit('start_game', {'status': 'success'}, room=sid)
            return

        elif game_type == settings.game_type_pvp:
            # Create PvP game
            game = Game(game_id, game_type)
            game.add_player(sid, player_name)
            games[game_id] = game
            await sio.enter_room(sid, game_id)
        else:
            error_msg = 'Unrecognized game type'

    if error_msg:
        await sio.emit('error', convert_numpy_types({
            'status': 'failed',
            'error_msg': error_msg,
        }), room=sid)

async def handle_join_current_game(sid: str, data: Dict[str, Any]) -> None:
    """
    Handle joining existing PvP game
    """
    if not sio:
        return
        
    game_id = data.get('gameID')
    player_name = data.get('playerName')
    error_msg = ''

    if not game_id:
        error_msg = 'Missing room ID'
    elif not player_name:
        error_msg = 'Missing player name'
    elif not games.get(game_id):
        error_msg = 'Cannot join, room does not exist'
    else:
        game = games[game_id]
        game.add_player(sid, player_name)
        await sio.enter_room(sid, game_id)
        
        await sio.emit('start_game', {
            'status': 'success',
            'player_names': {
                'player_1': game.player_names[0],
                'player_2': game.player_names[1],
            },
            'turn': game.current_turn
        }, room=game_id)

    if error_msg:
        await sio.emit('error', convert_numpy_types({
            'status': 'failed',
            'error_msg': error_msg,
        }), room=sid)

async def handle_move(sid: str, data: Dict[str, Any]) -> None:
    """
    Handle game moves
    """
    if not sio:
        return
        
    game_id = data.get('gameID')
    player_id = sid
    error_msg = ''

    if not game_id:
        error_msg = 'Missing game ID'
    elif not games.get(game_id):
        error_msg = 'Room does not exist'
    elif 'moveIndex' not in data:
        error_msg = 'No move recorded'
    else:
        game = games[game_id]
        move_index = data['moveIndex']
        
        if game.game_type == settings.game_type_single:
            # Single player mode
            if game.process_move(player_id, move_index):
                if game.game_over:
                    await sio.emit('move', convert_numpy_types({
                        'status': 'success',
                        'game_over': True,
                        'winner': 1 if game.winning_line else 0,
                        'winning_line': game.winning_line,
                        'move_index': [],
                    }), room=player_id)
                else:
                    # AI move
                    ai_move = generate_next_move(game, move_index)
                    print(f"AI move: {ai_move} -- class: {type(ai_move)}")
                    if ai_move:
                        game.process_move(settings.ai_id, ai_move)
                        if game.game_over:
                            await sio.emit('move', convert_numpy_types({
                                'status': 'success',
                                'game_over': True,
                                'winner': 2,
                                'winning_line': game.winning_line,
                                'move_index': ai_move,
                            }), room=player_id)
                        else:
                            await sio.emit('move', convert_numpy_types({
                                'status': 'success',
                                'game_over': False,
                                'your_turn': True,
                                'move_index': ai_move,
                            }), room=player_id)
            else:
                error_msg = 'Invalid Move'
        else:
            # PvP mode
            if game.process_move(player_id, move_index):
                if game.game_over:
                    winner_index = game.get_player_index(player_id)
                    await sio.emit('move', convert_numpy_types({
                        'status': 'success',
                        'game_over': True,
                        'winner': winner_index if game.winning_line else False,
                        'winning_line': game.winning_line,
                        'move_index': move_index,
                    }), room=game_id)
                else:
                    opponent_id = game.get_opponent_id(player_id)
                    await sio.emit('move', convert_numpy_types({
                        'status': 'success',
                        'game_over': False,
                        'move_index': move_index,
                    }), room=opponent_id)
            else:
                error_msg = 'Invalid Move'

    if error_msg:
        await sio.emit('error', convert_numpy_types({
            'status': 'failed',
            'error_msg': error_msg,
        }), room=game_id)

async def handle_rematch(sid: str, data: Dict[str, Any]) -> None:
    """
    Handle rematch requests
    """
    if not sio:
        return
        
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
        if game.game_type == settings.game_type_single:
            if command == REMATCH_REQUEST_COMMAND:
                game.rematch()
                await sio.emit('rematch', {
                    'status': 'success',
                    'your_turn': True,
                }, room=player_id)
        elif game.game_type == settings.game_type_pvp:
            opponent_id = game.get_opponent_id(player_id)
            if command == REMATCH_REQUEST_COMMAND:
                await sio.emit('rematch', {
                    'status': 'success',
                    'command': REMATCH_REQUEST_COMMAND,
                }, room=opponent_id)
            elif command == REMATCH_ACCEPT_COMMAND:
                game.rematch()
                player_turn = 1 if game.number_of_games % 2 else 2
                game.current_turn = player_turn
                
                await sio.emit('rematch', {
                    'status': 'success',
                    'command': REMATCH_START_COMMAND,
                    'player_turn': player_turn
                }, room=game_id)
            else:
                error_msg = 'Unknown command'

    if error_msg:
        await sio.emit('error', convert_numpy_types({
            'status': 'failed',
            'error_msg': error_msg,
        }), room=sid)

async def handle_disconnect_request(sid: str) -> None:
    """Handle disconnect request"""
    if sio:
        await sio.disconnect(sid)

# Game utility functions
def generate_game_id() -> int:
    """
    Generate a unique game ID
    """
    try_times = 0
    while True:
        try_times += 1
        game_id = Helper.generate_random_number()

        if games.get(game_id) is None:
            break
    
        if try_times >= settings.max_number_of_room:
            game_id = -1
            break

    return game_id

def get_game_context() -> Dict[str, Any]:
    """
    Get context data for the game template
    """
    game_id = generate_game_id()
    return {
        'game_id': game_id,
        'num_of_cells_background': range(14),
        'num_of_cells_board': range(15),
    }

def get_active_games() -> Dict[str, Any]:
    """
    Get information about active games
    """
    return {
        'total_games': len(games),
        'games': [
            {
                'id': game_id,
                'type': game.game_type,
                'players': len(game.player_id),
                'moves': game.number_of_moves,
                'game_over': game.game_over
            }
            for game_id, game in games.items()
        ]
    }

def get_health_status() -> Dict[str, Any]:
    """
    Get health status of the application
    """
    return {
        'status': 'healthy',
        'games_active': len(games),
        'version': settings.version
    }

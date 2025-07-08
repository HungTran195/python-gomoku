"""
FastAPI Gomoku Game Application
Main application entry point
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import socketio
import eventlet
import os
from pathlib import Path
from typing import Dict, Any

from config import settings
from game.views import (
    set_socketio_server,
    handle_connect,
    handle_disconnect,
    handle_init_game,
    handle_join_current_game,
    handle_move,
    handle_rematch,
    handle_disconnect_request,
    get_game_context,
    get_active_games,
    get_health_status
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# Create Socket.IO app
socket_app = socketio.ASGIApp(sio, app)

# Setup static files and templates
static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

templates = Jinja2Templates(directory=str(templates_path))

# Set up Socket.IO server in views module
set_socketio_server(sio)

# Socket.IO event handlers - using handlers from views.py
@sio.event
async def connect(sid, environ):
    print(f"Socket.IO connect event: {sid}")
    await handle_connect(sid, environ)

@sio.event
async def disconnect(sid):
    print(f"Socket.IO disconnect event: {sid}")
    await handle_disconnect(sid)

@sio.event
async def init_game(sid, data):
    print(f"Socket.IO init_game event: {sid}, {data}")
    await handle_init_game(sid, data)

@sio.event
async def join_current_game(sid, data):
    print(f"Socket.IO join_current_game event: {sid}, {data}")
    await handle_join_current_game(sid, data)

@sio.event
async def move(sid, data):
    print(f"Socket.IO move event: {sid}, {data}")
    await handle_move(sid, data)

@sio.event
async def rematch(sid, data):
    print(f"Socket.IO rematch event: {sid}, {data}")
    await handle_rematch(sid, data)

@sio.event
async def disconnect_request(sid):
    print(f"Socket.IO disconnect_request event: {sid}")
    await handle_disconnect_request(sid)

# FastAPI routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page route"""
    context = get_game_context()
    return templates.TemplateResponse("board_game.html", {
        "request": request,
        **context
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return get_health_status()

@app.get("/api/games")
async def get_games():
    """API endpoint to get active games"""
    return get_active_games()

# WebSocket endpoint for Socket.IO
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Socket.IO"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:socket_app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    ) 
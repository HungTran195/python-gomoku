#!/usr/bin/env python3
"""
Test Socket.IO connection
"""

import socketio
import asyncio
import time

# Create a Socket.IO client
sio_client = socketio.AsyncClient()

@sio_client.event
async def connect():
    print("Connected to server!")
    
@sio_client.event
async def disconnect():
    print("Disconnected from server!")

@sio_client.event
async def start_game(data):
    print(f"Received start_game: {data}")

@sio_client.event
async def error(data):
    print(f"Received error: {data}")

async def test_connection():
    try:
        # Connect to the server
        await sio_client.connect('http://localhost:8000')
        print("Successfully connected to Socket.IO server")
        
        # Test init_game event
        test_data = {
            'gameID': 12345,
            'gameType': 'single',
            'playerName': 'TestPlayer'
        }
        
        print(f"Sending init_game with data: {test_data}")
        await sio_client.emit('init_game', test_data)
        
        # Wait a bit for response
        await asyncio.sleep(2)
        
        # Disconnect
        await sio_client.disconnect()
        print("Test completed")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 
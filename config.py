"""
Configuration settings for the FastAPI Gomoku game
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings using Pydantic"""
    
    # Application settings
    app_name: str = "Gomoku Game"
    version: str = "2.0.0"
    debug: bool = False
    
    # Game configuration
    number_of_row: int = 15
    number_of_col: int = 15
    game_type_single: str = 'single'
    game_type_pvp: str = 'pvp'
    async_mode: str = 'eventlet'
    max_number_of_room: int = 100000
    ai_id: str = 'AI_0'
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    
    # Static files
    static_dir: str = "static"
    templates_dir: str = "templates"
    
    # Socket.IO settings
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
print('here')

# Game constants (for backward compatibility)
NUMBER_OF_ROW = settings.number_of_row
NUMBER_OF_COL = settings.number_of_col
GAME_TYPE_SINGLE = settings.game_type_single
GAME_TYPE_PVP = settings.game_type_pvp
ASYNC_MODE = settings.async_mode
MAX_NUMBER_OF_ROOM = settings.max_number_of_room
AI_ID = settings.ai_id 
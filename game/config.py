from dotenv import load_dotenv
import os
from os.path import join, dirname

# set path to env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)


class Config:
    """Set Django configuration vars from .env file."""

    # Load in enviornemnt variables
    NUM_ROW = 16
    NUM_COL = 16
    ASYNC_MODE = 'eventlet'
    SERVER = 'http://127.0.0.1:8000'
    AI_ID = 'AI_0'
    MAX_NUMBER_OF_ROOM = 100000000

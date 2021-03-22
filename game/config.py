from dotenv import load_dotenv
import os
from os.path import join, dirname

# set path to env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)


class Config:
    """Set Django configuration vars from .env file."""

    # Load in enviornemnt variables
    NUM_ROW = int(os.environ.get("NUM_ROW"))
    NUM_COL = int(os.environ.get('NUM_COL'))
    ASYNC_MODE = os.getenv('ASYNC_MODE')
    SERVER = os.getenv('SERVER')

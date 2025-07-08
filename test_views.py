#!/usr/bin/env python3
"""
Test script for FastAPI views functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_views_imports():
    """Test that all views functions can be imported"""
    try:
        from game.views import (
            set_socketio_server,
            handle_connect,
            handle_disconnect,
            handle_init_game,
            handle_join_current_game,
            handle_move,
            handle_rematch,
            handle_disconnect_request,
            generate_game_id,
            get_game_context,
            get_active_games,
            get_health_status
        )
        print("✅ All views functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_utility_functions():
    """Test utility functions"""
    try:
        from game.views import generate_game_id, get_game_context, get_active_games, get_health_status
        
        # Test generate_game_id
        game_id = generate_game_id()
        print(f"✅ Generated game ID: {game_id}")
        
        # Test get_game_context
        context = get_game_context()
        print(f"✅ Game context: {context}")
        
        # Test get_active_games
        games = get_active_games()
        print(f"✅ Active games: {games}")
        
        # Test get_health_status
        health = get_health_status()
        print(f"✅ Health status: {health}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing utility functions: {e}")
        return False

def test_config_import():
    """Test config import"""
    try:
        from config import settings
        print(f"✅ Config loaded: {settings.app_name}")
        return True
    except ImportError as e:
        print(f"❌ Config import error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing FastAPI views functionality...")
    print("=" * 50)
    
    tests = [
        ("Config Import", test_config_import),
        ("Views Imports", test_views_imports),
        ("Utility Functions", test_utility_functions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI views are ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
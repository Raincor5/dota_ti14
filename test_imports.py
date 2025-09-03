#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all the main imports."""
    print("🧪 Testing imports...")
    
    try:
        # Test model imports
        print("  Testing models...")
        from models.player import Player
        from models.team import Team
        from models.match import Match
        from models.tournament import Tournament
        print("    ✅ Models imported successfully")
        
        # Test feature imports
        print("  Testing features...")
        from features.elo_system import EloRatingSystem
        print("    ✅ Features imported successfully")
        
        # Test data collection imports
        print("  Testing data collection...")
        from data_collection.opendota_client import OpenDotaClient
        print("    ✅ Data collection imported successfully")
        
        print("\n🎉 All imports successful! The project is ready to use.")
        return True
        
    except ImportError as e:
        print(f"    ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"    ❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🚀 You can now run:")
        print("   python examples/elo_demo.py")
        print("   python src/main.py")
    else:
        print("\n⚠️  Please fix the import issues before proceeding.")

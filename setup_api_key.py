#!/usr/bin/env python3
"""
Helper script to set up OpenDota API key.
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file with OpenDota API key configuration."""
    env_path = Path('.env')
    
    if env_path.exists():
        print("⚠️  .env file already exists!")
        with open(env_path, 'r') as f:
            current_content = f.read()
            if 'OPENDOTA_API_KEY' in current_content:
                print("✅ OpenDota API key is already configured in .env file")
                return
            else:
                print("📝 .env file exists but doesn't contain OpenDota API key")
    
    print("🔑 OpenDota API Key Setup")
    print("=" * 30)
    print("1. Go to: https://www.opendota.com/")
    print("2. Sign in with your Steam account")
    print("3. Go to your profile settings")
    print("4. Generate an API key")
    print()
    
    api_key = input("Enter your OpenDota API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    # Create .env file
    env_content = f"""# OpenDota API Configuration
# Get your API key from: https://www.opendota.com/
OPENDOTA_API_KEY={api_key}

# Data Collection Settings
DAYS_BACK=30
MAX_MATCHES=1000

# ELO System Settings
BASE_K_FACTOR=32.0
RATING_DECAY_DAYS=365
DECAY_FACTOR=0.95
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ .env file created successfully!")
    print(f"📁 Location: {env_path.absolute()}")
    print()
    print("🚀 You can now run the main project:")
    print("   python3 main.py")
    print()
    print("💡 The API key will be loaded automatically from the .env file")

if __name__ == "__main__":
    create_env_file()

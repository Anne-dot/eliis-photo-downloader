from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import os
import sys

def get_firefox_driver(profile_path):
    """Connect to existing Firefox session with user profile"""
    if not os.path.exists(profile_path):
        print(f"Error: Firefox profile not found at {profile_path}")
        sys.exit(1)
    
    options = Options()
    options.set_preference('profile', profile_path)
    options.add_argument(f"-profile={profile_path}")
    
    service = Service('/usr/local/bin/geckodriver')
    
    try:
        print("Starting Firefox with your profile...")
        print("Note: This will open a new Firefox window.")
        print("Please log in to eliis.eu if needed.")
        driver = webdriver.Firefox(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error connecting to Firefox: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Firefox is not running")
        print("2. Try closing all Firefox windows and run again")
        print("3. The script will open its own Firefox window")
        sys.exit(1)
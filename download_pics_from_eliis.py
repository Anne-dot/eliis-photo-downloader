#!/usr/bin/env python3
import json
import sys
import os
from colorama import init, Fore
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from firefox_session import get_firefox_driver
from arrow_download_handler import ArrowDownloadHandler
from scraper import EliisScraper

init(autoreset=True)  # Initialize colorama

def load_config():
    """Load configuration from config.json"""
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"{Fore.RED}Error: config.json not found!")
        print(f"Please copy config.example.json to config.json and update it.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

def print_banner():
    """Print welcome banner"""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Eliisi Picture Downloader")
    print(f"{Fore.CYAN}{'='*50}\n")


def main():
    print_banner()
    
    # Load configuration
    print("Loading configuration...")
    config = load_config()
    
    # Connect to Firefox
    print(f"Connecting to Firefox profile...")
    driver = get_firefox_driver(config['firefox_profile_path'])
    
    try:
        # Initialize components
        download_handler = ArrowDownloadHandler(driver, config)
        scraper = EliisScraper(driver, config)
        
        # Start downloading
        start_time = datetime.now()
        total = scraper.process_all_children(download_handler)
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\n{Fore.GREEN}{'='*50}")
        print(f"{Fore.GREEN}Download complete!")
        print(f"{Fore.GREEN}Total photos downloaded: {total}")
        print(f"{Fore.GREEN}Time taken: {duration:.1f} seconds")
        print(f"{Fore.GREEN}{'='*50}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Download cancelled by user")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
        if config.get('debug_mode'):
            import traceback
            traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
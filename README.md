# Eliisi Picture Downloader

A Python automation tool to download pictures and descriptions from eliis.eu for multiple children.

## Problem Statement
Currently, eliis.eu only allows downloading pictures one at a time through the web interface. With multiple children, this becomes time-consuming. This tool automates the process of downloading all pictures and their descriptions.

## Design Principles (ADHD-Friendly)
- **KISS**: Keep It Simple, Stupid - One button, it just works
- **DRY**: Don't Repeat Yourself - Modular, reusable code
- **Single Source of Truth**: One config file, one place for each setting
- **Clear Feedback**: Always show what's happening
- **Fail Gracefully**: Clear error messages, easy recovery

## MVP Features
- Use existing Firefox session (no login needed!)
- Download ALL pictures for ALL children in one go
- Clear progress indicator (X of Y downloaded)
- Smart duplicate detection (skip already downloaded)
- Simple folder structure: `child_name/YYYY-MM-DD/picture.jpg`

## How It Works
- **Arrow Navigation**: Clicks first photo thumbnail, then uses arrow keys to navigate through all photos for each date
- **Automatic Loading**: Loads older diary entries automatically with "Vaata vanemaid päevikuid" button
- **Smart Downloads**: Uses your existing Firefox session with authentication
- **Organized Storage**: Downloads to `downloads/child_name/YYYY-MM-DD/`
- **Efficient**: Only opens photo viewer once per date, uses arrows to move between photos

## Project Structure
```
eliisi-piltide-laadimine/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.json                  # Your configuration (excluded from git)
├── config.example.json          # Configuration template
├── download_pics_from_eliis.py  # Main script
├── src/                         # Source code modules
│   ├── firefox_session.py       # Firefox connection handler
│   ├── scraper.py              # Web scraping and navigation logic
│   └── arrow_download_handler.py # Smart photo download with arrow navigation
└── downloads/                   # Downloaded pictures (excluded from git)
    ├── Child1_Name/
    │   ├── 2025-05-30/
    │   │   ├── photo_20250530_001.jpg
    │   │   └── ...
    │   └── ...
    └── Child2_Name/
```

## Installation

1. **Clone this repository**
   ```bash
   git clone <repository-url>
   cd eliisi-piltide-laadimine
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install geckodriver** (Firefox driver for Selenium)
   ```bash
   # On Ubuntu/Debian:
   sudo apt-get install firefox-geckodriver
   
   # Or download manually from:
   # https://github.com/mozilla/geckodriver/releases
   ```

4. **Setup Firefox session**
   - Open Firefox and log in to eliis.eu with your Google account
   - Keep Firefox running in the background
   - Find your Firefox profile path:
     ```bash
     # Regular Firefox installation:
     find ~/.mozilla/firefox -name "*.default*" -type d
     
     # Snap Firefox installation:
     find ~/snap/firefox/common/.mozilla/firefox -name "*.default*" -type d
     ```

5. **Configure the script**
   - Copy `config.example.json` to `config.json`
   - Update with your Firefox profile path
   - Find your children's IDs:
     - In Firefox, navigate to each child's diary page
     - Look at the URL: `https://eliis.eu/child/XXXXXX/diary`
     - The number (XXXXXX) is the child ID
   - Update the config with child names, IDs, and folder names

## Usage
```bash
python3 download_pics_from_eliis.py
```

The script will:
- Connect to your running Firefox session
- Navigate to each child's diary
- Process each date by clicking the first photo thumbnail
- Use arrow navigation to download all photos for that date
- Automatically load older diary entries
- Save photos to `downloads/child_name/YYYY-MM-DD/`
- Skip already downloaded files
- Show progress: `Photo 1... ✓`

## Security Considerations
- Credentials stored securely (never in code)
- Respects website rate limits
- Only accesses authorized content
- No data sharing with third parties

## Performance
- **Setup time**: ~1.5 hours with AI assistance
- **Download speed**: ~700 photos in 30 minutes
- **Coverage**: Downloads all available photos (tested with 4 months of kindergarten photos)
- **Efficiency**: Uses arrow navigation instead of clicking each thumbnail individually

## Requirements
- Linux (tested on Ubuntu)
- Python 3.x
- Firefox with existing eliis.eu login session
- Dependencies: selenium, geckodriver (for Firefox)

## Current Status (2025-05-31)

### ✅ Fully Working!
- Successfully downloads all available photos from eliis.eu
- Uses smart arrow navigation for efficient downloading
- Handles multiple children in one run
- Automatically loads older diary entries
- Skips already downloaded photos
- Tested with 700+ photos across 4 months

### Key Features Implemented:
- **Photo Detection**: Uses `div.e3-image-thumbnail` elements
- **Navigation**: Clicks thumbnails and uses forward arrow in photo viewer
- **Date Handling**: Processes photos by date groups
- **Automatic Loading**: Clicks "Vaata vanemaid päevikuid" for older entries
- **File Organization**: Saves as `downloads/child_name/YYYY-MM-DD/photo_YYYYMMDD_XXX.jpg`

### Known Limitations:
- Only downloads photos currently available on eliis.eu (older photos may be archived/removed by the platform)
- Requires Firefox to stay open during download
- JSON config doesn't support comments (use proper JSON syntax)

## Future Development Ideas

### Make It Parent-Friendly
- **Windows Support**: Most parents use Windows, not Linux
  - Adapt Firefox profile detection for Windows
  - Handle Windows paths properly
  - Provide Windows-specific installation guide

- **Easy Installation Package**:
  - One-click installer with everything bundled
  - Auto-detect Firefox profile
  - Simple GUI for configuration (no JSON editing)
  - "Just works" approach - minimal technical knowledge required

- **Smart Features**:
  - **Stop at Last Download Date**: When downloading on June 15th, stop once it reaches May 30th photos (if that's when you last downloaded)
  - **Scheduling**: Run automatically every week/month
  - **Notifications**: Email when new photos are downloaded
  - System tray icon showing download status

### Current Workaround for Non-Technical Parents
- Technical parent/friend sets it up once
- Create desktop shortcut to run the script
- Schedule with cron (Linux) or Task Scheduler (Windows)

## Disclaimer
This tool is for personal use only. Users must ensure they comply with eliis.eu terms of service and only download content they are authorized to access.
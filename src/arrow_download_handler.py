import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class ArrowDownloadHandler:
    def __init__(self, driver, config):
        """Initialize download handler with browser driver and config"""
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 10)
        self.download_path = config.get('download_path', 'downloads')
        self.firefox_download_dir = str(Path.home() / "Downloads")
        
    def ensure_directory(self, path):
        """Create directory if it doesn't exist"""
        os.makedirs(path, exist_ok=True)
        return path
    
    def extract_date_from_card(self, card_element):
        """Extract date from diary card"""
        try:
            date_elem = card_element.find_element(By.CSS_SELECTOR, ".text-muted")
            date_text = date_elem.text
            
            months = {
                'jaanuar': 1, 'veebruar': 2, 'märts': 3, 'aprill': 4,
                'mai': 5, 'juuni': 6, 'juuli': 7, 'august': 8,
                'september': 9, 'oktoober': 10, 'november': 11, 'detsember': 12
            }
            
            parts = date_text.split(', ')[1].split(' ')
            day = int(parts[0])
            month_name = parts[1].lower()
            year = int(parts[2])
            
            month = months.get(month_name, 1)
            return datetime(year, month, day)
            
        except Exception as e:
            print(f"  Error parsing date: {e}")
            return datetime.now()
    
    
    def get_photo_path(self, child_name, date, index):
        """Build path: base/child_name/YYYY-MM-DD/photo_index.jpg"""
        date_folder = date.strftime("%Y-%m-%d")
        full_path = os.path.join(self.download_path, child_name, date_folder)
        self.ensure_directory(full_path)
        
        filename = f"photo_{date.strftime('%Y%m%d')}_{index:03d}.jpg"
        return os.path.join(full_path, filename)
    
    def wait_for_download(self, timeout=10):
        """Wait for download to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            download_files = list(Path(self.firefox_download_dir).glob("*.jpg"))
            temp_files = list(Path(self.firefox_download_dir).glob("*.part"))
            
            if download_files and not temp_files:
                return download_files[0] if download_files else None
            
            time.sleep(0.5)
        
        return None
    
    def clear_downloads(self):
        """Clear existing downloads"""
        for f in Path(self.firefox_download_dir).glob("*.jpg"):
            try:
                f.unlink()
            except:
                pass
    
    def download_current_photo(self):
        """Download the currently displayed photo"""
        try:
            # Find and click download button
            download_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".mdi-download"))
            )
            self.driver.execute_script("arguments[0].click();", download_btn)
            return True
        except:
            return False
    
    def has_forward_arrow(self):
        """Check if forward arrow exists and is clickable"""
        try:
            # Debug: Find all clickable elements
            if self.config.get('debug_mode'):
                all_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, i[class*='mdi'], div[class*='arrow'], span[class*='arrow']")
                print(f"\n  Debug: Found {len(all_buttons)} potential buttons")
                for btn in all_buttons[:10]:
                    classes = btn.get_attribute('class')
                    if classes and ('arrow' in classes or 'chevron' in classes or 'next' in classes):
                        print(f"    - {btn.tag_name}: {classes}")
            
            # Look for forward/next arrow - common selectors
            forward_selectors = [
                # SVG arrow button (based on your inspection)
                "button.d-none:nth-child(1)",
                "button:has(svg path[d*='M8.59,16.58L13.17,12'])",
                "button svg[viewBox='0 0 24 24']",
                # Icon-based arrows
                ".mdi-chevron-right",
                ".mdi-arrow-right",
                # Other common patterns
                "[aria-label*='next']",
                "[aria-label*='Next']",
                "button[title*='next']"
            ]
            
            for selector in forward_selectors:
                try:
                    if selector == "button.d-none:nth-child(1)":
                        # Special handling for d-none button - find by SVG content
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            try:
                                svg = btn.find_element(By.TAG_NAME, "svg")
                                path = svg.find_element(By.TAG_NAME, "path")
                                d_attr = path.get_attribute("d")
                                if d_attr and "M8.59,16.58L13.17,12" in d_attr:
                                    # This is the forward arrow
                                    if self.config.get('debug_mode'):
                                        print(f"  Found forward arrow button via SVG path")
                                    return btn
                            except:
                                continue
                    else:
                        arrows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for arrow in arrows:
                            if arrow.is_displayed() and arrow.size['width'] > 0:
                                if self.config.get('debug_mode'):
                                    print(f"  Found arrow with selector: {selector}")
                                return arrow
                except:
                    continue
            
            return None
        except:
            return None
    
    def click_forward_arrow(self):
        """Click the forward arrow to go to next photo"""
        arrow = self.has_forward_arrow()
        if arrow:
            try:
                # Get current image src before clicking
                current_img = self.get_current_image_src()
                
                # Click arrow
                self.driver.execute_script("arguments[0].click();", arrow)
                
                # Wait for image to change
                start_time = time.time()
                while time.time() - start_time < 5:  # 5 second timeout
                    time.sleep(0.3)
                    new_img = self.get_current_image_src()
                    if new_img and new_img != current_img:
                        # Image has changed
                        return True
                
                print("  Warning: Image didn't change after arrow click")
                return False
            except:
                pass
        return False
    
    def get_current_image_src(self):
        """Get the src of the currently displayed image"""
        try:
            # Look for the main displayed image in the viewer
            selectors = [
                "img.e3-img-full",
                ".modal img",
                ".photo-viewer img",
                "img[style*='display: block']",
                "img:not(.e3-image-thumbnail)"
            ]
            
            for selector in selectors:
                imgs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for img in imgs:
                    if img.is_displayed() and img.size['height'] > 100:  # Main image, not thumbnail
                        src = img.get_attribute('src')
                        if src and 'cloudfront' in src:
                            return src
            
            return None
        except:
            return None
    
    def close_photo_viewer(self):
        """Close the photo viewer"""
        try:
            # Try multiple ways to close
            close_selectors = [
                ".mdi-close",
                "[aria-label='close']",
                "button.close",
                ".modal-close"
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if close_btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", close_btn)
                        time.sleep(0.5)
                        return
                except:
                    continue
            
            # If no close button found, try ESC
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
            
        except:
            pass
    
    def download_photos_for_date(self, card_element, child_name, date):
        """Download all photos for a specific date using arrow navigation"""
        downloaded = 0
        
        # Find thumbnails in this card - no expansion needed
        try:
            thumbnails = card_element.find_elements(By.CSS_SELECTOR, ".e3-image-thumbnail")
            if not thumbnails:
                # No visible thumbnails, skip this date
                return downloaded
            
            print(f"  Found {len(thumbnails)} visible photos for {date.strftime('%Y-%m-%d')}")
            
            # Click first thumbnail
            self.driver.execute_script("arguments[0].scrollIntoView(true);", thumbnails[0])
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", thumbnails[0])
            time.sleep(1)
            
            # Download photos using arrow navigation
            photo_index = 1
            while True:
                print(f"    Photo {photo_index}...", end='', flush=True)
                
                # Clear downloads folder
                self.clear_downloads()
                
                # Download current photo
                if self.download_current_photo():
                    # Wait for download
                    downloaded_file = self.wait_for_download()
                    if downloaded_file:
                        # Move to organized location
                        dest_path = self.get_photo_path(child_name, date, photo_index)
                        if not os.path.exists(dest_path):
                            shutil.move(str(downloaded_file), dest_path)
                            downloaded += 1
                            print(" ✓")
                        else:
                            print(" (exists)")
                    else:
                        print(" (timeout)")
                else:
                    print(" (failed)")
                
                # Try to go to next photo
                if not self.click_forward_arrow():
                    # No more photos for this date
                    break
                
                photo_index += 1
                time.sleep(0.5)
            
            # Close photo viewer
            self.close_photo_viewer()
            
        except Exception as e:
            print(f"  Error processing date photos: {e}")
            self.close_photo_viewer()
        
        return downloaded
    
    def load_more_dates(self):
        """Click 'Vaata vanemaid päevikuid' to load older dates"""
        try:
            # Look for the button
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.position-relative")
            for btn in buttons:
                if "Vaata vanemaid" in btn.text:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", btn)
                    print("\n→ Loading older diary entries...")
                    time.sleep(3)
                    return True
            return False
        except:
            return False
    
    def process_all_dates(self, child_name):
        """Process all date cards and download photos"""
        total_downloaded = 0
        processed_dates = set()
        
        while True:
            # Find all diary cards
            cards = self.driver.find_elements(By.CSS_SELECTOR, "div.card.p-3.mb-3")
            
            # Process new cards only
            new_cards = []
            for card in cards:
                try:
                    date = self.extract_date_from_card(card)
                    date_str = date.strftime('%Y-%m-%d')
                    if date_str not in processed_dates:
                        new_cards.append((card, date, date_str))
                except:
                    continue
            
            if new_cards:
                print(f"\nFound {len(new_cards)} new diary entries to process")
                
                for i, (card, date, date_str) in enumerate(new_cards, 1):
                    try:
                        print(f"\n[{i}/{len(new_cards)}] Processing {date_str}...")
                        
                        # Download photos for this date
                        downloaded = self.download_photos_for_date(card, child_name, date)
                        total_downloaded += downloaded
                        processed_dates.add(date_str)
                        
                        print(f"  Downloaded {downloaded} photos")
                        
                    except Exception as e:
                        print(f"  Error processing card: {e}")
                        continue
            
            # Try to load more dates
            if not self.load_more_dates():
                # No more dates to load
                break
        
        return total_downloaded
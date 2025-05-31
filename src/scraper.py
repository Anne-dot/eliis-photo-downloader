from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re

class EliisScraper:
    def __init__(self, driver, config):
        """Initialize scraper with browser driver and config"""
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 10)
    
    
    def navigate_to_child_diary(self, child_id):
        """Navigate directly to a child's diary page"""
        diary_url = f"https://eliis.eu/child/{child_id}/diary"
        print(f"Navigating to diary: {diary_url}")
        try:
            self.driver.get(diary_url)
            time.sleep(self.config.get('wait_time', 3))
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        except Exception as e:
            print(f"Error navigating to child diary: {e}")
            return False
    
    def extract_date_from_page(self):
        """Extract date from page elements"""
        try:
            date_elements = self.driver.find_elements(By.XPATH, "//time | //*[contains(@class, 'date')] | //*[contains(text(), '2025')] | //*[contains(text(), 'mai')]")
            for elem in date_elements:
                date_text = elem.text
                for fmt in ["%d. %B %Y", "%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        date_text = date_text.replace("jaanuar", "january").replace("veebruar", "february")
                        date_text = date_text.replace("märts", "march").replace("aprill", "april")
                        date_text = date_text.replace("mai", "may").replace("juuni", "june")
                        date_text = date_text.replace("juuli", "july").replace("august", "august")
                        date_text = date_text.replace("september", "september").replace("oktoober", "october")
                        date_text = date_text.replace("november", "november").replace("detsember", "december")
                        return datetime.strptime(date_text, fmt)
                    except:
                        continue
        except:
            pass
        return datetime.now()
    
    def extract_date_from_url(self, url):
        """Extract date from page context"""
        return self.extract_date_from_page()
    
    
    def click_show_more_photos(self):
        """Click 'Kuva rohkem' button to load more photos"""
        try:
            show_more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Kuva rohkem')]")
            if show_more_buttons:
                for btn in show_more_buttons:
                    if btn.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", btn)
                        print("  → Clicked 'Kuva rohkem' button")
                        time.sleep(2)
                        return True
            return False
        except Exception as e:
            if self.config.get('debug_mode'):
                print(f"  Error clicking show more: {e}")
            return False
    
    def click_load_older_diaries(self):
        """Click 'Vaata vanemaid päevikuid' button to load older entries"""
        try:
            older_diary_btn = self.driver.find_element(By.CSS_SELECTOR, "button.position-relative")
            if older_diary_btn and "Vaata vanemaid" in older_diary_btn.text:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", older_diary_btn)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", older_diary_btn)
                print("  → Clicked 'Vaata vanemaid päevikuid' button")
                time.sleep(3)
                return True
            return False
        except:
            return False
    
    def scroll_and_load_all_photos(self):
        """Scroll page to load all photos and click load more buttons"""
        photos_before = 0
        scroll_attempts = 0
        max_attempts = self.config.get('max_scroll_attempts', 10)
        
        while scroll_attempts < max_attempts:
            current_photos = len(self.driver.find_elements(By.CSS_SELECTOR, "div.e3-image-thumbnail"))
            
            while self.click_show_more_photos():
                time.sleep(1)
                new_count = len(self.driver.find_elements(By.CSS_SELECTOR, "div.e3-image-thumbnail"))
                print(f"  Photos after 'Kuva rohkem': {new_count}")
            
            current_photos = len(self.driver.find_elements(By.CSS_SELECTOR, "div.e3-image-thumbnail"))
            
            if current_photos == photos_before and scroll_attempts > 0:
                if not self.click_load_older_diaries():
                    break
                else:
                    time.sleep(2)
                    continue
                
            photos_before = current_photos
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.config.get('wait_time', 2))
                
            scroll_attempts += 1
            print(f"Loading photos... ({current_photos} found)")
    
    def download_photos_with_buttons(self, download_handler, child_name):
        """Download photos by clicking download buttons"""
        downloaded = 0
        
        thumbnail_divs = self.driver.find_elements(By.CSS_SELECTOR, "div.e3-image-thumbnail")
        total = len(thumbnail_divs)
        
        print(f"\nFound {total} photos total")
        
        for i, thumbnail in enumerate(thumbnail_divs, 1):
            print(f"[{i}/{total}] Downloading...", end='', flush=True)
            
            date = self.extract_date_from_page()
            
            success, result = download_handler.download_photo_via_click(
                thumbnail, child_name, date, i
            )
            
            if success:
                downloaded += 1
                print(" ✓ Done!")
            else:
                print(f" → Skipped ({result})")
            
            time.sleep(1)
        
        return downloaded
    
    def process_all_children(self, download_handler):
        """Process photos for all configured children"""
        total_downloaded = 0
        
        # Check if using arrow navigation
        use_arrow_nav = hasattr(download_handler, 'process_all_dates')
        
        for child in self.config['children']:
            print(f"\n{'='*50}")
            print(f"Processing {child['name']}...")
            print(f"{'='*50}")
            
            if not self.navigate_to_child_diary(child['id']):
                print(f"Failed to navigate to {child['name']}'s diary")
                continue
            
            # Wait for content to load
            time.sleep(5)
            
            if use_arrow_nav:
                downloaded = download_handler.process_all_dates(child['folder_name'])
            else:
                self.scroll_and_load_all_photos()
                downloaded = self.download_photos_with_buttons(
                    download_handler, child['folder_name']
                )
            
            total_downloaded += downloaded
        
        return total_downloaded
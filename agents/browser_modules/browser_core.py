"""
Browser Core Module - Basic browser initialization and navigation
"""

import time
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class BrowserCore:
    """Core browser functionality"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.is_initialized = False
        
        # Action templates for explanations
        self.action_templates = {
            "navigate": "I navigated to {url} and the page loaded successfully.",
            "click": "I clicked on '{element}' and the action was completed.",
            "fill": "I filled in the {field} field with '{value}'.",
            "scroll": "I scrolled {direction} on the page.",
            "wait": "I waited for {duration} seconds."
        }
    
    def initialize_browser(self, headless: bool = None):
        """Initialize the browser instance."""
        try:
            if headless is None:
                headless = False
            
            # Setup Chrome options
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Suppress Chrome warnings and errors
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI,VizDisplayCompositor")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # Initialize Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Initialize WebDriverWait with faster timeout for snappy demo
            self.wait = WebDriverWait(self.driver, 5)  # Reduced from 10 seconds
            
            self.is_initialized = True
            
        except Exception as e:
            raise
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a specific URL."""
        try:
            if not self.is_initialized:
                self.initialize_browser()
            
            self.driver.get(url)
            time.sleep(2)
            
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            return {
                "success": True,
                "message": f"Successfully navigated to {url}. Page title: {page_title}",
                "action": "navigate",
                "url": current_url,
                "title": page_title
            }
            
        except Exception as e:
            error_msg = f"Navigation failed: {str(e)}"
            return {
                "success": False,
                "message": f"Failed to navigate to {url}. {error_msg}",
                "error": error_msg
            }
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information for context."""
        try:
            if not self.is_initialized or not self.driver:
                return {"error": "Browser not initialized"}
            
            info = {
                "title": self.driver.title,
                "url": self.driver.current_url,
                "ready_state": self.driver.execute_script("return document.readyState")
            }
            
            return info
            
        except Exception as e:
            return {"error": f"Failed to get page info: {str(e)}"}
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of the current page."""
        try:
            if not self.is_initialized:
                return "Browser not initialized"
            
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            screenshot_path = self.driver.save_screenshot(filename)
            
            return screenshot_path
            
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"
    
    def close_browser(self):
        """Close the browser instance."""
        try:
            if self.driver:
                self.driver.quit()
                print("Browser closed successfully")
        except Exception as e:
            print(f"Failed to close browser: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close_browser()

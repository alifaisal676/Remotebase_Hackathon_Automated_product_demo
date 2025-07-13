"""
Browser Automation Agent: Executes browser actions using browser-use package.
Handles navigation, clicking, filling forms, scrolling, and generates explanations.
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
# Settings removed
# Logging removed

class BrowserAutomationAgent:
    """
    Browser Automation Agent responsible for:
    1. Executing browser actions based on structured intents
    2. Using browser-use package for automation
    3. Observing page state and content
    4. Generating natural language explanations
    """
    
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
        
        # Success: Browser agent
    
    def initialize_browser(self, headless: bool = None):
        """
        Initialize the browser instance.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        try:
            # Debug: Browser agent action
            
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
            
            # Initialize Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Initialize WebDriverWait
            self.wait = WebDriverWait(self.driver, 10)
            
            self.is_initialized = True
            # Success: Browser agent")
            
        except Exception as e:
            # Error: Browser agent}")
            raise
    
    def execute_intent(self, intent_data: Dict[str, Any]) -> str:
        """
        Execute a browser action based on structured intent.
        
        Args:
            intent_data: Structured intent from Intent Parsing Agent
            
        Returns:
            Natural language explanation of the action
        """
        try:
            if not self.is_initialized:
                self.initialize_browser()
            
            intent = intent_data.get("intent", "unknown")
            # Debug: Browser agent action
            
            # Route to appropriate handler
            if intent == "navigate":
                return self.handle_navigate(intent_data)
            elif intent == "click":
                return self.handle_click(intent_data)
            elif intent == "fill":
                return self.handle_fill(intent_data)
            elif intent == "scroll":
                return self.handle_scroll(intent_data)
            elif intent == "wait":
                return self.handle_wait(intent_data)
            elif intent == "question":
                return self.handle_question(intent_data)
            else:
                return self.handle_unknown_intent(intent_data)
                
        except Exception as e:
            error_msg = f"Failed to execute intent '{intent}': {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "error": error_msg,
                "message": f"I encountered an error: {error_msg}"
            }
    
    def handle_question(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle question intent."""
        try:
            question = intent_data.get("question", "")
            # Debug: Browser agent action
            
            from agents.intent_parsing_agent import IntentParsingAgent
            intent_agent = IntentParsingAgent()
            answer = intent_agent.answer_question(question)
            
            return {
                "success": True,
                "message": answer,
                "action": "question"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Couldn't answer: {str(e)}",
                "error": str(e)
            }
    
    def handle_navigate(self, intent_data: Dict[str, Any]) -> str:
        """
        Handle navigation intent.
        
        Args:
            intent_data: Intent data containing target_url
            
        Returns:
            Explanation of navigation action
        """
        try:
            target_url = intent_data.get("target_url")
            page_name = intent_data.get("page_name", "page")
            
            if not target_url:
                return {"success": False, "message": "I couldn't navigate because no URL was specified.", "error": "No URL specified"}
            
            # Debug: Browser agent action
            
            # Navigate using Selenium
            self.driver.get(target_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Get page title for better explanation
            try:
                page_title = self.driver.title
                if page_title:
                    explanation = f"I navigated to {target_url} and loaded the '{page_title}' page."
                else:
                    explanation = f"I navigated to {target_url} and the page loaded successfully."
            except:
                explanation = f"I navigated to {target_url}."
            
            # Success: Browser agent
            return {
                "success": True,
                "message": explanation,
                "url": target_url
            }
            
        except Exception as e:
            error_msg = f"Navigation failed: {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "error": error_msg,
                "message": f"I couldn't navigate to the page. {error_msg}"
            }
    
    def handle_click(self, intent_data: Dict[str, Any]) -> str:
        """
        Handle click intent.
        
        Args:
            intent_data: Intent data containing element information
            
        Returns:
            Explanation of click action
        """
        try:
            element_text = intent_data.get("element_text")
            element_selector = intent_data.get("element_selector")
            
            if not element_text and not element_selector:
                return {"success": False, "message": "I couldn't click because no element was specified.", "error": "No element specified"}
            
            target = element_text or element_selector
            # Debug: Browser agent action
            
            # Try to find and click the element
            try:
                element = None
                
                if element_text:
                    # Try to find by text content using XPath
                    try:
                        element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{element_text}')]")
                    except:
                        # Try partial link text for links
                        try:
                            element = self.driver.find_element(By.PARTIAL_LINK_TEXT, element_text)
                        except:
                            # Try button with text
                            try:
                                element = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{element_text}')]")
                            except:
                                pass
                
                if not element and element_selector:
                    # Try CSS selector
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
                    except:
                        pass
                
                if element:
                    # Scroll to element and click
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    element.click()
                    explanation = f"I clicked on '{target}' and the action was completed."
                else:
                    explanation = f"I couldn't find the element '{target}' to click."
                    
            except Exception as e:
                explanation = f"I had trouble clicking '{target}': {str(e)}"
            
            # Success: Browser agent
            return {"success": True, "message": explanation, "action": "click", "target": target}
            
        except Exception as e:
            error_msg = f"Click failed: {str(e)}"
            # Error: Browser agent
            return {"success": False, "message": f"I couldn't click the element. {error_msg}", "error": error_msg}
    
    def handle_fill(self, intent_data: Dict[str, Any]) -> str:
        """
        Handle fill/input intent.
        
        Args:
            intent_data: Intent data containing field and value
            
        Returns:
            Explanation of fill action
        """
        try:
            field_name = intent_data.get("field_name")
            value = intent_data.get("value")
            
            if not field_name or not value:
                return {"success": False, "message": "I couldn't fill the field because field name or value is missing.", "error": "Missing field name or value"}
            
            # Debug: Browser agent action
            
            # Try to find and fill the field
            try:
                # Try multiple strategies to find the field
                element = None
                
                # Try by name attribute
                try:
                    element = self.driver.find_element(By.NAME, field_name)
                except:
                    pass
                
                # Try by id attribute
                if not element:
                    try:
                        element = self.driver.find_element(By.ID, field_name)
                    except:
                        pass
                
                # Try by placeholder text
                if not element:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//input[@placeholder='{field_name}']")
                    except:
                        pass
                
                # Try by label text
                if not element:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//input[@type='text' or @type='email' or @type='password'][preceding-sibling::label[contains(text(), '{field_name}')]]")
                    except:
                        pass
                
                if element:
                    # Scroll to element
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    
                    # Clear and fill
                    element.clear()
                    element.send_keys(value)
                    explanation = f"I filled in the {field_name} field with '{value}'."
                else:
                    explanation = f"I couldn't find the {field_name} field to fill."
                    
            except Exception as e:
                explanation = f"I had trouble filling the {field_name} field: {str(e)}"
            
            # Success: Browser agent
            return {"success": True, "message": explanation, "action": "fill", "field": field_name, "value": value}
            
        except Exception as e:
            error_msg = f"Fill failed: {str(e)}"
            # Error: Browser agent
            return {"success": False, "message": f"I couldn't fill the field. {error_msg}", "error": error_msg}
    
    def handle_scroll(self, intent_data: Dict[str, Any]) -> str:
        """
        Handle scroll intent.
        
        Args:
            intent_data: Intent data containing scroll direction/amount
            
        Returns:
            Explanation of scroll action
        """
        try:
            direction = intent_data.get("direction", "down")
            amount = intent_data.get("amount", "normal")
            
            # Debug: Browser agent action
            
            # Execute scroll action
            try:
                if direction.lower() == "down":
                    self.driver.execute_script("window.scrollBy(0, 500);")
                elif direction.lower() == "up":
                    self.driver.execute_script("window.scrollBy(0, -500);")
                elif direction.lower() == "top":
                    self.driver.execute_script("window.scrollTo(0, 0);")
                elif direction.lower() == "bottom":
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                explanation = f"I scrolled {direction} on the page."
                
            except Exception as e:
                explanation = f"I had trouble scrolling: {str(e)}"
            
            # Success: Browser agent
            return {"success": True, "message": explanation, "action": "scroll", "direction": direction}
            
        except Exception as e:
            error_msg = f"Scroll failed: {str(e)}"
            # Error: Browser agent
            return {"success": False, "message": f"I couldn't scroll the page. {error_msg}", "error": error_msg}
    
    def handle_wait(self, intent_data: Dict[str, Any]) -> str:
        """
        Handle wait intent.
        
        Args:
            intent_data: Intent data containing wait duration
            
        Returns:
            Explanation of wait action
        """
        try:
            duration = intent_data.get("duration", 2)
            
            # Convert to number if it's a string
            if isinstance(duration, str):
                try:
                    duration = float(duration)
                except:
                    duration = 2
            
            # Debug: Browser agent action
            
            time.sleep(duration)
            
            explanation = f"I waited for {duration} seconds."
            
            # Success: Browser agent
            return {"success": True, "message": explanation, "action": "wait", "duration": duration}
            
        except Exception as e:
            error_msg = f"Wait failed: {str(e)}"
            # Error: Browser agent
            return {"success": False, "message": f"I couldn't wait properly. {error_msg}", "error": error_msg}
    
    def handle_unknown_intent(self, intent_data: Dict[str, Any]) -> str:
        """
        Handle unknown or unsupported intents.
        
        Args:
            intent_data: Intent data
            
        Returns:
            Explanation of inability to handle intent
        """
        intent = intent_data.get("intent", "unknown")
        original_command = intent_data.get("original_command", "")
        
        # Debug: Browser agent action
        
        return {"success": False, "message": f"I don't understand how to handle the '{intent}' action. Could you try rephrasing your command?", "error": f"Unknown intent: {intent}"}
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        Get current page information for context.
        
        Returns:
            Dictionary with page information
        """
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
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional filename for screenshot
            
        Returns:
            Path to screenshot file
        """
        try:
            if not self.is_initialized:
                return "Browser not initialized"
            
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            screenshot_path = self.driver.save_screenshot(filename)
            # Success: Browser agent
            
            return screenshot_path
            
        except Exception as e:
            # Error: Browser agent}")
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
    
    def handle_question(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle question intent by providing answers about GIKI Transport System.
        
        Args:
            intent_data: Intent data containing the question
            
        Returns:
            Response with answer to the question
        """
        try:
            question = intent_data.get("question", "")
            
            if not question:
                return {
                    "success": False,
                    "message": "No question was provided.",
                    "error": "Missing question"
                }
            
            # Debug: Browser agent action
            
            # Import here to avoid circular imports
            from agents.intent_parsing_agent import IntentParsingAgent
            
            # Create a temporary intent agent for question answering
            intent_agent = IntentParsingAgent()
            answer = intent_agent.answer_question(question)
            
            # Success: Browser agent
            
            return {
                "success": True,
                "message": answer,
                "action": "question",
                "question": question,
                "answer": answer
            }
            
        except Exception as e:
            error_msg = f"Question answering failed: {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "message": f"I couldn't answer that question. {error_msg}",
                "error": error_msg
            }

    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a specific URL."""
        try:
            if not self.is_initialized:
                self.initialize_browser()
            
            # Debug: Browser agent action
            self.driver.get(url)
            time.sleep(2)
            
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            # Success: Browser agent
            
            return {
                "success": True,
                "message": f"Successfully navigated to {url}. Page title: {page_title}",
                "action": "navigate",
                "url": current_url,
                "title": page_title
            }
            
        except Exception as e:
            error_msg = f"Navigation failed: {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "message": f"Failed to navigate to {url}. {error_msg}",
                "error": error_msg
            }
    
    def handle_booking_flow(self) -> Dict[str, Any]:
        """Handle booking flow for GIKI Transport - navigates directly to payment page."""
        try:
            booking_url = "https://giktransport.giki.edu.pk:8038/booking/payment/wallet/5/"
            print(f"🌐 Navigating directly to booking payment page: {booking_url}")
            
            result = self.navigate_to_url(booking_url)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Successfully navigated to the booking payment page.",
                    "action": "booking",
                    "url": booking_url
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Booking flow failed: {str(e)}"
            print(f"❌ Booking flow error: {error_msg}")
            return {
                "success": False,
                "message": f"Failed to navigate to booking page. {error_msg}",
                "error": error_msg
            }
    
    def click_book_ticket_button(self) -> Dict[str, Any]:
        """Navigate directly to the booking payment page."""
        try:
            booking_url = "https://giktransport.giki.edu.pk:8038/booking/payment/wallet/5/"
            print(f"🎯 Navigating directly to booking payment page: {booking_url}")
            
            result = self.navigate_to_url(booking_url)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Successfully navigated to the booking payment page.",
                    "action": "book_ticket",
                    "url": booking_url
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Book ticket navigation failed: {str(e)}"
            print(f"❌ Book ticket error: {error_msg}")
            return {
                "success": False,
                "message": f"Failed to navigate to booking page. {error_msg}",
                "error": error_msg
            }

    def check_tickets(self) -> Dict[str, Any]:
        """Check user's tickets in GIKI Transport."""
        try:
            tickets_url = "https://giktransport.giki.edu.pk:8038/my-tickets/"
            # Debug: Browser agent action
            
            result = self.navigate_to_url(tickets_url)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Navigated to your tickets page. Here you can view all your transport tickets.",
                    "action": "tickets",
                    "url": tickets_url
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Ticket check failed: {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "message": f"Failed to check tickets. {error_msg}",
                "error": error_msg
            }
    
    def check_profile(self) -> Dict[str, Any]:
        """Check user's profile in GIKI Transport."""
        try:
            profile_url = "https://giktransport.giki.edu.pk:8038/auth/profile/"
            # Debug: Browser agent action
            
            result = self.navigate_to_url(profile_url)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Navigated to your profile page. Here you can view and update your profile information.",
                    "action": "profile",
                    "url": profile_url
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Profile check failed: {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "message": f"Failed to check profile. {error_msg}",
                "error": error_msg
            }
    
    def handle_signin(self, email: str = None, password: str = None) -> Dict[str, Any]:
        """
        Handle signin process for GIKI Transport.
        
        Args:
            email: Email address for signin
            password: Password for signin
            
        Returns:
            Response with signin result
        """
        try:
            # Default credentials
            if not email:
                email = "alifaisalkhn@gmail.com"
            if not password:
                password = "Alifaisal123@"
            
            signin_url = "https://giktransport.giki.edu.pk:8038/auth/signin/"
            # Debug: Browser agent action
            
            # Navigate to signin page
            result = self.navigate_to_url(signin_url)
            
            if not result["success"]:
                return result
            
            # Wait for page to load
            time.sleep(3)
            
            # Find and fill email field
            try:
                email_field = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                email_field.clear()
                email_field.send_keys(email)
                # Debug: Browser agent action
            except:
                try:
                    email_field = self.driver.find_element(By.ID, "email")
                    email_field.clear()
                    email_field.send_keys(email)
                    # Debug: Browser agent action")
                except:
                    return {
                        "success": False,
                        "message": "Could not find email field on signin page",
                        "error": "Email field not found"
                    }
            
            # Find and fill password field
            try:
                password_field = self.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(password)
                # Debug: Browser agent action
            except:
                try:
                    password_field = self.driver.find_element(By.ID, "password")
                    password_field.clear()
                    password_field.send_keys(password)
                    # Debug: Browser agent action")
                except:
                    return {
                        "success": False,
                        "message": "Could not find password field on signin page",
                        "error": "Password field not found"
                    }
            
            # Find and click signin button
            try:
                signin_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In') or contains(text(), 'Sign in') or contains(text(), 'Login') or contains(text(), 'login')]")
                signin_button.click()
                # Debug: Browser agent action
            except:
                try:
                    signin_button = self.driver.find_element(By.TYPE, "submit")
                    signin_button.click()
                    # Debug: Browser agent action
                except:
                    return {
                        "success": False,
                        "message": "Could not find signin button on page",
                        "error": "Signin button not found"
                    }
            
            # Wait for redirect to dashboard
            time.sleep(5)
            
            # Check if successfully signed in (should redirect to dashboard)
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            if "dashboard" in current_url.lower() or "giktransport.giki.edu.pk:8038/" in current_url:
                # Success: Browser agent
                return {
                    "success": True,
                    "message": f"Successfully signed in to GIKI Transport! You are now on the dashboard. Page title: {page_title}",
                    "action": "signin",
                    "url": current_url,
                    "title": page_title
                }
            else:
                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
                    if error_elements:
                        error_text = error_elements[0].text
                        return {
                            "success": False,
                            "message": f"Signin failed: {error_text}",
                            "error": error_text
                        }
                except:
                    pass
                
                return {
                    "success": False,
                    "message": "Signin may have failed - not redirected to dashboard",
                    "error": "No redirect to dashboard detected"
                }
            
        except Exception as e:
            error_msg = f"Signin process failed: {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "message": f"Failed to signin. {error_msg}",
                "error": error_msg
            }
    
    def handle_signup(self) -> Dict[str, Any]:
        """
        Handle signup process for GIKI Transport.
        
        Returns:
            Response with signup result
        """
        try:
            signup_url = "https://giktransport.giki.edu.pk:8038/auth/signup/"
            # Debug: Browser agent action
            
            result = self.navigate_to_url(signup_url)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Navigated to signup page. Please fill in your details to create a new account.",
                    "action": "signup",
                    "url": signup_url
                }
            else:
                return result
                
        except Exception as e:
            error_msg = f"Signup navigation failed: {str(e)}"
            # Error: Browser agent
            return {
                "success": False,
                "message": f"Failed to navigate to signup page. {error_msg}",
                "error": error_msg
            }

    def run_automated_demo(self) -> Dict[str, Any]:
        """Run automated demo showcasing all GIKI Transport functionalities with voice narration."""
        try:
            print("🎬 Starting GIKI Transport Demo...")
            
            # Get voice agent for narration
            voice_agent = None
            try:
                from agents.voice_agent import VoiceAgent
                voice_agent = VoiceAgent()
                # Set higher volume for better audibility
                voice_agent.volume = 1  # Increase volume to 90%
                voice_agent.speak_response("Welcome to GIKI Transport demo! I'll show you all features quickly.")
                time.sleep(0.5)  # Reduced from 2 seconds
            except Exception as e:
                print(f"Voice agent not available: {e}")
            
            # Initialize browser first
            if not self.is_initialized:
                print("🔄 Initializing browser for demo...")
                if voice_agent:
                    voice_agent.speak_response("Initializing the browser for our demonstration.")
                self.initialize_browser(headless=False)
                time.sleep(0.2)
            
            demo_steps = []
            
            # Step 1: Main website
            print("📝 Step 1: Opening main website...")
            if voice_agent:
                voice_agent.speak_response("Step 1: Opening main website.")
            result = self.navigate_to_url("https://giktransport.giki.edu.pk:8038/")
            if result["success"]:
                demo_steps.append("✅ Opened main website")
                print("✅ Main website opened successfully")
                if voice_agent:
                    voice_agent.speak_response("Great! Homepage loaded successfully.")
            else:
                demo_steps.append("❌ Failed to open main website")
                print(f"❌ Failed to open main website: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Issue loading website.")
            
            if voice_agent:
                voice_agent.speak_response("Moving to sign-in page.")
            time.sleep(0.5)  # Reduced significantly
            
            # Step 2: Signin page
            print("📝 Step 2: Navigating to signin page...")
            if voice_agent:
                voice_agent.speak_response("Step 2: Accessing sign-in page.")
            result = self.navigate_to_url("https://giktransport.giki.edu.pk:8038/auth/signin/")
            if result["success"]:
                demo_steps.append("✅ Navigated to signin page")
                print("✅ Signin page loaded successfully")
                if voice_agent:
                    voice_agent.speak_response("Sign-in page loaded. Now logging in automatically.")
            else:
                demo_steps.append("❌ Failed to navigate to signin page")
                print(f"❌ Failed to navigate to signin page: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Issue with sign-in page.")
            
            time.sleep(0.5)  # Reduced significantly
            
            # Step 3: Sign in
            print("📝 Step 3: Signing in...")
            if voice_agent:
                voice_agent.speak_response("Step 3: Signing in automatically.")
            result = self.handle_signin()
            if result["success"]:
                demo_steps.append("✅ Signed in successfully")
                print("✅ Signin completed successfully")
                if voice_agent:
                    voice_agent.speak_response("Excellent! Successfully logged in to dashboard.")
            else:
                demo_steps.append("⚠️ Signin attempted but may have failed")
                print(f"⚠️ Signin issue: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Login encountered an issue, continuing demo.")
            
            time.sleep(1)  # Reduced significantly
            
            # Step 4: Dashboard
            print("📝 Step 4: Exploring dashboard...")
            if voice_agent:
                voice_agent.speak_response("Step 4: Exploring main dashboard.")
            result = self.navigate_to_url("https://giktransport.giki.edu.pk:8038/")
            if result["success"]:
                demo_steps.append("✅ Explored dashboard")
                print("✅ Dashboard loaded successfully")
                if voice_agent:
                    voice_agent.speak_response("Dashboard loaded! Central hub for all transport services.")
            else:
                demo_steps.append("❌ Failed to load dashboard")
                print(f"❌ Dashboard error: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Dashboard loading issue.")
            
            time.sleep(1)  # Reduced significantly
            
            # Step 5: Profile
            print("📝 Step 5: Visiting profile page...")
            if voice_agent:
                voice_agent.speak_response("Step 5: Checking user profile.")
            result = self.check_profile()
            if result["success"]:
                demo_steps.append("✅ Visited profile page")
                print("✅ Profile page loaded successfully")
                if voice_agent:
                    voice_agent.speak_response("Profile page loaded! Account management section.")
            else:
                demo_steps.append("❌ Failed to visit profile page")
                print(f"❌ Profile page error: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Profile page issue.")
            
            time.sleep(1)  # Reduced significantly
            
            # Step 6: Tickets
            print("📝 Step 6: Checking tickets page...")
            if voice_agent:
                voice_agent.speak_response("Step 6: Checking tickets page.")
            result = self.check_tickets()
            if result["success"]:
                demo_steps.append("✅ Checked tickets page")
                print("✅ Tickets page loaded successfully")
                if voice_agent:
                    voice_agent.speak_response("Tickets page loaded! View all bookings here.")
            else:
                demo_steps.append("❌ Failed to check tickets page")
                print(f"❌ Tickets page error: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Tickets page issue.")
            
            time.sleep(1)  # Reduced significantly
            
            # Step 7: Booking
            print("📝 Step 7: Accessing booking page...")
            if voice_agent:
                voice_agent.speak_response("Step 7: Accessing booking system.")
            result = self.click_book_ticket_button()
            if result["success"]:
                demo_steps.append("✅ Accessed booking page")
                print("✅ Booking page loaded successfully")
                if voice_agent:
                    voice_agent.speak_response("Booking page loaded! Ticket reservation system.")
            else:
                demo_steps.append("❌ Failed to access booking page")
                print(f"❌ Booking page error: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Booking page issue.")
            
            time.sleep(1)  # Reduced significantly
            
            # Step 8: Return to dashboard
            print("📝 Step 8: Returning to dashboard...")
            if voice_agent:
                voice_agent.speak_response("Step 8: Returning to main dashboard.")
            result = self.navigate_to_url("https://giktransport.giki.edu.pk:8038/")
            if result["success"]:
                demo_steps.append("✅ Demo completed")
                print("✅ Demo completed successfully")
                if voice_agent:
                    voice_agent.speak_response("Demo complete! You've seen all GIKI Transport features - homepage, authentication, dashboard, profile, tickets, and booking system.")
            else:
                demo_steps.append("❌ Demo ended with error")
                print(f"❌ Demo completion error: {result.get('error', 'Unknown error')}")
                if voice_agent:
                    voice_agent.speak_response("Demo completed with some issues.")
            
            if voice_agent:
                voice_agent.speak_response("Thank you for watching! This shows the power of voice-controlled navigation. Do you have any questions about the GIKI Transport system?")
            
            # Start intelligent Q&A session
            self.start_intelligent_qa_session(voice_agent)
            
            time.sleep(0.5)  # Reduced significantly
            
            summary = "🎬 GIKI Transport Demo Completed!\n\n"
            summary += "Demonstrated features:\n"
            for step in demo_steps:
                summary += f"• {step}\n"
            summary += "\n🌟 Demo finished with voice narration!"
            
            return {
                "success": True,
                "message": summary,
                "action": "demo",
                "steps_completed": len(demo_steps)
            }
            
        except Exception as e:
            error_msg = f"Demo failed: {str(e)}"
            print(f"❌ Demo error: {error_msg}")
            return {
                "success": False,
                "message": f"Demo failed: {error_msg}",
                "error": str(e)
            }
    
    def start_intelligent_qa_session(self, voice_agent):
        """Start Q&A with LLM - improved with proper timing and shorter answers."""
        try:
            from agents.intent_parsing_agent import IntentParsingAgent
            intent_agent = IntentParsingAgent()
            
            print("\n🤖 Starting intelligent Q&A session...")
            print("🎙️ Say your question clearly, then wait for the complete answer")
            
            for i in range(3):  # Allow 3 questions
                try:
                    print(f"\n📝 Question {i+1}/3:")
                    
                    if voice_agent:
                        # Clear prompt for user
                        voice_agent.speak_response("What's your question?")
                        
                        # Wait for speech to finish completely
                        print("⏳ Waiting for speech to complete...")
                        time.sleep(3)  # Ensure TTS finishes
                        
                        print("🎙️ Listening for your question...")
                        question = voice_agent.listen_and_transcribe()
                    else:
                        question = input("Enter your question: ").strip()
                    
                    if not question or question.lower() in ['no', 'done', 'exit', 'stop']:
                        print("👋 Q&A session ended")
                        break
                    
                    print(f"❓ Your question: {question}")
                    
                    # Generate SHORT LLM answer
                    try:
                        print("🧠 Generating answer...")
                        response = intent_agent.groq_client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[
                                {
                                    "role": "system", 
                                    "content": "Answer in exactly 1-2 short sentences about GIKI Transport. Be very concise and clear."
                                },
                                {
                                    "role": "user", 
                                    "content": f"GIKI Transport question: {question}"
                                }
                            ],
                            max_tokens=40,  # Reduced for shorter answers
                            temperature=0.3
                        )
                        answer = response.choices[0].message.content.strip()
                    except Exception as llm_error:
                        print(f"⚠️ LLM error: {llm_error}")
                        # Short fallback answers
                        if 'book' in question.lower():
                            answer = "Use voice commands to book tickets instantly."
                        elif 'voice' in question.lower():
                            answer = "Complete voice control for all features."
                        elif 'profile' in question.lower():
                            answer = "Manage account settings and information."
                        else:
                            answer = "GIKI Transport offers comprehensive transport services."
                    
                    print(f"💡 Answer: {answer}")
                    
                    if voice_agent:
                        print("🔊 Speaking answer...")
                        voice_agent.speak_response(answer)
                        
                        # Calculate proper wait time for TTS completion
                        # Conservative timing: 60ms per character + 4 second buffer
                        wait_time = len(answer) * 0.06 + 4.0
                        print(f"⏳ Waiting {wait_time:.1f} seconds for speech to complete...")
                        
                        time.sleep(wait_time)
                        print("✅ Speech completed, ready for next question")
                    
                except Exception as question_error:
                    print(f"❌ Error in question {i+1}: {question_error}")
                    continue
            
            print("\n🎉 Q&A session completed!")
            if voice_agent:
                voice_agent.speak_response("Q&A session finished. Thank you!")
                
        except Exception as e:
            print(f"❌ Q&A session error: {e}")

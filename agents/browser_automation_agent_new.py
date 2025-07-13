"""
Browser Automation Agent - Streamlined with Interactive Demo Support
Handles navigation, clicking, filling forms, scrolling, and interactive demos with Q&A
"""

import time
from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import our modular components
from .browser_modules import BrowserCore, GIKITransportActions, InteractiveDemo

class BrowserAutomationAgent:
    """
    Streamlined Browser Automation Agent with Interactive Demo Support
    """
    
    def __init__(self):
        # Initialize core components
        self.browser_core = BrowserCore()
        self.giki_actions = GIKITransportActions(self.browser_core)
        self.interactive_demo = InteractiveDemo(self.browser_core, self.giki_actions)
        
        # Legacy compatibility
        self.driver = None
        self.wait = None
        self.is_initialized = False
    
    def initialize_browser(self, headless: bool = None):
        """Initialize the browser instance."""
        self.browser_core.initialize_browser(headless)
        # Update legacy references
        self.driver = self.browser_core.driver
        self.wait = self.browser_core.wait
        self.is_initialized = self.browser_core.is_initialized
    
    def set_agents(self, voice_agent, intent_agent):
        """Set the voice and intent agents for interactive demo"""
        self.interactive_demo.set_agents(voice_agent, intent_agent)
    
    # Legacy method compatibility
    def execute_intent(self, intent_data: Dict[str, Any]) -> str:
        """Execute a browser action based on structured intent."""
        try:
            if not self.is_initialized:
                self.initialize_browser()
            
            intent = intent_data.get("intent", "unknown")
            
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
            return {
                "success": False,
                "error": error_msg,
                "message": f"I encountered an error: {error_msg}"
            }
    
    def handle_navigate(self, intent_data: Dict[str, Any]) -> str:
        """Handle navigation intent."""
        try:
            target_url = intent_data.get("target_url")
            if not target_url:
                return {"success": False, "message": "I couldn't navigate because no URL was specified.", "error": "No URL specified"}
            
            return self.browser_core.navigate_to_url(target_url)
            
        except Exception as e:
            error_msg = f"Navigation failed: {str(e)}"
            return {
                "success": False,
                "error": error_msg,
                "message": f"I couldn't navigate to the page. {error_msg}"
            }
    
    def handle_click(self, intent_data: Dict[str, Any]) -> str:
        """Handle click intent."""
        try:
            element_text = intent_data.get("element_text")
            element_selector = intent_data.get("element_selector")
            
            if not element_text and not element_selector:
                return {"success": False, "message": "I couldn't click because no element was specified.", "error": "No element specified"}
            
            target = element_text or element_selector
            
            # Try to find and click the element
            try:
                element = None
                
                if element_text:
                    try:
                        element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{element_text}')]")
                    except:
                        try:
                            element = self.driver.find_element(By.PARTIAL_LINK_TEXT, element_text)
                        except:
                            try:
                                element = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{element_text}')]")
                            except:
                                pass
                
                if not element and element_selector:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
                    except:
                        pass
                
                if element:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    element.click()
                    explanation = f"I clicked on '{target}' and the action was completed."
                else:
                    explanation = f"I couldn't find the element '{target}' to click."
                    
            except Exception as e:
                explanation = f"I had trouble clicking '{target}': {str(e)}"
            
            return {"success": True, "message": explanation, "action": "click", "target": target}
            
        except Exception as e:
            error_msg = f"Click failed: {str(e)}"
            return {"success": False, "message": f"I couldn't click the element. {error_msg}", "error": error_msg}
    
    def handle_fill(self, intent_data: Dict[str, Any]) -> str:
        """Handle fill/input intent."""
        try:
            field_name = intent_data.get("field_name")
            value = intent_data.get("value")
            
            if not field_name or not value:
                return {"success": False, "message": "I couldn't fill the field because field name or value is missing.", "error": "Missing field name or value"}
            
            # Try to find and fill the field
            try:
                element = None
                
                # Try multiple strategies to find the field
                try:
                    element = self.driver.find_element(By.NAME, field_name)
                except:
                    try:
                        element = self.driver.find_element(By.ID, field_name)
                    except:
                        try:
                            element = self.driver.find_element(By.XPATH, f"//input[@placeholder='{field_name}']")
                        except:
                            try:
                                element = self.driver.find_element(By.XPATH, f"//input[@type='text' or @type='email' or @type='password'][preceding-sibling::label[contains(text(), '{field_name}')]]")
                            except:
                                pass
                
                if element:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    element.clear()
                    element.send_keys(value)
                    explanation = f"I filled in the {field_name} field with '{value}'."
                else:
                    explanation = f"I couldn't find the {field_name} field to fill."
                    
            except Exception as e:
                explanation = f"I had trouble filling the {field_name} field: {str(e)}"
            
            return {"success": True, "message": explanation, "action": "fill", "field": field_name, "value": value}
            
        except Exception as e:
            error_msg = f"Fill failed: {str(e)}"
            return {"success": False, "message": f"I couldn't fill the field. {error_msg}", "error": error_msg}
    
    def handle_scroll(self, intent_data: Dict[str, Any]) -> str:
        """Handle scroll intent."""
        try:
            direction = intent_data.get("direction", "down")
            
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
            
            return {"success": True, "message": explanation, "action": "scroll", "direction": direction}
            
        except Exception as e:
            error_msg = f"Scroll failed: {str(e)}"
            return {"success": False, "message": f"I couldn't scroll the page. {error_msg}", "error": error_msg}
    
    def handle_wait(self, intent_data: Dict[str, Any]) -> str:
        """Handle wait intent."""
        try:
            duration = intent_data.get("duration", 2)
            
            if isinstance(duration, str):
                try:
                    duration = float(duration)
                except:
                    duration = 2
            
            time.sleep(duration)
            explanation = f"I waited for {duration} seconds."
            
            return {"success": True, "message": explanation, "action": "wait", "duration": duration}
            
        except Exception as e:
            error_msg = f"Wait failed: {str(e)}"
            return {"success": False, "message": f"I couldn't wait properly. {error_msg}", "error": error_msg}
    
    def handle_unknown_intent(self, intent_data: Dict[str, Any]) -> str:
        """Handle unknown or unsupported intents."""
        intent = intent_data.get("intent", "unknown")
        
        return {"success": False, "message": f"I don't understand how to handle the '{intent}' action. Could you try rephrasing your command?", "error": f"Unknown intent: {intent}"}
    
    def handle_question(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle question intent."""
        try:
            question = intent_data.get("question", "")
            
            if not question:
                return {
                    "success": False,
                    "message": "No question was provided.",
                    "error": "Missing question"
                }
            
            from agents.intent_parsing_agent import IntentParsingAgent
            intent_agent = IntentParsingAgent()
            answer = intent_agent.answer_question(question)
            
            return {
                "success": True,
                "message": answer,
                "action": "question",
                "question": question,
                "answer": answer
            }
            
        except Exception as e:
            error_msg = f"Question answering failed: {str(e)}"
            return {
                "success": False,
                "message": f"I couldn't answer that question. {error_msg}",
                "error": error_msg
            }
    
    # Delegate methods to modules
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a specific URL."""
        return self.browser_core.navigate_to_url(url)
    
    def handle_signin(self, email: str = None, password: str = None) -> Dict[str, Any]:
        """Handle signin process."""
        return self.giki_actions.handle_signin(email, password)
    
    def handle_signup(self) -> Dict[str, Any]:
        """Handle signup process."""
        return self.giki_actions.handle_signup()
    
    def check_tickets(self) -> Dict[str, Any]:
        """Check user's tickets."""
        return self.giki_actions.check_tickets()
    
    def check_profile(self) -> Dict[str, Any]:
        """Check user's profile."""
        return self.giki_actions.check_profile()
    
    def handle_booking_flow(self) -> Dict[str, Any]:
        """Handle booking flow."""
        return self.giki_actions.handle_booking_flow()
    
    def click_book_ticket_button(self) -> Dict[str, Any]:
        """Navigate to booking page."""
        return self.giki_actions.click_book_ticket_button()
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        return self.browser_core.get_page_info()
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot."""
        return self.browser_core.take_screenshot(filename)
    
    def close_browser(self):
        """Close the browser."""
        self.browser_core.close_browser()
    
    # NEW: Interactive Demo Methods
    def run_automated_demo(self) -> Dict[str, Any]:
        """Run the old automated demo (legacy support)."""
        return self.run_interactive_demo()
    
    def run_interactive_demo(self) -> Dict[str, Any]:
        """Run the new interactive demo with Q&A support."""
        return self.interactive_demo.run_interactive_demo()
    
    def handle_demo_question(self, question: str) -> Dict[str, Any]:
        """Handle a question during the demo."""
        return self.interactive_demo.handle_demo_question(question)
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close_browser()

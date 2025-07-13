"""
Dynamic Demo Executor - Handles demo execution for any configured product
"""

import time
import threading
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from demo_config import ProductConfig, DemoStep

class DynamicDemoExecutor:
    """Execute demos dynamically based on configuration"""
    
    def __init__(self, voice_agent=None):
        self.voice_agent = voice_agent
        self.driver = None
        self.demo_config = None
        self.demo_running = False
        self.question_queue = []
        self.current_step_index = 0
        
    def initialize_browser(self, headless=False):
        """Initialize Chrome browser"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            print("✅ Dynamic demo browser initialized")
            return True
            
        except Exception as e:
            print(f"❌ Browser initialization failed: {e}")
            return False
    
    def set_demo_config(self, config: ProductConfig):
        """Set the demo configuration"""
        self.demo_config = config
        self.current_step_index = 0
        print(f"📋 Demo configuration set: {config.product_name}")
    
    def run_interactive_demo(self) -> Dict[str, Any]:
        """Run interactive demo based on current configuration"""
        if not self.demo_config:
            return {
                'success': False,
                'message': 'No demo configuration loaded'
            }
        
        try:
            self.demo_running = True
            print(f"🎬 Starting Interactive Demo: {self.demo_config.product_name}")
            
            # Initialize browser if not already done
            if not self.driver:
                if not self.initialize_browser():
                    return {
                        'success': False,
                        'message': 'Failed to initialize browser'
                    }
            
            # Welcome message
            if self.demo_config.welcome_message and self.voice_agent:
                self.voice_agent.speak_response(self.demo_config.welcome_message)
            
            # Execute demo steps
            completed_steps = []
            
            for i, step in enumerate(self.demo_config.demo_steps):
                self.current_step_index = i
                print(f"📝 Step {i+1}: {step.name}")
                
                # Speak step narration
                narration = step.voice_script or f"Step {i+1}: {step.description}"
                if self.voice_agent:
                    self.voice_agent.speak_response(narration)
                
                # Execute step action
                step_result = self.execute_step(step)
                completed_steps.append({
                    'name': step.name,
                    'success': step_result['success'],
                    'message': step_result.get('message', '')
                })
                
                # Wait between steps
                time.sleep(step.wait_time)
                
                # Check for questions during demo
                self.check_for_questions()
            
            # Closing message
            if self.demo_config.closing_message and self.voice_agent:
                self.voice_agent.speak_response(self.demo_config.closing_message)
            
            self.demo_running = False
            
            return {
                'success': True,
                'message': f'🎬 Interactive Demo Completed: {self.demo_config.product_name}',
                'steps_completed': len(completed_steps),
                'steps': completed_steps
            }
            
        except Exception as e:
            self.demo_running = False
            error_msg = f"Demo execution failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
    
    def execute_step(self, step: DemoStep) -> Dict[str, Any]:
        """Execute a single demo step"""
        try:
            if step.action_type == "navigate":
                return self.navigate_to_url(step.url)
            
            elif step.action_type == "login":
                return self.handle_login(step)
            
            elif step.action_type == "click":
                return self.click_element(step.element_selector)
            
            elif step.action_type == "form_fill":
                return self.fill_form(step)
            
            elif step.action_type == "showcase":
                return self.showcase_page(step)
            
            else:
                # Default to navigation
                return self.navigate_to_url(step.url)
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Step execution failed: {str(e)}"
            }
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            
            title = self.driver.title
            current_url = self.driver.current_url
            
            return {
                'success': True,
                'message': f'Successfully navigated to {url}',
                'url': current_url,
                'title': title
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Navigation failed: {str(e)}'
            }
    
    def handle_login(self, step: DemoStep) -> Dict[str, Any]:
        """Handle login if credentials are provided"""
        try:
            if not self.demo_config.login_credentials:
                return {
                    'success': False,
                    'message': 'No login credentials configured'
                }
            
            # Navigate to login page first
            if step.url:
                self.driver.get(step.url)
                time.sleep(2)
            
            # Try common login form selectors
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="username"]',
                '#email',
                '#username',
                '.email-input'
            ]
            
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                '#password',
                '.password-input'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button.login-btn',
                'button.submit-btn',
                '.login-button'
            ]
            
            # Fill email/username
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if email_field:
                email_field.clear()
                email_field.send_keys(self.demo_config.login_credentials.get('email', ''))
            
            # Fill password
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if password_field:
                password_field.clear()
                password_field.send_keys(self.demo_config.login_credentials.get('password', ''))
            
            # Submit form
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                submit_button.click()
                time.sleep(3)  # Wait for login to complete
            
            return {
                'success': True,
                'message': f'Login attempt completed for {self.demo_config.product_name}',
                'url': self.driver.current_url,
                'title': self.driver.title
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }
    
    def click_element(self, selector: str) -> Dict[str, Any]:
        """Click an element by selector"""
        try:
            if not selector:
                return {
                    'success': False,
                    'message': 'No element selector provided'
                }
            
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            
            time.sleep(2)  # Wait for action to complete
            
            return {
                'success': True,
                'message': f'Successfully clicked element: {selector}',
                'url': self.driver.current_url
            }
            
        except TimeoutException:
            return {
                'success': False,
                'message': f'Element not found or not clickable: {selector}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Click failed: {str(e)}'
            }
    
    def fill_form(self, step: DemoStep) -> Dict[str, Any]:
        """Fill form fields (placeholder for future implementation)"""
        try:
            # Navigate to the URL first
            if step.url:
                self.driver.get(step.url)
                time.sleep(2)
            
            # This is a placeholder - in a real implementation,
            # you would define form field mappings in the step configuration
            
            return {
                'success': True,
                'message': f'Form showcase completed for {step.name}',
                'url': self.driver.current_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Form handling failed: {str(e)}'
            }
    
    def showcase_page(self, step: DemoStep) -> Dict[str, Any]:
        """Showcase a page (navigate and describe)"""
        try:
            # Navigate to the page
            result = self.navigate_to_url(step.url)
            
            # Add some visual effects or highlights here if needed
            time.sleep(1)
            
            return {
                'success': True,
                'message': f'Page showcase completed: {step.name}',
                'url': self.driver.current_url,
                'title': self.driver.title
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Page showcase failed: {str(e)}'
            }
    
    def check_for_questions(self):
        """Check if there are any questions during demo (placeholder)"""
        # This would integrate with the voice system to handle questions
        # For now, it's just a placeholder
        pass
    
    def handle_demo_question(self, question: str) -> str:
        """Handle questions during demo"""
        try:
            print(f"🤔 Demo question: {question}")
            
            # Generate contextual answer based on current demo config
            if self.demo_config:
                product_context = f"about {self.demo_config.product_name}"
                base_answer = f"That's a great question {product_context}! "
            else:
                base_answer = "That's a great question! "
            
            # Simple question handling based on keywords
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['what', 'about', 'tell me']):
                answer = base_answer + f"This demo showcases {self.demo_config.product_name}, which is {self.demo_config.description}. You're seeing how users can interact with our platform seamlessly!"
            
            elif any(word in question_lower for word in ['how', 'work', 'use']):
                answer = base_answer + f"{self.demo_config.product_name} works by providing an intuitive interface that makes complex tasks simple. As you can see in the demo, everything is designed for ease of use!"
            
            elif any(word in question_lower for word in ['features', 'functionality']):
                answer = base_answer + f"{self.demo_config.product_name} includes all the features you're seeing in this demo and much more. Each step shows different capabilities of our platform!"
            
            else:
                answer = base_answer + f"{self.demo_config.product_name} is designed to provide the best user experience. Would you like me to show you a specific feature?"
            
            if self.voice_agent:
                self.voice_agent.speak_response(answer)
            
            return answer
            
        except Exception as e:
            error_msg = f"I apologize, I encountered an issue: {str(e)}"
            if self.voice_agent:
                self.voice_agent.speak_response(error_msg)
            return error_msg
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                print("🧹 Browser cleanup completed")
        except Exception as e:
            print(f"⚠️ Browser cleanup warning: {e}")

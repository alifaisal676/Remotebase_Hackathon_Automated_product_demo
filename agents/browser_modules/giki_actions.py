"""
GIKI Transport Actions Module - Specific GIKI Transport functionality
"""

import time
from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class GIKITransportActions:
    """GIKI Transport specific actions"""
    
    def __init__(self, browser_core):
        self.browser_core = browser_core
    
    def handle_signin(self, email: str = None, password: str = None) -> Dict[str, Any]:
        """Handle signin process for GIKI Transport."""
        try:
            # Default credentials
            if not email:
                email = "alifaisalkhn@gmail.com"
            if not password:
                password = "Alifaisal123@"
            
            signin_url = "https://giktransport.giki.edu.pk:8038/auth/signin/"
            
            # Navigate to signin page
            result = self.browser_core.navigate_to_url(signin_url)
            
            if not result["success"]:
                return result
            
            # Quick page load wait
            time.sleep(1.5)  # Reduced from 3 seconds
            
            # Find and fill email field
            try:
                email_field = self.browser_core.wait.until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                email_field.clear()
                email_field.send_keys(email)
            except:
                try:
                    email_field = self.browser_core.driver.find_element(By.ID, "email")
                    email_field.clear()
                    email_field.send_keys(email)
                except:
                    return {
                        "success": False,
                        "message": "Could not find email field on signin page",
                        "error": "Email field not found"
                    }
            
            # Find and fill password field
            try:
                password_field = self.browser_core.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(password)
            except:
                try:
                    password_field = self.browser_core.driver.find_element(By.ID, "password")
                    password_field.clear()
                    password_field.send_keys(password)
                except:
                    return {
                        "success": False,
                        "message": "Could not find password field on signin page",
                        "error": "Password field not found"
                    }
            
            # Find and click signin button
            try:
                signin_button = self.browser_core.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In') or contains(text(), 'Sign in') or contains(text(), 'Login') or contains(text(), 'login')]")
                signin_button.click()
            except:
                try:
                    signin_button = self.browser_core.driver.find_element(By.TYPE, "submit")
                    signin_button.click()
                except:
                    return {
                        "success": False,
                        "message": "Could not find signin button on page",
                        "error": "Signin button not found"
                    }
            
            # Quick wait for redirect to dashboard
            time.sleep(1.5)  # Reduced from 3 seconds
            
            # Check if successfully signed in
            current_url = self.browser_core.driver.current_url
            page_title = self.browser_core.driver.title
            
            if "dashboard" in current_url.lower() or "giktransport.giki.edu.pk:8038/" in current_url:
                return {
                    "success": True,
                    "message": f"Successfully signed in to GIKI Transport! You are now on the dashboard. Page title: {page_title}",
                    "action": "signin",
                    "url": current_url,
                    "title": page_title
                }
            else:
                return {
                    "success": False,
                    "message": "Signin may have failed - not redirected to dashboard",
                    "error": "No redirect to dashboard detected"
                }
            
        except Exception as e:
            error_msg = f"Signin process failed: {str(e)}"
            return {
                "success": False,
                "message": f"Failed to signin. {error_msg}",
                "error": error_msg
            }
    
    def handle_signup(self) -> Dict[str, Any]:
        """Handle signup process for GIKI Transport."""
        try:
            signup_url = "https://giktransport.giki.edu.pk:8038/auth/signup/"
            
            result = self.browser_core.navigate_to_url(signup_url)
            
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
            return {
                "success": False,
                "message": f"Failed to navigate to signup page. {error_msg}",
                "error": error_msg
            }
    
    def check_tickets(self) -> Dict[str, Any]:
        """Check user's tickets in GIKI Transport with multiple attempts."""
        try:
            # Try multiple possible URLs for tickets page
            ticket_urls = [
                "https://giktransport.giki.edu.pk:8038/my-tickets/",
                "https://giktransport.giki.edu.pk:8038/tickets/",
                "https://giktransport.giki.edu.pk:8038/user/tickets/",
                "https://giktransport.giki.edu.pk:8038/"  # Fallback to dashboard
            ]
            
            for tickets_url in ticket_urls:
                print(f"🎫 Trying tickets URL: {tickets_url}")
                
                result = self.browser_core.navigate_to_url(tickets_url)
                
                if result["success"]:
                    # Wait for page to load
                    time.sleep(2)
                    
                    # Check if we're on a valid page
                    current_url = self.browser_core.driver.current_url
                    page_title = self.browser_core.driver.title
                    
                    # Look for tickets-related content
                    try:
                        # Try to find ticket-related elements
                        ticket_elements = self.browser_core.driver.find_elements(By.XPATH, 
                            "//*[contains(text(), 'ticket') or contains(text(), 'Ticket') or contains(text(), 'booking') or contains(text(), 'Booking')]")
                        
                        if ticket_elements or "ticket" in page_title.lower() or "ticket" in current_url.lower():
                            return {
                                "success": True,
                                "message": f"Successfully accessed tickets page! Here you can view your transport bookings and ticket history. Page loaded: {page_title}",
                                "action": "tickets",
                                "url": current_url,
                                "title": page_title
                            }
                        elif tickets_url == ticket_urls[-1]:  # Last URL (dashboard)
                            # Try to find tickets link from dashboard
                            try:
                                ticket_link_result = self.find_tickets_from_dashboard()
                                if ticket_link_result["success"]:
                                    return ticket_link_result
                            except:
                                pass
                            
                            return {
                                "success": True,
                                "message": "Navigated to the main dashboard. From here you can access your tickets through the navigation menu or by looking for 'My Tickets' or 'Bookings' section.",
                                "action": "tickets_dashboard",
                                "url": current_url,
                                "title": page_title
                            }
                    except Exception as e:
                        print(f"⚠️ Error checking page content: {e}")
                        continue
                else:
                    print(f"❌ Failed to navigate to {tickets_url}")
                    continue
            
            # If all URLs failed
            return {
                "success": False,
                "message": "Unable to access tickets page. The page might be temporarily unavailable or require different navigation.",
                "error": "All ticket URL attempts failed"
            }
                
        except Exception as e:
            error_msg = f"Ticket check failed: {str(e)}"
            return {
                "success": False,
                "message": f"Failed to check tickets. The tickets page may be temporarily unavailable. Error: {error_msg}",
                "error": error_msg
            }
    
    def check_profile(self) -> Dict[str, Any]:
        """Check user's profile in GIKI Transport."""
        try:
            profile_url = "https://giktransport.giki.edu.pk:8038/auth/profile/"
            
            result = self.browser_core.navigate_to_url(profile_url)
            
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
            return {
                "success": False,
                "message": f"Failed to check profile. {error_msg}",
                "error": error_msg
            }
    
    def handle_booking_flow(self) -> Dict[str, Any]:
        """Handle booking flow for GIKI Transport."""
        try:
            booking_url = "https://giktransport.giki.edu.pk:8038/booking/payment/wallet/5/"
            print(f"🌐 Navigating directly to booking payment page: {booking_url}")
            
            result = self.browser_core.navigate_to_url(booking_url)
            
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
            
            result = self.browser_core.navigate_to_url(booking_url)
            
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
    
    def find_tickets_from_dashboard(self) -> Dict[str, Any]:
        """Try to find tickets link from the current dashboard page."""
        try:
            # Look for tickets/booking links on the current page
            ticket_links = [
                "//a[contains(text(), 'Ticket') or contains(text(), 'ticket')]",
                "//a[contains(text(), 'Booking') or contains(text(), 'booking')]", 
                "//a[contains(text(), 'My Tickets')]",
                "//a[contains(@href, 'ticket')]",
                "//a[contains(@href, 'booking')]",
                "//button[contains(text(), 'Ticket') or contains(text(), 'ticket')]"
            ]
            
            for xpath in ticket_links:
                try:
                    elements = self.browser_core.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        element = elements[0]
                        element.click()
                        time.sleep(2)
                        
                        current_url = self.browser_core.driver.current_url
                        page_title = self.browser_core.driver.title
                        
                        return {
                            "success": True,
                            "message": f"Found and clicked tickets link! Now viewing: {page_title}",
                            "action": "tickets_found",
                            "url": current_url,
                            "title": page_title
                        }
                except Exception as e:
                    continue
            
            return {
                "success": False,
                "message": "No tickets link found on the current page. You may need to look for a 'My Tickets' or 'Bookings' section in the navigation menu.",
                "error": "No tickets link found"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching for tickets link: {str(e)}",
                "error": str(e)
            }

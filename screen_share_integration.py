"""
Screen Sharing Integration
Handles automatic screen sharing for live demos
"""

import subprocess
import platform
import time
import pyautogui
import psutil
from typing import Dict, Any, Optional

class ScreenShareManager:
    """Manages screen sharing across different platforms"""
    
    def __init__(self):
        self.is_sharing = False
        self.sharing_process = None
        self.platform = platform.system().lower()
        
    def start_screen_share_google_meet(self) -> Dict[str, Any]:
        """Start screen sharing in Google Meet"""
        try:
            print("🖥️ Starting screen share in Google Meet...")
            
            # Wait for Google Meet to be ready
            time.sleep(2)
            
            # Use keyboard shortcut Ctrl+Alt+S (Google Meet screen share shortcut)
            pyautogui.hotkey('ctrl', 'alt', 's')
            time.sleep(1)
            
            # Alternative: Try Ctrl+Alt+Here for some Google Meet versions
            if not self._check_screen_share_dialog():
                pyautogui.hotkey('ctrl', 'alt', 'here')
                time.sleep(1)
            
            # If still no dialog, try clicking the screen share button
            if not self._check_screen_share_dialog():
                self._click_screen_share_button_google_meet()
            
            # Select entire screen option
            time.sleep(1)
            pyautogui.press('tab')  # Navigate to "Entire screen"
            time.sleep(0.5)
            pyautogui.press('enter')  # Select entire screen
            time.sleep(1)
            pyautogui.press('enter')  # Confirm share
            
            self.is_sharing = True
            
            return {
                "success": True,
                "message": "Screen sharing started in Google Meet",
                "platform": "Google Meet"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start Google Meet screen share: {str(e)}"
            }
    
    def start_screen_share_zoom(self) -> Dict[str, Any]:
        """Start screen sharing in Zoom"""
        try:
            print("🖥️ Starting screen share in Zoom...")
            
            # Wait for Zoom to be ready
            time.sleep(2)
            
            # Use keyboard shortcut Alt+S (Zoom screen share shortcut)
            pyautogui.hotkey('alt', 's')
            time.sleep(1)
            
            # Alternative shortcut for some Zoom versions
            if not self._check_screen_share_dialog():
                pyautogui.hotkey('alt', 'shift', 's')
                time.sleep(1)
            
            # Select entire screen and start sharing
            time.sleep(1)
            pyautogui.press('enter')  # Usually selects the first screen by default
            
            self.is_sharing = True
            
            return {
                "success": True,
                "message": "Screen sharing started in Zoom",
                "platform": "Zoom"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start Zoom screen share: {str(e)}"
            }
    
    def start_screen_share_teams(self) -> Dict[str, Any]:
        """Start screen sharing in Microsoft Teams"""
        try:
            print("🖥️ Starting screen share in Microsoft Teams...")
            
            # Wait for Teams to be ready
            time.sleep(2)
            
            # Use keyboard shortcut Ctrl+Shift+E (Teams screen share shortcut)
            pyautogui.hotkey('ctrl', 'shift', 'e')
            time.sleep(2)
            
            # Select desktop and confirm
            pyautogui.press('tab')  # Navigate to desktop option
            time.sleep(0.5)
            pyautogui.press('enter')  # Select desktop
            time.sleep(1)
            pyautogui.press('enter')  # Confirm share
            
            self.is_sharing = True
            
            return {
                "success": True,
                "message": "Screen sharing started in Microsoft Teams",
                "platform": "Microsoft Teams"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start Teams screen share: {str(e)}"
            }
    
    def auto_detect_and_share(self) -> Dict[str, Any]:
        """Auto-detect the meeting platform and start screen sharing"""
        try:
            # Check which meeting app is running
            running_apps = self._get_running_meeting_apps()
            
            if 'chrome' in running_apps or 'edge' in running_apps:
                # Likely Google Meet (web-based)
                result = self.start_screen_share_google_meet()
                if result["success"]:
                    return result
            
            if 'zoom' in running_apps:
                result = self.start_screen_share_zoom()
                if result["success"]:
                    return result
            
            if 'teams' in running_apps:
                result = self.start_screen_share_teams()
                if result["success"]:
                    return result
            
            # Fallback: Try manual instructions
            return self._provide_manual_instructions()
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Auto-detection failed: {str(e)}"
            }
    
    def show_screen_share_instructions(self, platform: str = "auto") -> Dict[str, Any]:
        """Show screen sharing instructions for the platform"""
        instructions = {
            "google_meet": [
                "1. In Google Meet, click the 'Present now' button (screen icon)",
                "2. Select 'Your entire screen'",
                "3. Choose your main screen",
                "4. Click 'Share'",
                "Alternative: Press Ctrl+Alt+S"
            ],
            "zoom": [
                "1. In Zoom, click the 'Share Screen' button",
                "2. Select your screen",
                "3. Click 'Share'",
                "Alternative: Press Alt+S"
            ],
            "teams": [
                "1. In Teams, click the 'Share content' button",
                "2. Select 'Desktop'",
                "3. Choose your screen",
                "4. Click 'Confirm'",
                "Alternative: Press Ctrl+Shift+E"
            ],
            "generic": [
                "1. Look for a 'Share Screen' or 'Present' button in your meeting",
                "2. Click it and select your entire screen",
                "3. Confirm the sharing",
                "Common shortcuts: Ctrl+Alt+S (Meet), Alt+S (Zoom), Ctrl+Shift+E (Teams)"
            ]
        }
        
        platform_key = platform.lower().replace(" ", "_") if platform != "auto" else "generic"
        selected_instructions = instructions.get(platform_key, instructions["generic"])
        
        return {
            "success": True,
            "platform": platform,
            "instructions": selected_instructions,
            "message": f"Screen sharing instructions for {platform}"
        }
    
    def _get_running_meeting_apps(self) -> list:
        """Get list of running meeting applications"""
        running_apps = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                proc_name = proc.info['name'].lower()
                if any(app in proc_name for app in ['zoom', 'teams', 'chrome', 'edge', 'firefox']):
                    running_apps.append(proc_name)
        except Exception as e:
            print(f"⚠️ Error detecting running apps: {e}")
        
        return running_apps
    
    def _check_screen_share_dialog(self) -> bool:
        """Check if screen share dialog is open"""
        try:
            # This is a simplified check - in practice, you'd use more sophisticated detection
            time.sleep(0.5)
            return True  # Assume dialog opened for now
        except Exception:
            return False
    
    def _click_screen_share_button_google_meet(self):
        """Try to click the screen share button in Google Meet"""
        try:
            # This would need to be more sophisticated in practice
            # For now, we'll rely on keyboard shortcuts
            pass
        except Exception as e:
            print(f"⚠️ Could not click screen share button: {e}")
    
    def _provide_manual_instructions(self) -> Dict[str, Any]:
        """Provide manual screen sharing instructions"""
        return {
            "success": True,
            "message": "Please manually start screen sharing",
            "instructions": [
                "1. Look for a 'Share Screen' or 'Present' button in your meeting",
                "2. Click it and select your entire screen",
                "3. The demo will appear on your shared screen",
                "4. Your audience will see the live demo!"
            ],
            "shortcuts": {
                "Google Meet": "Ctrl+Alt+S",
                "Zoom": "Alt+S", 
                "Teams": "Ctrl+Shift+E"
            }
        }
    
    def stop_screen_share(self) -> Dict[str, Any]:
        """Stop screen sharing"""
        try:
            if not self.is_sharing:
                return {
                    "success": False,
                    "message": "No active screen sharing session"
                }
            
            # Try common stop sharing shortcuts
            pyautogui.hotkey('ctrl', 'alt', 's')  # Google Meet toggle
            time.sleep(0.5)
            pyautogui.hotkey('alt', 's')  # Zoom toggle
            
            self.is_sharing = False
            
            return {
                "success": True,
                "message": "Screen sharing stopped"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stop screen sharing: {str(e)}"
            }
    
    def get_sharing_status(self) -> Dict[str, Any]:
        """Get current screen sharing status"""
        return {
            "is_sharing": self.is_sharing,
            "platform": self.platform,
            "available_shortcuts": {
                "Google Meet": "Ctrl+Alt+S",
                "Zoom": "Alt+S",
                "Microsoft Teams": "Ctrl+Shift+E"
            }
        }

# Global screen share manager
screen_share_manager = ScreenShareManager()

"""
Live Meeting Integration System
Handles video conferencing, screen sharing, and live demo sessions
"""

import time
import threading
import subprocess
import webbrowser
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

try:
    from screen_share_integration import screen_share_manager
    SCREEN_SHARE_AVAILABLE = True
except ImportError:
    SCREEN_SHARE_AVAILABLE = False
    print("⚠️ Screen sharing not available - install pyautogui and psutil for full functionality")

class MeetingProvider:
    """Base class for meeting providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.meeting_id = None
        self.meeting_url = None
        self.is_active = False
    
    def create_meeting(self, title: str, description: str = "", duration_minutes: int = 60) -> Dict[str, Any]:
        """Create a new meeting"""
        raise NotImplementedError
    
    def join_meeting(self, meeting_url: str) -> bool:
        """Join an existing meeting"""
        raise NotImplementedError
    
    def start_screen_share(self) -> bool:
        """Start screen sharing"""
        raise NotImplementedError
    
    def stop_screen_share(self) -> bool:
        """Stop screen sharing"""
        raise NotImplementedError
    
    def get_meeting_info(self) -> Dict[str, Any]:
        """Get current meeting information"""
        return {
            "meeting_id": self.meeting_id,
            "meeting_url": self.meeting_url,
            "is_active": self.is_active,
            "provider": self.__class__.__name__
        }

class GoogleMeetProvider(MeetingProvider):
    """Google Meet integration"""
    
    def create_meeting(self, title: str, description: str = "", duration_minutes: int = 60) -> Dict[str, Any]:
        """Create a Google Meet meeting"""
        try:
            # Generate a simple Google Meet URL (for MVP - in production, use Google Calendar API)
            self.meeting_id = f"demo-{uuid.uuid4().hex[:8]}"
            
            # For now, we'll use the simple meet.google.com/new approach
            # In production, you'd integrate with Google Calendar API
            self.meeting_url = f"https://meet.google.com/new"
            
            meeting_info = {
                "success": True,
                "meeting_id": self.meeting_id,
                "meeting_url": self.meeting_url,
                "title": title,
                "description": description,
                "duration_minutes": duration_minutes,
                "provider": "Google Meet",
                "instructions": [
                    "1. Click the meeting link to create a new Google Meet",
                    "2. Share the generated link with your customer",
                    "3. Wait for customer to join",
                    "4. Start screen sharing for the demo"
                ]
            }
            
            print(f"✅ Google Meet session prepared: {title}")
            return meeting_info
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Google Meet: {str(e)}"
            }
    
    def join_meeting(self, meeting_url: str) -> bool:
        """Join Google Meet meeting"""
        try:
            webbrowser.open(meeting_url)
            self.meeting_url = meeting_url
            self.is_active = True
            print(f"🎥 Opening Google Meet: {meeting_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to join Google Meet: {e}")
            return False

class ZoomProvider(MeetingProvider):
    """Zoom integration"""
    
    def create_meeting(self, title: str, description: str = "", duration_minutes: int = 60) -> Dict[str, Any]:
        """Create a Zoom meeting"""
        try:
            # For MVP, use Zoom's instant meeting feature
            # In production, integrate with Zoom API
            self.meeting_id = f"zoom-demo-{uuid.uuid4().hex[:8]}"
            
            # Zoom instant meeting URL
            self.meeting_url = "https://zoom.us/start/videomeeting"
            
            meeting_info = {
                "success": True,
                "meeting_id": self.meeting_id,
                "meeting_url": self.meeting_url,
                "title": title,
                "description": description,
                "duration_minutes": duration_minutes,
                "provider": "Zoom",
                "instructions": [
                    "1. Click the meeting link to start instant Zoom meeting",
                    "2. Copy the meeting ID and share with customer", 
                    "3. Wait for customer to join",
                    "4. Start screen sharing for the demo"
                ]
            }
            
            print(f"✅ Zoom session prepared: {title}")
            return meeting_info
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Zoom meeting: {str(e)}"
            }
    
    def join_meeting(self, meeting_url: str) -> bool:
        """Join Zoom meeting"""
        try:
            webbrowser.open(meeting_url)
            self.meeting_url = meeting_url
            self.is_active = True
            print(f"🎥 Opening Zoom: {meeting_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to join Zoom: {e}")
            return False

class GenericMeetProvider(MeetingProvider):
    """Generic meeting provider for any video conferencing platform"""
    
    def create_meeting(self, title: str, description: str = "", duration_minutes: int = 60) -> Dict[str, Any]:
        """Create a generic meeting session"""
        try:
            self.meeting_id = f"generic-demo-{uuid.uuid4().hex[:8]}"
            
            # List of popular meeting platforms
            platforms = [
                {"name": "Google Meet", "url": "https://meet.google.com/new"},
                {"name": "Zoom", "url": "https://zoom.us/start/videomeeting"},
                {"name": "Microsoft Teams", "url": "https://teams.microsoft.com/"},
                {"name": "Webex", "url": "https://www.webex.com/start-meeting.html"},
                {"name": "Jitsi Meet", "url": "https://meet.jit.si/DemoSession" + self.meeting_id}
            ]
            
            meeting_info = {
                "success": True,
                "meeting_id": self.meeting_id,
                "title": title,
                "description": description,
                "duration_minutes": duration_minutes,
                "provider": "Multi-Platform",
                "platforms": platforms,
                "instructions": [
                    "1. Choose your preferred video conferencing platform",
                    "2. Create a new meeting using the provided links",
                    "3. Share the meeting link with your customer",
                    "4. Start screen sharing when customer joins",
                    "5. Begin your interactive demo"
                ]
            }
            
            print(f"✅ Multi-platform meeting options prepared: {title}")
            return meeting_info
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to prepare meeting options: {str(e)}"
            }

class LiveDemoMeetingManager:
    """Manages live demo meetings with video conferencing"""
    
    def __init__(self, voice_agent=None, demo_executor=None):
        self.voice_agent = voice_agent
        self.demo_executor = demo_executor
        self.providers = {
            "google_meet": GoogleMeetProvider({}),
            "zoom": ZoomProvider({}),
            "generic": GenericMeetProvider({})
        }
        self.current_session = None
        self.meeting_active = False
        self.demo_active = False
        self.participants = []
        
    def create_demo_meeting(self, provider: str, demo_config, customer_info: Dict = None) -> Dict[str, Any]:
        """Create a live demo meeting"""
        try:
            if provider not in self.providers:
                return {
                    "success": False,
                    "error": f"Unsupported provider: {provider}"
                }
            
            provider_instance = self.providers[provider]
            
            # Generate meeting details
            title = f"Live Demo: {demo_config.product_name if demo_config else 'Interactive Product Demo'}"
            description = f"Interactive product demonstration with Q&A session"
            
            if demo_config:
                description += f"\n\nProduct: {demo_config.product_name}\nDescription: {demo_config.description}"
            
            if customer_info:
                description += f"\n\nCustomer: {customer_info.get('name', 'Guest')}"
                if customer_info.get('email'):
                    description += f"\nEmail: {customer_info['email']}"
            
            # Create the meeting
            meeting_result = provider_instance.create_meeting(title, description)
            
            if meeting_result.get("success"):
                # Store session information
                self.current_session = {
                    "session_id": f"live-demo-{uuid.uuid4().hex[:8]}",
                    "created_at": datetime.now().isoformat(),
                    "provider": provider,
                    "meeting_info": meeting_result,
                    "demo_config": demo_config,
                    "customer_info": customer_info,
                    "status": "created"
                }
                
                # Prepare voice announcement
                if self.voice_agent and demo_config:
                    announcement = f"Live demo meeting created for {demo_config.product_name}! The meeting link has been generated and is ready to share with your customer."
                    self.voice_agent.speak_response(announcement)
                
                print(f"🎬 Live demo session created: {self.current_session['session_id']}")
                
                return {
                    "success": True,
                    "session": self.current_session,
                    "message": "Live demo meeting created successfully!"
                }
            else:
                return meeting_result
                
        except Exception as e:
            error_msg = f"Failed to create demo meeting: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def start_live_demo(self, join_meeting: bool = True) -> Dict[str, Any]:
        """Start the live demo session"""
        try:
            if not self.current_session:
                return {
                    "success": False,
                    "error": "No active meeting session"
                }
            
            session = self.current_session
            meeting_info = session["meeting_info"]
            demo_config = session["demo_config"]
            
            # Join the meeting if requested
            if join_meeting and meeting_info.get("meeting_url"):
                provider = self.providers[session["provider"]]
                if provider.join_meeting(meeting_info["meeting_url"]):
                    self.meeting_active = True
                    session["status"] = "meeting_joined"
                    
                    # Wait a moment for meeting to load
                    time.sleep(3)
            
            # Prepare for demo
            if self.demo_executor and demo_config:
                self.demo_executor.set_demo_config(demo_config)
                
                # Welcome message for live demo
                if self.voice_agent:
                    try:
                        welcome_msg = f"Welcome to our live demonstration of {demo_config.product_name}! I'm your AI assistant and I'll be guiding you through our platform. Feel free to ask questions anytime during the demo."
                        self.voice_agent.speak_response(welcome_msg)
                    except Exception as voice_error:
                        print(f"⚠️ Voice error during welcome: {voice_error}")
                        print(f"💬 Welcome message (text only): Welcome to live demo of {demo_config.product_name}")
                
                session["status"] = "demo_ready"
                
                return {
                    "success": True,
                    "message": "Live demo session started! Ready to begin demonstration.",
                    "session": session,
                    "next_steps": [
                        "Share your screen in the video call",
                        "Start the interactive demo",
                        "Engage with customer questions in real-time"
                    ]
                }
            else:
                return {
                    "success": True,
                    "message": "Meeting joined successfully! Manual demo control enabled.",
                    "session": session
                }
                
        except Exception as e:
            error_msg = f"Failed to start live demo: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def run_live_demo(self) -> Dict[str, Any]:
        """Run the actual demo in live meeting context"""
        try:
            if not self.current_session:
                return {
                    "success": False,
                    "error": "No active session"
                }
            
            session = self.current_session
            demo_config = session.get("demo_config")
            
            # If no demo config in session, use default GIKI Transport
            if not demo_config:
                from demo_config import demo_config_manager
                demo_config = demo_config_manager.get_config("giki_transport")
                session["demo_config"] = demo_config
                print("🔄 Using default GIKI Transport demo configuration")
            
            if not demo_config:
                return {
                    "success": False,
                    "error": "No demo configuration available"
                }
            
            # Ensure demo executor is available
            if not self.demo_executor:
                from dynamic_demo_executor import DynamicDemoExecutor
                self.demo_executor = DynamicDemoExecutor(self.voice_agent)
                print("🔄 Created new demo executor")
            
            # Set the demo configuration
            self.demo_executor.set_demo_config(demo_config)
            
            # Mark demo as active
            self.demo_active = True
            session["status"] = "demo_running"
            session["demo_started_at"] = datetime.now().isoformat()
            
            # Announce demo start
            if self.voice_agent:
                try:
                    start_msg = f"Starting our interactive demonstration of {demo_config.product_name}. I'll walk you through each feature and you can ask questions at any time!"
                    self.voice_agent.speak_response(start_msg)
                except Exception as voice_error:
                    print(f"⚠️ Voice error during demo start: {voice_error}")
                    print(f"💬 Demo starting for: {demo_config.product_name}")
            
            # Run the demo in a separate thread to allow for real-time interaction
            def demo_worker():
                try:
                    # Initialize browser if needed
                    if not self.demo_executor.driver:
                        self.demo_executor.initialize_browser()
                    
                    # Start screen sharing automatically
                    if SCREEN_SHARE_AVAILABLE:
                        print("🖥️ Attempting to start screen sharing...")
                        share_result = screen_share_manager.auto_detect_and_share()
                        if share_result["success"]:
                            print(f"✅ {share_result['message']}")
                            
                            # Announce successful screen sharing
                            if self.voice_agent:
                                try:
                                    share_msg = "Screen sharing has been activated! Your audience can now see your demonstration."
                                    self.voice_agent.speak_response(share_msg)
                                except Exception as voice_error:
                                    print(f"⚠️ Voice error during screen share announcement: {voice_error}")
                        else:
                            print(f"⚠️ Automatic screen sharing failed: {share_result.get('error', 'Manual sharing required')}")
                            
                            # Provide detailed instructions if auto-sharing fails
                            instructions = screen_share_manager.show_screen_share_instructions()
                            print("📋 Manual screen sharing instructions:")
                            for i, instruction in enumerate(instructions["instructions"], 1):
                                print(f"   {i}. {instruction}")
                            
                            # Announce manual instructions
                            if self.voice_agent:
                                try:
                                    manual_msg = "Please start screen sharing manually in your meeting platform. Look for the screen share button in your meeting controls and select 'Entire Screen' to share your demonstration."
                                    self.voice_agent.speak_response(manual_msg)
                                except Exception as voice_error:
                                    print(f"⚠️ Voice error during manual screen share instructions: {voice_error}")
                    else:
                        print("📋 Screen sharing dependencies not available. Please install pyautogui and psutil for automatic screen sharing.")
                        print("💡 Manual screen sharing: Look for the screen share button in your meeting platform")
                        
                        # Announce manual requirement
                        if self.voice_agent:
                            try:
                                deps_msg = "Screen sharing automation is not available. Please manually start screen sharing in your meeting platform before we begin the demonstration."
                                self.voice_agent.speak_response(deps_msg)
                            except Exception as voice_error:
                                print(f"⚠️ Voice error during dependency warning: {voice_error}")
                    
                    # Wait a moment for screen sharing to initialize
                    time.sleep(2)
                    
                    result = self.demo_executor.run_interactive_demo()
                    session["demo_result"] = result
                    session["status"] = "demo_completed" if result.get("success") else "demo_failed"
                    session["demo_completed_at"] = datetime.now().isoformat()
                    self.demo_active = False
                    
                    # Stop screen sharing when demo ends
                    if SCREEN_SHARE_AVAILABLE and screen_share_manager.is_sharing:
                        stop_result = screen_share_manager.stop_screen_share()
                        print(f"🛑 Screen sharing stopped: {stop_result.get('message', '')}")
                    
                    # Final message with error handling
                    if self.voice_agent:
                        try:
                            if result.get("success"):
                                final_msg = f"That completes our demonstration of {demo_config.product_name}! Thank you for your time. Do you have any final questions about what we've shown?"
                            else:
                                final_msg = "I apologize, but we encountered some technical difficulties during the demo. Let me answer any questions you might have about our platform."
                            self.voice_agent.speak_response(final_msg)
                        except Exception as voice_error:
                            print(f"⚠️ Voice error during final message: {voice_error}")
                    
                    print(f"🎬 Live demo completed: {session['session_id']}")
                    
                except Exception as e:
                    print(f"❌ Demo execution error: {e}")
                    session["demo_result"] = {"success": False, "error": str(e)}
                    session["status"] = "demo_failed"
                    self.demo_active = False
            
            # Start demo in background
            demo_thread = threading.Thread(target=demo_worker, daemon=True)
            demo_thread.start()
            
            return {
                "success": True,
                "message": f"Live demo of {demo_config.product_name} started! Screen sharing will begin automatically.",
                "session": session
            }
            
        except Exception as e:
            self.demo_active = False
            error_msg = f"Failed to run live demo: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def handle_live_question(self, question: str, participant_name: str = "Customer") -> Dict[str, Any]:
        """Handle questions during live demo with improved context and answers"""
        try:
            if not self.current_session:
                return {
                    "success": False,
                    "error": "No active session"
                }

            session = self.current_session
            demo_config = session.get("demo_config")

            # Log the question
            if "questions" not in session:
                session["questions"] = []

            question_entry = {
                "timestamp": datetime.now().isoformat(),
                "participant": participant_name,
                "question": question,
                "answered_by": "AI Assistant"
            }

            # Generate contextual answer with better logic
            answer = self._generate_contextual_answer(question, demo_config)
            
            question_entry["answer"] = answer
            session["questions"].append(question_entry)

            # Speak the answer with error handling - WAIT for demo to finish speaking
            if self.voice_agent:
                try:
                    # Wait if demo is currently speaking to avoid overlap
                    if hasattr(self.voice_agent, 'is_speaking') and self.voice_agent.is_speaking:
                        time.sleep(2)  # Brief pause
                    
                    response = f"Great question! {answer}"
                    self.voice_agent.speak_response(response)
                except Exception as voice_error:
                    print(f"⚠️ Voice error during Q&A: {voice_error}")
                    print(f"💬 Answer (text only): {answer}")

            print(f"❓ Live Q&A - {participant_name}: {question}")
            print(f"💬 AI Response: {answer}")

            return {
                "success": True,
                "question": question,
                "answer": answer,
                "participant": participant_name
            }

        except Exception as e:
            error_msg = f"Failed to handle live question: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def _generate_contextual_answer(self, question: str, demo_config) -> str:
        """Generate a contextual answer based on the question and demo context"""
        question_lower = question.lower()
        
        # Get product name
        product_name = demo_config.product_name if demo_config else "our platform"
        
        # Sign-in/Login questions - SPECIFIC MATCH
        if any(word in question_lower for word in ["sign in", "login", "log in", "sign up", "register", "account"]):
            return f"To sign in to {product_name}, simply click the 'Sign In' button on our homepage. You'll be taken to a secure login page where you can enter your credentials. If you don't have an account yet, click 'Register' to create one. The process is quick and straightforward - just provide your email, create a password, and you'll have immediate access to all platform features."
        
        # How to use/getting started questions
        elif any(phrase in question_lower for phrase in ["how to use", "how do i", "getting started", "first time", "begin"]):
            return f"Getting started with {product_name} is simple! After signing in, you'll land on your personalized dashboard where you can see all available features. For first-time users, I recommend starting with the booking system to see how easy it is to manage your transport needs. Everything is designed to be intuitive - just click through the menu options and explore!"
        
        # Pricing questions
        elif any(word in question_lower for word in ["price", "cost", "pricing", "expensive", "cheap", "fee", "payment"]):
            return f"Our pricing for {product_name} is very competitive and designed to provide excellent value. We offer flexible plans starting from basic packages for individual users up to enterprise solutions. Contact our sales team for detailed pricing that fits your specific needs and usage requirements."
        
        # Feature questions
        elif any(word in question_lower for word in ["feature", "functionality", "capability", "what can", "does it", "can you"]):
            return f"{product_name} offers a comprehensive set of features designed to streamline your workflow. As you can see in our demo, we provide intuitive user interfaces, powerful automation capabilities, and seamless integration options. The platform is built with scalability in mind and includes advanced analytics, real-time processing, and customizable workflows. Would you like me to demonstrate any specific feature you're interested in?"
        
        # Security questions
        elif any(word in question_lower for word in ["security", "safe", "secure", "privacy", "data protection", "encryption"]):
            return f"Security is a top priority for {product_name}. We implement industry-standard security measures including end-to-end encryption, secure data transmission, regular security audits, and compliance with major regulations like GDPR and SOC 2. Your data is protected with multi-layered security protocols, and we provide detailed security documentation for enterprise customers. Our platform also includes role-based access controls and audit trails for complete transparency."
        
        # Integration questions
        elif any(word in question_lower for word in ["integration", "api", "connect", "third party", "integrate", "sync"]):
            return f"{product_name} is designed for seamless integration with your existing tools and systems. We provide RESTful APIs, webhooks, and pre-built integrations with popular platforms like Salesforce, HubSpot, Slack, and many others. Our integration platform allows you to connect virtually any system, and we also offer custom integration support for enterprise clients. The demo you're seeing can actually be integrated into your existing workflow quite easily."
        
        # Support questions
        elif any(word in question_lower for word in ["support", "help", "assistance", "training", "onboarding"]):
            return f"We provide comprehensive support for {product_name} users. This includes 24/7 technical support, detailed documentation, video tutorials, live training sessions, and dedicated customer success managers for enterprise accounts. We also have an active community forum and regular webinars. Our onboarding process is designed to get you up and running quickly, with personalized setup assistance and training tailored to your team's needs."
        
        # Performance questions
        elif any(word in question_lower for word in ["fast", "speed", "performance", "slow", "latency", "response time"]):
            return f"{product_name} is built for high performance with sub-second response times and 99.9% uptime SLA. Our platform uses cloud-native architecture with global CDN distribution, ensuring fast performance regardless of your location. We continuously monitor performance metrics and have built-in optimization features that adapt to your usage patterns. The system scales automatically to handle peak loads without any performance degradation."
        
        # Customization questions
        elif any(word in question_lower for word in ["customize", "custom", "personalize", "configure", "settings"]):
            return f"Absolutely! {product_name} is highly customizable to fit your specific business needs. You can customize workflows, user interfaces, data fields, reporting dashboards, and notification settings. We also support custom branding, white-labeling options, and can develop custom features for enterprise clients. The platform includes a visual configuration interface, so you don't need technical expertise to make most customizations."
        
        # Comparison questions
        elif any(word in question_lower for word in ["competitor", "compare", "alternative", "versus", "better than", "different from"]):
            return f"Great question! {product_name} stands out from alternatives through our focus on user experience, comprehensive feature set, and exceptional customer support. Unlike many competitors, we provide unlimited customization options, transparent pricing, and dedicated account management. Our platform is also designed with future-proofing in mind, ensuring that your investment continues to provide value as your business grows. I'd be happy to show you specific features that differentiate us from other solutions."
        
        # Technical questions
        elif any(word in question_lower for word in ["technical", "requirements", "system", "server", "database", "infrastructure"]):
            return f"{product_name} is built on modern, cloud-native infrastructure that requires minimal technical requirements from your end. It's a web-based solution that works on any modern browser, with mobile apps available for iOS and Android. We handle all the backend infrastructure, databases, and server management, so you don't need to worry about technical maintenance. For enterprise clients, we also offer on-premise deployment options with full technical support."
        
        # Scale/Growth questions
        elif any(word in question_lower for word in ["scale", "growth", "expand", "users", "volume", "enterprise"]):
            return f"{product_name} is designed to scale with your business from startup to enterprise level. Our architecture automatically scales to handle increased users, data volume, and transaction loads. We support unlimited users on our enterprise plans and have customers processing millions of transactions daily. The platform grows with you, adding new features and capabilities as your needs evolve, without requiring migration or system changes."
        
        # Demo-specific questions
        elif any(word in question_lower for word in ["demo", "showing", "screen", "example", "sample"]):
            return f"In this live demo of {product_name}, I'm showing you our core features in action using real-world scenarios. What you're seeing represents the actual user experience - this isn't a mock-up or simulation. The interface you see is exactly what you and your team would use daily. I can demonstrate any specific workflow or feature you're curious about. Feel free to ask me to show you particular use cases that are relevant to your business needs."
        
        # General/fallback answer
        else:
            # Try to use demo executor if available for domain-specific questions
            if self.demo_executor and hasattr(self.demo_executor, 'handle_demo_question'):
                try:
                    return self.demo_executor.handle_demo_question(question)
                except Exception as demo_error:
                    print(f"⚠️ Demo executor question error: {demo_error}")
            
            # Fallback to general helpful response
            return f"That's an excellent question about {product_name}! Based on what we're demonstrating here, our platform is designed to address exactly these kinds of business challenges. Let me give you a comprehensive answer: {product_name} provides robust solutions that are user-friendly, scalable, and designed with your success in mind. We've built this platform based on years of customer feedback and industry best practices. Would you like me to demonstrate a specific aspect that relates to your question, or would you prefer to see how this would work in your particular use case?"
    
    def end_live_demo(self) -> Dict[str, Any]:
        """End the live demo session"""
        try:
            if not self.current_session:
                return {
                    "success": False,
                    "error": "No active session to end"
                }
            
            session = self.current_session
            
            # Stop demo if running
            if self.demo_active:
                self.demo_active = False
            
            # Update session status
            session["status"] = "completed"
            session["ended_at"] = datetime.now().isoformat()
            
            # Calculate session duration
            if "demo_started_at" in session:
                start_time = datetime.fromisoformat(session["demo_started_at"])
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds() / 60
                session["duration_minutes"] = round(duration, 2)
            
            # Final thank you message
            if self.voice_agent:
                demo_config = session.get("demo_config")
                if demo_config:
                    final_msg = f"Thank you for joining our live demonstration of {demo_config.product_name}! If you have any follow-up questions, please don't hesitate to reach out."
                else:
                    final_msg = "Thank you for joining our live demonstration! We hope you found it valuable."
                self.voice_agent.speak_response(final_msg)
            
            # Generate session summary
            summary = self.generate_session_summary(session)
            
            # Clear current session
            completed_session = self.current_session
            self.current_session = None
            self.meeting_active = False
            
            print(f"🎬 Live demo session ended: {completed_session['session_id']}")
            
            return {
                "success": True,
                "message": "Live demo session ended successfully",
                "session_summary": summary,
                "completed_session": completed_session
            }
            
        except Exception as e:
            error_msg = f"Failed to end live demo: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def generate_session_summary(self, session: Dict) -> Dict[str, Any]:
        """Generate a summary of the demo session"""
        try:
            demo_config = session.get("demo_config")
            questions = session.get("questions", [])
            
            summary = {
                "session_id": session["session_id"],
                "product_demo": demo_config.product_name if demo_config else "Generic Demo",
                "duration_minutes": session.get("duration_minutes", 0),
                "questions_asked": len(questions),
                "customer_engagement": "High" if len(questions) > 3 else "Medium" if len(questions) > 0 else "Low",
                "demo_completed": session.get("status") == "completed",
                "key_topics": []
            }
            
            # Extract key topics from questions
            if questions:
                topics = set()
                for q in questions:
                    question_text = q["question"].lower()
                    if any(word in question_text for word in ["price", "cost", "pricing"]):
                        topics.add("Pricing")
                    if any(word in question_text for word in ["feature", "functionality", "capability"]):
                        topics.add("Features")
                    if any(word in question_text for word in ["security", "safe", "secure"]):
                        topics.add("Security")
                    if any(word in question_text for word in ["integration", "api", "connect"]):
                        topics.add("Integration")
                    if any(word in question_text for word in ["support", "help", "assistance"]):
                        topics.add("Support")
                
                summary["key_topics"] = list(topics)
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Failed to generate session summary: {e}")
            return {"error": str(e)}
    
    def start_screen_sharing(self, platform: str = "auto") -> Dict[str, Any]:
        """Manually start screen sharing"""
        try:
            if not SCREEN_SHARE_AVAILABLE:
                return {
                    "success": False,
                    "error": "Screen sharing dependencies not available"
                }
            
            if platform == "auto":
                result = screen_share_manager.auto_detect_and_share()
            elif platform == "google_meet":
                result = screen_share_manager.start_screen_share_google_meet()
            elif platform == "zoom":
                result = screen_share_manager.start_screen_share_zoom()
            elif platform == "teams":
                result = screen_share_manager.start_screen_share_teams()
            else:
                result = screen_share_manager.show_screen_share_instructions(platform)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start screen sharing: {str(e)}"
            }
    
    def stop_screen_sharing(self) -> Dict[str, Any]:
        """Stop screen sharing"""
        try:
            if not SCREEN_SHARE_AVAILABLE:
                return {
                    "success": False,
                    "error": "Screen sharing dependencies not available"
                }
            
            result = screen_share_manager.stop_screen_share()
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stop screen sharing: {str(e)}"
            }
    
    def get_screen_share_status(self) -> Dict[str, Any]:
        """Get screen sharing status"""
        if not SCREEN_SHARE_AVAILABLE:
            return {
                "available": False,
                "message": "Screen sharing dependencies not installed"
            }
        
        status = screen_share_manager.get_sharing_status()
        status["available"] = True
        return status

    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        if not self.current_session:
            return {
                "active": False,
                "message": "No active session"
            }
        
        return {
            "active": True,
            "session": self.current_session,
            "meeting_active": self.meeting_active,
            "demo_active": self.demo_active,
            "status": self.current_session.get("status", "unknown")
        }

# Global live demo manager
live_demo_manager = None

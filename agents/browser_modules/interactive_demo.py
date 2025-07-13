"""
Interactive Demo Module - Handles voice-narrated demos with real-time Q&A
"""

import time
import threading
from typing import Dict, Any, Optional

class InteractiveDemo:
    """Interactive demo with real-time Q&A capabilities"""
    
    def __init__(self, browser_core, giki_actions):
        self.browser_core = browser_core
        self.giki_actions = giki_actions
        self.demo_paused = False
        self.question_mode = False
        self.current_step = 0
        self.demo_steps = []
        self.voice_agent = None
        self.intent_agent = None
        self.demo_thread = None
        self.qa_active = False
        self.demo_active = False  # Add missing attribute
    
    def set_agents(self, voice_agent, intent_agent):
        """Set the voice and intent agents"""
        self.voice_agent = voice_agent
        self.intent_agent = intent_agent
    
    def run_interactive_demo(self) -> Dict[str, Any]:
        """Run the interactive demo with real-time Q&A capability"""
        try:
            self.demo_active = True  # Set demo as active
            print("🎬 Starting Interactive GIKI Transport Demo...")
            print("💡 Press microphone button anytime during demo to ask questions!")
            
            # Initialize browser first
            if not self.browser_core.is_initialized:
                print("🔄 Initializing browser for demo...")
                # Try voice with error handling
                try:
                    if self.voice_agent:
                        self.voice_agent.speak_response("Welcome! I'm your personal GIKI Transport assistant. I'll show you our amazing features, and you can ask me questions anytime during the demo!")
                except Exception as e:
                    print(f"⚠️ Voice initialization failed: {e}")
                    print("🔄 Demo will continue without voice...")
                self.browser_core.initialize_browser(headless=False)
                time.sleep(0.2)  # Quick startup pause
            
            # Define demo steps
            self.demo_steps = [
                {
                    "name": "Homepage",
                    "action": lambda: self.browser_core.navigate_to_url("https://giktransport.giki.edu.pk:8038/"),
                    "narration": "Let's start with our beautiful homepage. This is where users first experience GIKI Transport."
                },
                {
                    "name": "Sign-in Page",
                    "action": lambda: self.browser_core.navigate_to_url("https://giktransport.giki.edu.pk:8038/auth/signin/"),
                    "narration": "Here's our secure sign-in page. Users can safely access their accounts."
                },
                {
                    "name": "Automatic Login",
                    "action": lambda: self.giki_actions.handle_signin(),
                    "narration": "Watch as I automatically log in to show you the full experience."
                },
                {
                    "name": "Dashboard",
                    "action": lambda: self.browser_core.navigate_to_url("https://giktransport.giki.edu.pk:8038/"),
                    "narration": "Welcome to the main dashboard! This is your central hub for all transport services."
                },
                {
                    "name": "Profile Management",
                    "action": lambda: self.giki_actions.check_profile(),
                    "narration": "Here users can manage their personal information and account settings."
                },
                {
                    "name": "Ticket Management",
                    "action": lambda: self.giki_actions.check_tickets(),
                    "narration": "This is where users can view and manage all their transport tickets."
                },
                {
                    "name": "Booking System",
                    "action": lambda: self.giki_actions.click_book_ticket_button(),
                    "narration": "And here's our powerful booking system where users can reserve tickets instantly."
                },
                {
                    "name": "Demo Complete",
                    "action": lambda: self.browser_core.navigate_to_url("https://giktransport.giki.edu.pk:8038/"),
                    "narration": "That's our complete tour! GIKI Transport provides seamless voice-controlled navigation, secure authentication, and instant booking capabilities."
                }
            ]
            
            # Start demo execution
            return self.execute_demo_steps()
            
        except Exception as e:
            error_msg = f"Interactive demo failed: {str(e)}"
            print(f"❌ Demo error: {error_msg}")
            return {
                "success": False,
                "message": f"Demo failed: {error_msg}",
                "error": str(e)
            }
    
    def execute_demo_steps(self) -> Dict[str, Any]:
        """Execute demo steps with Q&A support"""
        completed_steps = []
        
        for i, step in enumerate(self.demo_steps):
            self.current_step = i
            
            try:
                print(f"\n📝 Step {i+1}: {step['name']}")
                
                # Voice narration with error handling
                try:
                    if self.voice_agent:
                        self.voice_agent.speak_response(f"Step {i+1}: {step['narration']}")
                        time.sleep(0.3)  # Quick pause after narration
                except Exception as e:
                    print(f"⚠️ Voice narration failed: {e}")
                    print("🔄 Demo continues without voice...")
                
                # Execute the action
                print(f"🔄 Executing: {step['name']}...")
                result = step["action"]()
                print(f"📊 Result: {result}")
                
                if result and result.get("success"):
                    completed_steps.append(f"✅ {step['name']}")
                    print(f"✅ {step['name']} completed successfully")
                else:
                    completed_steps.append(f"⚠️ {step['name']} - had issues")
                    print(f"⚠️ {step['name']} - had issues but continuing")
                
                # Simple wait between steps
                print(f"⏰ Moving to next step...")
                self.wait_with_qa_option(2.0)  # Simple 2 second wait
                
            except Exception as e:
                completed_steps.append(f"❌ {step['name']} - failed")
                print(f"❌ {step['name']} failed: {str(e)}")
                continue
        
        # Final summary with Q&A invitation
        self.demo_active = False  # Mark demo as completed
        if self.voice_agent:
            self.voice_agent.speak_response("Demo completed! Thanks for watching. Do you have any final questions about GIKI Transport?")
            
            # Give user time to ask final questions
            print("\n🤔 Waiting for final questions... (10 seconds)")
            final_qa_time = 10  # seconds for final Q&A
            start_time = time.time()
            
            while time.time() - start_time < final_qa_time:
                if self.qa_active:
                    # Q&A session is active, wait for it to complete
                    while self.qa_active:
                        time.sleep(0.1)
                    # Reset the timer after Q&A
                    start_time = time.time()
                time.sleep(0.1)
            
            self.voice_agent.speak_response("Thank you for your time! GIKI Transport is here to serve all your transportation needs.")
        
        summary = "🎬 Interactive GIKI Transport Demo Completed!\n\n"
        summary += "Steps completed:\n"
        for step in completed_steps:
            summary += f"• {step}\n"
        summary += "\n🌟 Interactive demo finished with Q&A support!"
        
        return {
            "success": True,
            "message": summary,
            "action": "interactive_demo",
            "steps_completed": len(completed_steps)
        }
    
    def wait_with_qa_option(self, duration: float):
        """Simple wait that can be interrupted for Q&A"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if self.qa_active:
                # Wait for Q&A to finish, then continue
                while self.qa_active:
                    time.sleep(0.1)
                return  # Continue demo after Q&A
            time.sleep(0.1)
    
    def handle_demo_question(self, question: str) -> Dict[str, Any]:
        """Handle a question during the demo - simple and direct"""
        try:
            print(f"\n🤔 Demo Question: {question}")
            
            # Set Q&A active flag (but don't interrupt current speech)
            self.qa_active = True
            
            # Generate answer using LLM
            try:
                if self.intent_agent:
                    response = self.intent_agent.groq_client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a professional sales agent demonstrating GIKI Transport. Answer questions briefly and enthusiastically like a human sales agent would during a product demo. Be helpful and engaging. Keep responses short."
                            },
                            {
                                "role": "user", 
                                "content": f"During GIKI Transport demo, customer asks: {question}"
                            }
                        ],
                        max_tokens=40,  # Shorter for faster responses
                        temperature=0.4
                    )
                    answer = response.choices[0].message.content.strip()
                else:
                    answer = "That's a great question! GIKI Transport is designed to be user-friendly and efficient."
            except Exception as llm_error:
                print(f"⚠️ LLM error: {llm_error}")
                # Sales-style fallback answers
                if 'book' in question.lower():
                    answer = "Excellent question! Our booking system is incredibly fast - you can reserve tickets in just seconds with voice commands!"
                elif 'voice' in question.lower():
                    answer = "Great point! Our voice control makes everything hands-free and super convenient for busy users."
                elif 'profile' in question.lower():
                    answer = "Smart question! The profile section lets users manage everything from one place - it's really user-friendly."
                elif 'ticket' in question.lower():
                    answer = "Perfect question! Users can view, manage, and track all their tickets in one convenient location."
                elif 'price' in question.lower() or 'cost' in question.lower():
                    answer = "That's a popular question! GIKI Transport offers competitive pricing with great value for our comprehensive features."
                else:
                    answer = "That's an excellent question! GIKI Transport is built to solve exactly those kinds of user needs with our intuitive design."
            
            print(f"💡 Demo Answer: {answer}")
            
            # Speak the answer
            if self.voice_agent:
                self.voice_agent.speak_response(answer)
                
                # Simple transition message based on demo state
                if self.demo_active and self.current_step < len(self.demo_steps) - 1:
                    self.voice_agent.speak_response("Let me continue the demo.")
                else:
                    self.voice_agent.speak_response("Any other questions?")
            
            # Clear Q&A flag
            self.qa_active = False
            
            return {
                "success": True,
                "question": question,
                "answer": answer,
                "demo_step": self.current_step,
                "timestamp": time.strftime("%H:%M:%S")
            }
            
        except Exception as e:
            self.qa_active = False
            print(f"❌ Demo Q&A error: {str(e)}")
            return {
                "success": False,
                "error": f"Demo Q&A failed: {str(e)}"
            }
    
    def pause_demo(self):
        """Pause the demo for Q&A"""
        self.demo_paused = True
        self.qa_active = True
    
    def resume_demo(self):
        """Resume the demo after Q&A"""
        self.demo_paused = False
        self.qa_active = False
    
    def stop_demo(self):
        """Stop the demo execution"""
        self.demo_active = False
        self.demo_paused = False
        self.current_step = 0
        self.qa_mode = False
        print("Demo stopped by user request")

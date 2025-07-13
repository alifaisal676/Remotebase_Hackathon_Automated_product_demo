"""
GIKI Transport Web Interface
Modern web-based voice interface with good UI
"""

import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import json
import time
from datetime import datetime
from demo_config import demo_config_manager, ProductConfig
from dynamic_demo_executor import DynamicDemoExecutor
from live_meeting_integration import LiveDemoMeetingManager

# Configure logging to reduce Flask output
logging.getLogger('werkzeug').setLevel(logging.WARNING)

from agents.voice_agent import VoiceAgent
from agents.intent_parsing_agent import IntentParsingAgent
from agents.browser_automation_agent_new import BrowserAutomationAgent

app = Flask(__name__)

# Global agents
voice_agent = None
intent_agent = None
browser_agent = None
dynamic_demo = None
live_demo_manager = None
current_demo_config = None

# System state
system_state = {
    "initialized": False,
    "listening": False,
    "last_command": "",
    "last_response": "",
    "error": None
}

# Global voice recording state
voice_recording_state = {
    "is_recording": False,
    "transcription": "",
    "error": None
}

# Global demo state for interactive Q&A
demo_state = {
    "is_running": False,
    "qa_enabled": False,
    "demo_agent": None
}

def initialize_agents():
    """Initialize all agents"""
    global voice_agent, intent_agent, browser_agent, dynamic_demo, system_state
    
    try:
        print("🔄 Initializing agents...")
        
        voice_agent = VoiceAgent()
        intent_agent = IntentParsingAgent()
        browser_agent = BrowserAutomationAgent()
        
        # Set the agents for the browser agent
        browser_agent.set_agents(voice_agent, intent_agent)
        
        # Initialize Dynamic Demo Executor
        dynamic_demo = DynamicDemoExecutor(voice_agent)
        
        # Initialize Live Demo Meeting Manager
        global live_demo_manager
        live_demo_manager = LiveDemoMeetingManager(voice_agent, dynamic_demo)
        
        system_state["initialized"] = True
        system_state["error"] = None
        
        print("✅ All agents initialized successfully!")
        
    except Exception as e:
        system_state["error"] = str(e)
        print(f"❌ Error initializing agents: {e}")

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify(system_state)

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a command"""
    global system_state
    
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({"success": False, "error": "No command provided"})
        
        if not system_state["initialized"]:
            return jsonify({"success": False, "error": "System not initialized"})
        
        # Update state
        system_state["last_command"] = command
        
        # Handle explicit navigation commands FIRST (before intent parsing)
        if 'go to signin' in command.lower() or 'go to login' in command.lower() or 'navigate to signin' in command.lower():
            result = browser_agent.navigate_to_url("https://giktransport.giki.edu.pk:8038/auth/signin/")
        
        elif 'go to signup' in command.lower() or 'navigate to signup' in command.lower():
            result = browser_agent.navigate_to_url("https://giktransport.giki.edu.pk:8038/auth/signup/")
        
        elif command.lower() == 'signin' or command.lower() == 'sign in':
            result = browser_agent.handle_signin()
        
        elif command.lower() == 'signup' or command.lower() == 'sign up':
            result = browser_agent.handle_signup()
        
        elif command.lower() == 'show demo' or command.lower() == 'demo':
            # Use the interactive demo instead of automated demo
            result = browser_agent.run_interactive_demo()
        
        else:
            # Parse intent for other commands
            intent_data = intent_agent.parse_command(command)
            intent_type = intent_data.get('intent', 'unknown')
            
            # Execute command based on intent
            if intent_type == 'navigate':
                # Use the URL from the parsed intent or extract it
                target_url = intent_data.get('target_url') or intent_agent.extract_url_from_command(command)
                if target_url:
                    result = browser_agent.navigate_to_url(target_url)
                else:
                    result = {"success": False, "message": "Could not determine where to navigate"}
            
            elif intent_type == 'question' or 'what' in command.lower() or 'how' in command.lower():
                answer = intent_agent.answer_question(command)
                result = {"success": True, "message": answer}
            
            elif 'book' in command.lower():
                if 'ticket' in command.lower():
                    result = browser_agent.click_book_ticket_button()
                else:
                    result = browser_agent.handle_booking_flow()
            
            elif 'ticket' in command.lower():
                result = browser_agent.check_tickets()
            
            elif 'profile' in command.lower():
                result = browser_agent.check_profile()
            
            else:
                # Default to navigation if we can find a URL
                url = intent_agent.extract_url_from_command(command)
                if url:
                    result = browser_agent.navigate_to_url(url)
                else:
                    result = {"success": False, "message": "I didn't understand that command. Try asking about GIKI Transport or use navigation commands like 'go to my profile' or 'book now'."}
        
        # Get response message
        response_message = result.get('message', 'Command executed')
        system_state["last_response"] = response_message
        
        return jsonify({
            "success": result.get('success', False),
            "message": response_message,
            "intent": intent_type,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        system_state["error"] = error_msg
        return jsonify({"success": False, "error": error_msg})

@app.route('/api/voice/start', methods=['POST'])
def start_voice():
    """Start voice listening"""
    global system_state
    
    try:
        if not system_state["initialized"]:
            return jsonify({"success": False, "error": "System not initialized"})
        
        if system_state["listening"]:
            return jsonify({"success": False, "error": "Already listening"})
        
        # Start voice recognition in background
        def voice_worker():
            try:
                system_state["listening"] = True
                command = voice_agent.get_voice_input()
                system_state["listening"] = False
                
                if command and command.strip():
                    system_state["last_command"] = command
                    
                    # Use same command handling as execute_command
                    # Handle explicit navigation commands FIRST
                    if 'go to signin' in command.lower() or 'go to login' in command.lower() or 'navigate to signin' in command.lower():
                        result = browser_agent.navigate_to_url("https://giktransport.giki.edu.pk:8038/auth/signin/")
                    
                    elif 'go to signup' in command.lower() or 'navigate to signup' in command.lower():
                        result = browser_agent.navigate_to_url("https://giktransport.giki.edu.pk:8038/auth/signup/")
                    
                    elif command.lower() == 'signin' or command.lower() == 'sign in':
                        result = browser_agent.handle_signin()
                    
                    elif command.lower() == 'signup' or command.lower() == 'sign up':
                        result = browser_agent.handle_signup()
                    
                    else:
                        # Parse intent for other commands
                        intent_data = intent_agent.parse_command(command)
                        intent_type = intent_data.get('intent', 'unknown')
                        
                        # Execute command based on intent
                        if intent_type == 'navigate':
                            target_url = intent_data.get('target_url') or intent_agent.extract_url_from_command(command)
                            if target_url:
                                result = browser_agent.navigate_to_url(target_url)
                            else:
                                result = {"success": False, "message": "Could not determine where to navigate"}
                        
                        elif intent_type == 'question' or 'what' in command.lower() or 'how' in command.lower():
                            answer = intent_agent.answer_question(command)
                            result = {"success": True, "message": answer}
                        
                        elif 'book' in command.lower():
                            if 'ticket' in command.lower():
                                result = browser_agent.click_book_ticket_button()
                            else:
                                result = browser_agent.handle_booking_flow()
                        
                        elif 'ticket' in command.lower():
                            result = browser_agent.check_tickets()
                        
                        elif 'profile' in command.lower():
                            result = browser_agent.check_profile()
                        
                        elif 'demo' in command.lower() or 'show demo' in command.lower():
                            result = browser_agent.run_automated_demo()
                        
                        else:
                            url = intent_agent.extract_url_from_command(command)
                            if url:
                                result = browser_agent.navigate_to_url(url)
                            else:
                                result = {"success": False, "message": "I didn't understand that command."}
                    
                    response_message = result.get('message', 'Command executed')
                    system_state["last_response"] = response_message
                    
                    # Speak response simply
                    if result.get('success'):
                        try:
                            voice_agent.speak_response(response_message)
                        except Exception as e:
                            print(f"TTS error: {e}")
                
            except Exception as e:
                system_state["listening"] = False
                system_state["error"] = str(e)
                print(f"Voice recognition error: {e}")
        
        threading.Thread(target=voice_worker, daemon=True).start()
        
        return jsonify({"success": True, "message": "Voice recognition started"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/voice/stop', methods=['POST'])
def stop_voice():
    """Stop voice listening"""
    global system_state
    
    system_state["listening"] = False
    
    # Stop any playing audio
    try:
        if voice_agent and hasattr(voice_agent, 'stop_audio'):
            voice_agent.stop_audio()
    except Exception as e:
        print(f"Error stopping audio: {e}")
    
    return jsonify({"success": True, "message": "Voice recognition stopped"})

@app.route('/qa_test_page')
def qa_test_page():
    """Serve the Q&A testing page"""
    return render_template('qa_test.html')

@app.route('/qa_test', methods=['POST'])
def qa_test():
    """Handle Q&A testing requests"""
    global voice_agent, intent_agent
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        volume = int(data.get('volume', 80))
        
        if not question:
            return jsonify({
                "success": False,
                "error": "No question provided"
            })
        
        print(f"📝 Q&A Test - Question: {question}")
        
        # Initialize agents if needed
        if not intent_agent:
            intent_agent = IntentParsingAgent()
        if not voice_agent:
            voice_agent = VoiceAgent()
            
        # Set volume (0-100 to 0.0-1.0)
        voice_agent.volume = volume / 100.0
        
        # Generate short answer using LLM
        try:
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
                max_tokens=40,  # Very short answers
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
            elif 'ticket' in question.lower():
                answer = "View and manage your transport tickets."
            elif 'dashboard' in question.lower():
                answer = "Central hub for all transport services."
            else:
                answer = "GIKI Transport offers comprehensive transport services."
        
        print(f"💡 Generated answer: {answer}")
        
        # Speak the answer
        try:
            print("🔊 Speaking answer...")
            voice_agent.speak_response(answer)
            print("✅ Answer spoken")
            
        except Exception as tts_error:
            print(f"⚠️ TTS error: {tts_error}")
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        print(f"❌ Q&A test error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Q&A test failed: {str(e)}"
        })

@app.route('/start_voice_recording', methods=['POST'])
def start_voice_recording():
    """Start voice recording for Q&A"""
    global voice_recording_state, voice_agent
    
    try:
        if not voice_agent:
            voice_agent = VoiceAgent()
            
        voice_recording_state["is_recording"] = True
        voice_recording_state["transcription"] = ""
        voice_recording_state["error"] = None
        
        print("🎙️ Started voice recording for Q&A")
        
        return jsonify({
            "success": True,
            "message": "Voice recording started"
        })
        
    except Exception as e:
        print(f"❌ Voice recording start error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to start recording: {str(e)}"
        })

@app.route('/stop_voice_recording', methods=['POST'])
def stop_voice_recording():
    """Stop voice recording and get transcription"""
    global voice_recording_state, voice_agent
    
    try:
        if not voice_recording_state["is_recording"]:
            return jsonify({
                "success": False,
                "error": "Not currently recording"
            })
        
        voice_recording_state["is_recording"] = False
        print("🎙️ Stopping voice recording and transcribing...")
        
        # Get transcription
        if voice_agent:
            try:
                transcription = voice_agent.listen_and_transcribe()
                voice_recording_state["transcription"] = transcription
                
                print(f"📝 Transcribed: {transcription}")
                
                return jsonify({
                    "success": True,
                    "transcription": transcription
                })
                
            except Exception as transcription_error:
                print(f"⚠️ Transcription error: {transcription_error}")
                return jsonify({
                    "success": False,
                    "error": f"Transcription failed: {str(transcription_error)}"
                })
        else:
            return jsonify({
                "success": False,
                "error": "Voice agent not available"
            })
        
    except Exception as e:
        print(f"❌ Voice recording stop error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to stop recording: {str(e)}"
        })

@app.route('/play_answer', methods=['POST'])
def play_answer():
    """Play an answer using TTS"""
    global voice_agent
    
    try:
        data = request.get_json()
        answer = data.get('answer', '').strip()
        volume = int(data.get('volume', 80))
        
        if not answer:
            return jsonify({
                "success": False,
                "error": "No answer provided"
            })
        
        if not voice_agent:
            voice_agent = VoiceAgent()
            
        # Set volume
        voice_agent.volume = volume / 100.0
        
        print(f"🔊 Playing answer: {answer}")
        
        # Simple TTS playback
        voice_agent.speak_response(answer)
        print("✅ Playback completed")
        
        return jsonify({
            "success": True,
            "message": "Answer played successfully"
        })
        
    except Exception as e:
        print(f"❌ Answer playback error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Playback failed: {str(e)}"
        })

@app.route('/api/demo/start', methods=['POST'])
def start_interactive_demo():
    """Start the interactive demo with Q&A support"""
    global demo_state, browser_agent, voice_agent, intent_agent
    
    try:
        if demo_state["is_running"]:
            return jsonify({
                "success": False,
                "error": "Demo is already running"
            })
        
        print("🎬 Starting interactive demo with Q&A support...")
        
        # Initialize agents if needed
        if not browser_agent:
            browser_agent = BrowserAutomationAgent()
        if not voice_agent:
            voice_agent = VoiceAgent()
        if not intent_agent:
            intent_agent = IntentParsingAgent()
        
        # Set agents for interactive demo
        browser_agent.set_agents(voice_agent, intent_agent)
        
        # Start demo in background
        def demo_worker():
            try:
                print("🎬 Demo worker starting...")
                demo_state["is_running"] = True
                demo_state["qa_enabled"] = True
                demo_state["demo_agent"] = browser_agent
                
                print("🎬 Calling run_interactive_demo...")
                result = browser_agent.run_interactive_demo()
                print(f"🎬 Demo result: {result}")
                
                demo_state["is_running"] = False
                demo_state["qa_enabled"] = False
                demo_state["demo_agent"] = None
                
                print("✅ Interactive demo completed")
                
            except Exception as e:
                demo_state["is_running"] = False
                demo_state["qa_enabled"] = False
                demo_state["demo_agent"] = None
                print(f"❌ Demo error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("🎬 Starting demo worker thread...")
        threading.Thread(target=demo_worker, daemon=True).start()
        
        return jsonify({
            "success": True,
            "message": "Interactive demo started! You can ask questions anytime during the demo."
        })
        
    except Exception as e:
        print(f"❌ Demo start error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to start demo: {str(e)}"
        })

@app.route('/api/demo/question', methods=['POST'])
def ask_demo_question():
    """Ask a question during the demo"""
    global demo_state, voice_agent
    
    try:
        if not demo_state["is_running"] or not demo_state["qa_enabled"]:
            return jsonify({
                "success": False,
                "error": "Demo is not running or Q&A is not enabled"
            })
        
        data = request.get_json()
        question = data.get('question', '').strip()
        use_voice = data.get('use_voice', False)
        volume = int(data.get('volume', 80))
        
        if not question and not use_voice:
            return jsonify({
                "success": False,
                "error": "No question provided"
            })
        
        # Get question via voice if requested
        if use_voice:
            try:
                if voice_agent:
                    voice_agent.volume = volume / 100.0
                    question = voice_agent.listen_and_transcribe()
                    if not question:
                        return jsonify({
                            "success": False,
                            "error": "Could not understand the question"
                        })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Voice agent not available"
                    })
            except Exception as voice_error:
                return jsonify({
                    "success": False,
                    "error": f"Voice recognition failed: {str(voice_error)}"
                })
        
        print(f"🤔 Demo question received: {question}")
        
        # Handle the question during demo - use the interactive demo directly
        if browser_agent and hasattr(browser_agent, 'interactive_demo') and browser_agent.interactive_demo:
            result = browser_agent.interactive_demo.handle_demo_question(question)
            
            if result["success"]:
                return jsonify({
                    "success": True,
                    "question": question,
                    "answer": result["answer"],
                    "demo_step": result.get("demo_step", 0),
                    "timestamp": result.get("timestamp", "")
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "Failed to answer question")
                })
        else:
            # Fallback Q&A if demo agent not available
            try:
                # Generate a quick answer
                if 'book' in question.lower():
                    answer = "Great question! Our booking system is incredibly fast and user-friendly!"
                elif 'price' in question.lower() or 'cost' in question.lower():
                    answer = "Excellent question! We offer competitive pricing with great value."
                elif 'voice' in question.lower():
                    answer = "Our voice features make everything hands-free and convenient!"
                else:
                    answer = "That's a great question! GIKI Transport is designed to be user-friendly and efficient."
                
                # Speak the answer if voice is available
                if voice_agent:
                    voice_agent.speak_response(answer)
                
                return jsonify({
                    "success": True,
                    "question": question,
                    "answer": answer,
                    "demo_step": 0,
                    "timestamp": time.strftime("%H:%M:%S")
                })
            except Exception as fallback_error:
                return jsonify({
                    "success": False,
                    "error": f"Fallback Q&A failed: {str(fallback_error)}"
                })
        
    except Exception as e:
        print(f"❌ Demo question error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to process question: {str(e)}"
        })

@app.route('/api/demo/status')
def get_demo_status():
    """Get current demo status"""
    global browser_agent
    
    # Check if interactive demo is actually running
    is_demo_active = False
    qa_enabled = False
    
    if browser_agent and hasattr(browser_agent, 'interactive_demo') and browser_agent.interactive_demo:
        is_demo_active = browser_agent.interactive_demo.demo_active
        qa_enabled = is_demo_active  # Q&A is enabled when demo is active
    
    return jsonify({
        "active": is_demo_active,
        "is_running": is_demo_active,  # For backward compatibility
        "qa_enabled": qa_enabled,
        "has_demo_agent": browser_agent is not None
    })

@app.route('/api/demo/stop', methods=['POST'])
def stop_demo():
    """Stop the interactive demo"""
    global demo_state
    try:
        if demo_state.get('active', False):
            demo_state['active'] = False
            demo_state['paused'] = False
            demo_state['current_step'] = 0
            
            # Stop the demo in the browser agent
            if hasattr(browser_agent, 'interactive_demo') and browser_agent.interactive_demo:
                browser_agent.interactive_demo.stop_demo()
            
            return jsonify({
                'success': True,
                'message': 'Demo stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No demo is currently running'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error stopping demo: {str(e)}'
        })

# Demo Configuration API Routes
@app.route('/config')
def demo_config():
    """Demo configuration interface for product owners"""
    return render_template('config.html')

@app.route('/api/demos/list', methods=['GET'])
def list_demos():
    """Get list of available demo configurations"""
    try:
        demos = demo_config_manager.list_configs()
        return jsonify({
            'success': True,
            'demos': demos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/demos/create', methods=['POST'])
def create_demo():
    """Create new demo configuration"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['product_name', 'base_url', 'description', 'steps']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create configuration
        config = demo_config_manager.create_config_from_input(data)
        config_id = demo_config_manager.add_custom_config(config)
        
        # Optionally save to file
        import os
        config_dir = 'demo_configs'
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        filename = f"{config_dir}/{config_id}.json"
        demo_config_manager.save_config_to_file(config, filename)
        
        return jsonify({
            'success': True,
            'config_id': config_id,
            'message': 'Demo configuration created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/demos/get/<config_id>', methods=['GET'])
def get_demo_config(config_id):
    """Get specific demo configuration"""
    try:
        config = demo_config_manager.get_config(config_id)
        if not config:
            return jsonify({
                'success': False,
                'message': 'Demo configuration not found'
            }), 404
        
        # Convert config to dictionary for JSON response
        config_dict = {
            'product_name': config.product_name,
            'base_url': config.base_url,
            'description': config.description,
            'welcome_message': config.welcome_message,
            'closing_message': config.closing_message,
            'login_credentials': config.login_credentials,
            'demo_steps': [
                {
                    'name': step.name,
                    'description': step.description,
                    'url': step.url,
                    'action_type': step.action_type,
                    'wait_time': step.wait_time,
                    'voice_script': step.voice_script
                }
                for step in config.demo_steps
            ]
        }
        
        return jsonify({
            'success': True,
            'config': config_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/demos/run', methods=['POST'])
def run_custom_demo():
    """Run a specific demo configuration"""
    try:
        data = request.json
        config_id = data.get('demo_id')
        
        if not config_id:
            return jsonify({
                'success': False,
                'message': 'Demo ID is required'
            }), 400
        
        config = demo_config_manager.get_config(config_id)
        if not config:
            return jsonify({
                'success': False,
                'message': 'Demo configuration not found'
            }), 404
        
        # Update the dynamic demo with new configuration
        global dynamic_demo, current_demo_config
        if dynamic_demo:
            dynamic_demo.set_demo_config(config)
        
        # Store current demo config globally
        current_demo_config = config
        
        return jsonify({
            'success': True,
            'message': f'Demo configuration loaded: {config.product_name}',
            'redirect': '/'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Live Meeting API
@app.route('/live-demo')
def live_demo_page():
    return render_template('live_demo.html')

@app.route('/api/live-meeting/create', methods=['POST'])
def create_live_meeting():
    try:
        if not live_demo_manager:
            return jsonify({'success': False, 'error': 'Live meeting system not initialized'}), 500
        data = request.get_json()
        provider = data.get('provider', 'google_meet')
        demo_config_id = data.get('demo_config_id')
        customer_info = data.get('customer_info', {})
        demo_config = demo_config_manager.get_config(demo_config_id) if demo_config_id else None
        result = live_demo_manager.create_demo_meeting(provider, demo_config, customer_info)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/live-meeting/start', methods=['POST'])
def start_live_meeting():
    try:
        if not live_demo_manager:
            return jsonify({'success': False, 'error': 'Live meeting system not initialized'}), 500
        data = request.get_json()
        result = live_demo_manager.start_live_demo(data.get('join_meeting', True))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/live-meeting/run-demo', methods=['POST'])
def run_live_demo():
    try:
        if not live_demo_manager:
            return jsonify({'success': False, 'error': 'Live meeting system not initialized'}), 500
        result = live_demo_manager.run_live_demo()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/live-meeting/question', methods=['POST'])
def handle_live_question():
    try:
        if not live_demo_manager:
            return jsonify({'success': False, 'error': 'Live meeting system not initialized'}), 500
        data = request.get_json()
        result = live_demo_manager.handle_live_question(data.get('question', ''), data.get('participant', 'Customer'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/live-meeting/end', methods=['POST'])
def end_live_meeting():
    try:
        if not live_demo_manager:
            return jsonify({'success': False, 'error': 'Live meeting system not initialized'}), 500
        result = live_demo_manager.end_live_demo()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/live-meeting/status')
def get_live_meeting_status():
    try:
        if not live_demo_manager:
            return jsonify({'active': False, 'error': 'Live meeting system not initialized'})
        status = live_demo_manager.get_session_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'active': False, 'error': str(e)}), 500

# Screen Sharing API endpoints
@app.route('/api/screen-share/start', methods=['POST'])
def start_screen_share():
    try:
        if not live_demo_manager:
            return jsonify({'success': False, 'error': 'Live meeting system not initialized'}), 500
        data = request.get_json()
        platform = data.get('platform', 'auto')
        result = live_demo_manager.start_screen_sharing(platform)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/screen-share/stop', methods=['POST'])
def stop_screen_share():
    try:
        if not live_demo_manager:
            return jsonify({'success': False, 'error': 'Live meeting system not initialized'}), 500
        result = live_demo_manager.stop_screen_sharing()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/screen-share/status')
def get_screen_share_status():
    try:
        if not live_demo_manager:
            return jsonify({'available': False, 'error': 'Live meeting system not initialized'})
        status = live_demo_manager.get_screen_share_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'available': False, 'error': str(e)}), 500

@app.route('/api/listen', methods=['POST'])
def voice_listen():
    """Voice listening endpoint for live demo questions"""
    try:
        if not voice_agent:
            return jsonify({'success': False, 'error': 'Voice agent not available'}), 500
        
        # Listen for voice input
        transcription = voice_agent.listen_and_transcribe()
        
        if transcription and transcription.strip():
            return jsonify({
                'success': True,
                'text': transcription.strip()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No speech detected or transcription failed'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Voice recognition error: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Initialize agents in background
    threading.Thread(target=initialize_agents, daemon=True).start()
    
    # Print the URL information
    print("\n🌐 GIKI Transport Web Interface")
    print("=" * 40)
    print("📱 Local URL:    http://localhost:5001")
    print("🌍 Network URL:  http://192.168.1.16:5001")
    print("=" * 40)
    print("💡 Open any of these URLs in your browser to access the interface")
    print("🎤 Voice recognition and browser automation ready!")
    print()
    
    # Start Flask app on port 5001
    app.run(debug=True, host='0.0.0.0', port=5001)


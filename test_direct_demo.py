"""
Direct Demo Test - Test the interactive demo directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.voice_agent import VoiceAgent
from agents.intent_parsing_agent import IntentParsingAgent
from agents.browser_automation_agent_new import BrowserAutomationAgent

def test_direct_demo():
    """Test the interactive demo directly"""
    
    print("🎬 Testing Interactive Demo Directly...")
    
    try:
        # Initialize agents
        print("🔄 Initializing agents...")
        voice_agent = VoiceAgent()
        intent_agent = IntentParsingAgent()
        browser_agent = BrowserAutomationAgent()
        
        # Set agents
        print("🔗 Setting agents...")
        browser_agent.set_agents(voice_agent, intent_agent)
        
        # Run demo
        print("🎬 Starting demo...")
        result = browser_agent.run_interactive_demo()
        
        print(f"✅ Demo result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_demo()

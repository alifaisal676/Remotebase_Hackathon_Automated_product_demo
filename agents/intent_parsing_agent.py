"""
Intent Parsing Agent: Converts natural language commands into structured JSON intents.
Uses Groq API for natural language understanding.
"""

import json
import re
import os
from typing import Dict, Any, List, Optional
from groq import Groq
# Settings removed
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IntentParsingAgent:
    """
    Intent Parsing Agent responsible for:
    1. Parsing free-form natural language commands
    2. Extracting intent and parameters
    3. Converting to structured JSON for browser automation
    4. Handling synonyms and variations
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"  # Fast and efficient model
        
        # Intent templates for consistent parsing
        self.intent_examples = {
            "navigate": {
                "examples": [
                    "Go to the dashboard",
                    "Open settings page",
                    "Take me to login",
                    "Navigate to home"
                ],
                "parameters": ["target_url", "page_name"]
            },
            "click": {
                "examples": [
                    "Click on settings",
                    "Press the login button",
                    "Hit save",
                    "Tap on logout"
                ],
                "parameters": ["element_text", "element_selector"]
            },
            "fill": {
                "examples": [
                    "Fill email as user@example.com",
                    "Enter password as secret123",
                    "Type in username john_doe",
                    "Input phone number 123-456-7890"
                ],
                "parameters": ["field_name", "value"]
            },
            "scroll": {
                "examples": [
                    "Scroll down",
                    "Scroll to bottom",
                    "Scroll up",
                    "Scroll to top"
                ],
                "parameters": ["direction", "amount"]
            },
            "wait": {
                "examples": [
                    "Wait 3 seconds",
                    "Pause for a moment",
                    "Hold on",
                    "Wait for page to load"
                ],
                "parameters": ["duration"]
            }
        }
        
        # Success: Intent agent
    
    def create_parsing_prompt(self, user_command: str) -> str:
        """
        Create a structured prompt for intent parsing.
        
        Args:
            user_command: Raw user command text
            
        Returns:
            Formatted prompt for the LLM
        """
        prompt = f"""
You are an expert intent parser for browser automation commands. 
Your job is to parse natural language commands and return structured JSON.

SUPPORTED INTENTS:
1. navigate - Go to a specific page/URL
2. click - Click on an element (button, link, etc.)
3. fill - Fill in form fields with values
4. scroll - Scroll the page in a direction
5. wait - Wait/pause for a specified time
6. question - Answer questions about the GIKI Transport System

EXAMPLES:
- "Go to dashboard" → {{"intent": "navigate", "page_name": "dashboard"}}
- "Click settings" → {{"intent": "click", "element_text": "settings"}}
- "Fill email as user@test.com" → {{"intent": "fill", "field_name": "email", "value": "user@test.com"}}
- "Scroll down" → {{"intent": "scroll", "direction": "down"}}
- "Wait 3 seconds" → {{"intent": "wait", "duration": 3}}
- "What is GIKI Transport?" → {{"intent": "question", "question": "What is GIKI Transport?"}}

GIKI TRANSPORT SYSTEM CONTEXT:
- This is a transport management system for GIKI university
- Main features: booking transport, viewing tickets, managing profile
- Available pages: dashboard/booking (main), profile, tickets, payment
- Users can book transport, view their tickets, and manage their profile

RULES:
1. Always return valid JSON
2. Use lowercase for intent names
3. Extract specific values when mentioned
4. Handle synonyms (e.g., "press" = "click", "type" = "fill")
5. If unsure, default to the most likely intent
6. Include confidence score (0-1)

USER COMMAND: "{user_command}"

Return only the JSON response:
"""
        return prompt
    
    def parse_command(self, user_command: str) -> Dict[str, Any]:
        """
        Parse a natural language command into structured intent.
        
        Args:
            user_command: Raw command text from user
            
        Returns:
            Structured intent dictionary
        """
        try:
            # Debug: Intent agent action
            
            # Create prompt
            prompt = self.create_parsing_prompt(user_command)
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert intent parser. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract and parse JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown formatting if present)
            response_text = re.sub(r'```json\n?', '', response_text)
            response_text = re.sub(r'```\n?', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON
            intent_data = json.loads(response_text)
            
            # Validate and enrich intent
            validated_intent = self.validate_and_enrich_intent(intent_data, user_command)
            
            # Success: Intent agent
            return validated_intent
            
        except json.JSONDecodeError as e:
            # Error: Intent agent}")
            return self.fallback_parsing(user_command)
            
        except Exception as e:
            # Error: Intent agent}")
            return self.fallback_parsing(user_command)
    
    def validate_and_enrich_intent(self, intent_data: Dict[str, Any], original_command: str) -> Dict[str, Any]:
        """
        Validate and enrich the parsed intent with additional context.
        
        Args:
            intent_data: Raw parsed intent
            original_command: Original user command
            
        Returns:
            Validated and enriched intent
        """
        try:
            # Ensure required fields
            if "intent" not in intent_data:
                raise ValueError("Missing 'intent' field")
            
            intent = intent_data["intent"].lower()
            
            # Enrich with demo URLs and selectors
            if intent == "navigate":
                if "page_name" in intent_data:
                    page_name = intent_data["page_name"].lower()
                    if page_name in {}:
                        intent_data["target_url"] = {}[page_name]
                
                # If no target_url, try to extract from command
                if "target_url" not in intent_data:
                    intent_data["target_url"] = self.extract_url_from_command(original_command)
            
            elif intent == "click":
                if "element_text" in intent_data:
                    element_text = intent_data["element_text"].lower()
                    if element_text in {}:
                        intent_data["element_selector"] = {}[element_text]
            
            # Add confidence score if missing
            if "confidence" not in intent_data:
                intent_data["confidence"] = 0.8  # Default confidence
            
            # Add original command for reference
            intent_data["original_command"] = original_command
            
            return intent_data
            
        except Exception as e:
            # Error: Intent agent}")
            return intent_data  # Return as-is if validation fails
    
    def extract_url_from_command(self, command: str) -> str:
        """
        Extract URL from command text for GIKI Transport System.
        
        Args:
            command: Command text
            
        Returns:
            Extracted URL or constructed URL
        """
        command_lower = command.lower()
        
        # Check for full URLs first
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, command)
        if match:
            return match.group(0)
        
        # GIKI Transport System specific URL mapping (REAL URLs)
        giki_urls = {
            # Authentication pages - be very specific to avoid conflicts
            r'go\s*to\s*sign\s*in|go\s*to\s*login|navigate\s*to\s*sign\s*in|navigate\s*to\s*login': 'https://giktransport.giki.edu.pk:8038/auth/signin/',
            r'go\s*to\s*sign\s*up|go\s*to\s*signup|navigate\s*to\s*sign\s*up|navigate\s*to\s*signup': 'https://giktransport.giki.edu.pk:8038/auth/signup/',
            
            # Home/Main pages - Dashboard & Bookings
            r'giki\s*transport(?:\s*system)?|transport\s*system|my\s*app|my\s*system|my\s*software|giki': 'https://giktransport.giki.edu.pk:8038/',
            r'home|main|index|dashboard|dash|booking(?:\s*page)?': 'https://giktransport.giki.edu.pk:8038/',
            
            # Profile page
            r'profile|my\s*profile': 'https://giktransport.giki.edu.pk:8038/auth/profile/',
            
            # Tickets page
            r'tickets?|my\s*tickets?': 'https://giktransport.giki.edu.pk:8038/my-tickets/',
            
            # Book now / Payment page - ONLY for specific "book now" phrases, NOT "book ticket"
            r'book\s*now|book\s*transport\s*now|pay|payment|wallet': 'https://giktransport.giki.edu.pk:8038/booking/payment/wallet/5/',
        }
        
        # Check for GIKI Transport specific URLs first
        for pattern, url in giki_urls.items():
            if re.search(pattern, command_lower):
                # Debug: Intent agent action
                return url
        
        # Common external sites (fallback)
        external_sites = {
            r'google(?:\.com)?': 'https://www.google.com',
            r'youtube(?:\.com)?': 'https://www.youtube.com',
            r'facebook(?:\.com)?': 'https://www.facebook.com',
            r'twitter(?:\.com)?': 'https://www.twitter.com',
            r'instagram(?:\.com)?': 'https://www.instagram.com',
            r'linkedin(?:\.com)?': 'https://www.linkedin.com',
            r'github(?:\.com)?': 'https://www.github.com',
            r'stackoverflow(?:\.com)?': 'https://www.stackoverflow.com',
            r'amazon(?:\.com)?': 'https://www.amazon.com',
            r'netflix(?:\.com)?': 'https://www.netflix.com',
        }
        
        # Check for external sites
        for pattern, url in external_sites.items():
            if re.search(pattern, command_lower):
                # Debug: Intent agent action
                return url
        
        # Extract .com domains
        dot_com_pattern = r'([a-zA-Z0-9-]+)\.com'
        dot_com_match = re.search(dot_com_pattern, command_lower)
        if dot_com_match:
            domain = dot_com_match.group(1)
            return f"https://www.{domain}.com"
        
        # Default to GIKI Transport home page for any navigation command
        if any(word in command_lower for word in ['go', 'navigate', 'open', 'visit']):
            # Debug: Intent agent action
            return "https://giktransport.giki.edu.pk:8038/"
        
        # Fallback to settings
        return {}.get("home", "https://giktransport.giki.edu.pk:8038/")
    
    def fallback_parsing(self, user_command: str) -> Dict[str, Any]:
        """
        Fallback parsing using simple keyword matching.
        
        Args:
            user_command: Raw command text
            
        Returns:
            Basic intent structure
        """
        try:
            # Debug: Intent agent action
            
            command_lower = user_command.lower()
            
            # Navigate keywords
            if any(keyword in command_lower for keyword in ["go", "navigate", "open", "visit"]):
                return {
                    "intent": "navigate",
                    "target_url": self.extract_url_from_command(user_command),
                    "confidence": 0.6,
                    "original_command": user_command
                }
            
            # Click keywords
            elif any(keyword in command_lower for keyword in ["click", "press", "tap", "hit"]):
                # Extract element text after click keyword
                element_text = self.extract_element_text(command_lower)
                return {
                    "intent": "click",
                    "element_text": element_text,
                    "confidence": 0.6,
                    "original_command": user_command
                }
            
            # Fill keywords
            elif any(keyword in command_lower for keyword in ["fill", "enter", "type", "input"]):
                field_name, value = self.extract_field_and_value(command_lower)
                return {
                    "intent": "fill",
                    "field_name": field_name,
                    "value": value,
                    "confidence": 0.6,
                    "original_command": user_command
                }
            
            # Scroll keywords
            elif any(keyword in command_lower for keyword in ["scroll", "move"]):
                direction = "down" if "down" in command_lower else "up"
                return {
                    "intent": "scroll",
                    "direction": direction,
                    "confidence": 0.6,
                    "original_command": user_command
                }
            
            # Question keywords
            elif any(keyword in command_lower for keyword in ["what", "how", "why", "when", "where", "who", "help", "explain", "tell me", "?"]):
                return {
                    "intent": "question",
                    "question": user_command,
                    "confidence": 0.7,
                    "original_command": user_command
                }
            
            # Default fallback
            else:
                return {
                    "intent": "unknown",
                    "confidence": 0.3,
                    "original_command": user_command,
                    "error": "Could not parse command"
                }
                
        except Exception as e:
            # Error: Intent agent}")
            return {
                "intent": "error",
                "confidence": 0.0,
                "original_command": user_command,
                "error": str(e)
            }
    
    def extract_element_text(self, command: str) -> str:
        """Extract element text from click command."""
        # Simple extraction - look for text after click keywords
        click_keywords = ["click", "press", "tap", "hit"]
        
        for keyword in click_keywords:
            if keyword in command:
                parts = command.split(keyword, 1)
                if len(parts) > 1:
                    text = parts[1].strip()
                    # Remove common prepositions
                    text = re.sub(r'^(on|the|a|an)\s+', '', text)
                    return text
        
        return "button"  # Default
    
    def extract_field_and_value(self, command: str) -> tuple:
        """Extract field name and value from fill command."""
        # Look for pattern: "fill [field] as [value]"
        as_match = re.search(r'fill\s+([^as]+)\s+as\s+(.+)', command)
        if as_match:
            field = as_match.group(1).strip()
            value = as_match.group(2).strip()
            return field, value
        
        # Look for pattern: "enter [value] in [field]"
        in_match = re.search(r'enter\s+([^in]+)\s+in\s+(.+)', command)
        if in_match:
            value = in_match.group(1).strip()
            field = in_match.group(2).strip()
            return field, value
        
        return "input", "value"  # Default
    
    def get_intent_confidence(self, intent_data: Dict[str, Any]) -> float:
        """
        Get confidence score for parsed intent.
        
        Args:
            intent_data: Parsed intent data
            
        Returns:
            Confidence score (0-1)
        """
        return intent_data.get("confidence", 0.5)
    
    def is_valid_intent(self, intent_data: Dict[str, Any], min_confidence: float = 0.5) -> bool:
        """
        Check if intent is valid and has sufficient confidence.
        
        Args:
            intent_data: Parsed intent data
            min_confidence: Minimum confidence threshold
            
        Returns:
            True if intent is valid and confident
        """
        return (
            intent_data.get("intent") != "unknown" and
            intent_data.get("intent") != "error" and
            self.get_intent_confidence(intent_data) >= min_confidence
        )
    
    def answer_question(self, question: str) -> str:
        """
        Answer questions about the GIKI Transport System using LLM.
        
        Args:
            question: User's question
            
        Returns:
            Answer to the question
        """
        try:
            # Debug: Intent agent action
            
            context_prompt = f"""
You are a helpful assistant for the GIKI Transport System. Answer questions about the transport system based on the following context:

GIKI TRANSPORT SYSTEM INFORMATION:
- This is a transport management system for GIKI University students and staff
- Main features:
  * Book transport/bus tickets
  * View booked tickets and travel history
  * Manage user profile and account settings
  * Make payments through wallet system
- Available pages:
  * Dashboard/Booking (main page): https://giktransport.giki.edu.pk:8038/
  * Profile: https://giktransport.giki.edu.pk:8038/auth/profile/
  * My Tickets: https://giktransport.giki.edu.pk:8038/my-tickets/
  * Payment/Wallet: https://giktransport.giki.edu.pk:8038/booking/payment/wallet/5/
- Users can:
  * Book transport by clicking "Book Now"
  * View their booked tickets
  * Update their profile information
  * Make payments through the wallet system
- The system helps students and staff manage their transportation needs at GIKI University

USER QUESTION: {question}

Provide a helpful, concise answer based on the GIKI Transport System context above. If the question is not related to transport or the system, politely redirect to transport-related topics.
"""
            
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for the GIKI Transport System. Provide clear, concise answers."},
                    {"role": "user", "content": context_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            # Success: Intent agent
            return answer
            
        except Exception as e:
            # Error: Intent agent}")
            return "I'm sorry, I couldn't answer that question right now. Please try asking about the GIKI Transport System features like booking, tickets, or profile management."

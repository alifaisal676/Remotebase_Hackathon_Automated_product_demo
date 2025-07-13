"""
Demo Configuration System
Allows product owners to configure custom demos for their websites/products
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import json

@dataclass
class DemoStep:
    """Single step in a demo"""
    name: str
    description: str
    url: str
    action_type: str  # navigate, click, form_fill, showcase
    element_selector: Optional[str] = None
    wait_time: int = 3
    voice_script: Optional[str] = None

@dataclass
class ProductConfig:
    """Complete product demo configuration"""
    product_name: str
    base_url: str
    description: str
    demo_steps: List[DemoStep]
    login_credentials: Optional[Dict[str, str]] = None
    welcome_message: Optional[str] = None
    closing_message: Optional[str] = None

class DemoConfigManager:
    """Manages demo configurations for different products"""
    
    def __init__(self):
        self.configs = {}
        self._load_default_configs()
    
    def _load_default_configs(self):
        """Load default demo configurations"""
        # GIKI Transport (existing demo)
        giki_steps = [
            DemoStep(
                name="Homepage",
                description="Beautiful homepage showcasing the transport booking system",
                url="https://giktransport.giki.edu.pk:8038/",
                action_type="navigate",
                voice_script="Welcome to our homepage! Here you can see our beautiful transport booking interface."
            ),
            DemoStep(
                name="Sign-in Page",
                description="Secure user authentication system",
                url="https://giktransport.giki.edu.pk:8038/auth/signin/",
                action_type="navigate",
                voice_script="Here's our secure sign-in page where users can safely access their accounts."
            ),
            DemoStep(
                name="Automatic Login",
                description="Seamless login demonstration",
                url="https://giktransport.giki.edu.pk:8038/auth/signin/",
                action_type="login",
                voice_script="Watch as I automatically log in to show you the authenticated experience."
            ),
            DemoStep(
                name="Dashboard",
                description="Main user dashboard with booking options",
                url="https://giktransport.giki.edu.pk:8038/",
                action_type="navigate",
                voice_script="Welcome to the main dashboard! This is your central hub for all transport bookings."
            ),
            DemoStep(
                name="Profile Management",
                description="User profile and account settings",
                url="https://giktransport.giki.edu.pk:8038/auth/profile/",
                action_type="navigate",
                voice_script="Users can manage their personal information and preferences here."
            ),
            DemoStep(
                name="Ticket Management",
                description="View and manage transport tickets",
                url="https://giktransport.giki.edu.pk:8038/my-tickets/",
                action_type="navigate",
                voice_script="This is where users can view and manage all their transport tickets."
            ),
            DemoStep(
                name="Booking System",
                description="Complete ticket booking process",
                url="https://giktransport.giki.edu.pk:8038/booking/payment/wallet/5/",
                action_type="navigate",
                voice_script="Here's our powerful booking system where users can book their transport tickets."
            ),
            DemoStep(
                name="Demo Complete",
                description="Demo conclusion with summary",
                url="https://giktransport.giki.edu.pk:8038/",
                action_type="navigate",
                voice_script="That's our complete tour! GIKI Transport provides seamless booking, secure payments, and excellent user experience."
            )
        ]
        
        giki_config = ProductConfig(
            product_name="GIKI Transport",
            base_url="https://giktransport.giki.edu.pk:8038/",
            description="Campus transport booking system for GIKI students",
            demo_steps=giki_steps,
            login_credentials={"email": "fahad.aziz@giki.edu.pk", "password": "12345678"},
            welcome_message="Welcome! I'm your personal GIKI Transport assistant, ready to showcase our amazing transport booking platform!",
            closing_message="Thank you for exploring GIKI Transport! We're revolutionizing campus transportation with seamless booking and user-friendly design."
        )
        
        self.configs["giki_transport"] = giki_config
    
    def add_custom_config(self, config: ProductConfig) -> str:
        """Add a new product configuration"""
        config_id = config.product_name.lower().replace(" ", "_")
        self.configs[config_id] = config
        return config_id
    
    def get_config(self, config_id: str) -> Optional[ProductConfig]:
        """Get configuration by ID"""
        return self.configs.get(config_id)
    
    def list_configs(self) -> Dict[str, str]:
        """List all available configurations"""
        return {
            config_id: config.product_name 
            for config_id, config in self.configs.items()
        }
    
    def create_config_from_input(self, product_data: Dict) -> ProductConfig:
        """Create configuration from user input"""
        steps = []
        for step_data in product_data.get('steps', []):
            step = DemoStep(
                name=step_data['name'],
                description=step_data['description'],
                url=step_data['url'],
                action_type=step_data.get('action_type', 'navigate'),
                element_selector=step_data.get('element_selector'),
                wait_time=step_data.get('wait_time', 3),
                voice_script=step_data.get('voice_script', f"Here's {step_data['name']} - {step_data['description']}")
            )
            steps.append(step)
        
        return ProductConfig(
            product_name=product_data['product_name'],
            base_url=product_data['base_url'],
            description=product_data['description'],
            demo_steps=steps,
            login_credentials=product_data.get('login_credentials'),
            welcome_message=product_data.get('welcome_message'),
            closing_message=product_data.get('closing_message')
        )
    
    def save_config_to_file(self, config: ProductConfig, filename: str):
        """Save configuration to JSON file"""
        config_dict = {
            'product_name': config.product_name,
            'base_url': config.base_url,
            'description': config.description,
            'login_credentials': config.login_credentials,
            'welcome_message': config.welcome_message,
            'closing_message': config.closing_message,
            'demo_steps': [
                {
                    'name': step.name,
                    'description': step.description,
                    'url': step.url,
                    'action_type': step.action_type,
                    'element_selector': step.element_selector,
                    'wait_time': step.wait_time,
                    'voice_script': step.voice_script
                }
                for step in config.demo_steps
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def load_config_from_file(self, filename: str) -> ProductConfig:
        """Load configuration from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        return self.create_config_from_input(data)

# Global demo config manager
demo_config_manager = DemoConfigManager()

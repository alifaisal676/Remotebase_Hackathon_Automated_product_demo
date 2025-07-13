"""
Test Dynamic Demo Configuration System
Simple test to verify the dynamic demo system works
"""

from demo_config import demo_config_manager, ProductConfig, DemoStep

def test_demo_config():
    """Test creating a custom demo configuration"""
    
    print("🧪 Testing Dynamic Demo Configuration System")
    print("=" * 50)
    
    # Test 1: List existing configurations
    print("📋 Existing demo configurations:")
    configs = demo_config_manager.list_configs()
    for config_id, name in configs.items():
        print(f"  • {config_id}: {name}")
    
    # Test 2: Create a new custom demo configuration
    print("\n🆕 Creating custom demo configuration...")
    
    custom_steps = [
        DemoStep(
            name="Homepage",
            description="Landing page with main features",
            url="https://example.com",
            action_type="navigate",
            voice_script="Welcome to our amazing platform! This is our beautiful homepage where users first discover our features."
        ),
        DemoStep(
            name="Features Page",
            description="Detailed feature showcase",
            url="https://example.com/features",
            action_type="navigate",
            voice_script="Here you can see all our powerful features that make our platform unique."
        ),
        DemoStep(
            name="Contact Us",
            description="Contact information and support",
            url="https://example.com/contact",
            action_type="navigate",
            voice_script="And here's how users can get in touch with our support team."
        )
    ]
    
    custom_config = ProductConfig(
        product_name="Example E-commerce Platform",
        base_url="https://example.com",
        description="A modern e-commerce solution with seamless user experience",
        demo_steps=custom_steps,
        welcome_message="Hello! Welcome to our Example E-commerce Platform demo. I'll show you how easy it is to create amazing online stores!",
        closing_message="Thank you for exploring our platform! We hope you can see the potential for your business. Contact us to get started!"
    )
    
    # Add the custom configuration
    config_id = demo_config_manager.add_custom_config(custom_config)
    print(f"✅ Custom demo created with ID: {config_id}")
    
    # Test 3: Retrieve and display the configuration
    print(f"\n📖 Retrieving configuration: {config_id}")
    retrieved_config = demo_config_manager.get_config(config_id)
    
    if retrieved_config:
        print(f"  Product: {retrieved_config.product_name}")
        print(f"  Description: {retrieved_config.description}")
        print(f"  Base URL: {retrieved_config.base_url}")
        print(f"  Steps: {len(retrieved_config.demo_steps)}")
        
        for i, step in enumerate(retrieved_config.demo_steps, 1):
            print(f"    {i}. {step.name} -> {step.url}")
    
    # Test 4: List all configurations again
    print("\n📋 Updated demo configurations:")
    configs = demo_config_manager.list_configs()
    for config_id, name in configs.items():
        print(f"  • {config_id}: {name}")
    
    print("\n✅ Dynamic Demo Configuration System Test Completed!")
    print("🎯 The system can now handle any product demo configuration!")

if __name__ == "__main__":
    test_demo_config()

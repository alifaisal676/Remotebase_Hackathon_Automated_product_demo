# 🎬 GIKI Transport Interactive Demo

An advanced voice-controlled browser automation system that provides interactive demos of the GIKI Transport platform with real-time Q&A capabilities.

## ✨ Features

- **🎤 Voice Recognition**: Google Speech Recognition for hands-free interaction
- **🔊 Text-to-Speech**: ElevenLabs AI for natural voice responses  
- **🎬 Interactive Demos**: Automated browser demonstrations with live Q&A
- **🤖 AI-Powered Q&A**: LLM-based question answering during demos
- **🌐 Web Interface**: Modern Flask-based web UI
- **🎯 Modular Architecture**: Clean separation of concerns with dedicated agents

## 🏗️ Architecture

### Core Components

```
├── agents/
│   ├── voice_agent.py              # Speech-to-text & text-to-speech
│   ├── intent_parsing_agent.py     # LLM-based intent understanding
│   ├── browser_automation_agent_new.py  # Main browser automation
│   └── browser_modules/
│       ├── browser_core.py         # Core browser functionality
│       ├── giki_transport_actions.py  # GIKI-specific actions
│       └── interactive_demo.py     # Demo orchestration + Q&A
├── templates/
│   ├── index.html                  # Main web interface
│   └── qa_test.html               # Q&A testing interface
└── web_interface.py               # Flask web server
```

### Agent Responsibilities

- **VoiceAgent**: Handles all audio I/O using Google STT + ElevenLabs TTS
- **IntentParsingAgent**: Uses Groq/LLM for natural language understanding  
- **BrowserAutomationAgent**: Orchestrates browser actions and demos
- **InteractiveDemo**: Manages demo flow with seamless Q&A interruption

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Microphone and speakers
- API Keys (see Environment Setup)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Remotebase_Hackathon
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file with your API keys:
   ```env
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

4. **Run the application**
   ```bash
   python web_interface.py
   ```

5. **Access the interface**
   Open http://localhost:5001 in your browser

## 🎯 Usage

### Interactive Demo
1. Click "Start Interactive Demo" 
2. Watch the automated browser demonstration
3. Press the microphone button anytime to ask questions
4. The system will pause, answer your question, and continue the demo

### Voice Commands
- "Show demo" - Start the interactive demonstration
- "Go to signin" - Navigate to sign-in page
- "Check my profile" - View profile information  
- "Book a ticket" - Access booking system
- Ask any question about GIKI Transport features

### Q&A Testing
- Visit `/qa_test_page` for isolated Q&A testing
- Adjust volume and test voice recognition
- Perfect for debugging and fine-tuning

## 🛠️ Configuration

### Voice Settings
```python
# In voice_agent.py
self.volume = 0.8          # TTS volume (0.0-1.0)
voice_id = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs voice
```

### Demo Timing
```python
# In interactive_demo.py  
self.wait_with_qa_option(2.0)  # Pause between demo steps
```

### Browser Settings
```python
# In browser_core.py
self.options.add_argument("--no-sandbox")
self.options.add_argument("--disable-dev-shm-usage")
```

## 🔧 API Integration

### ElevenLabs TTS
- High-quality voice synthesis
- Configurable voice selection
- Real-time audio generation

### Groq LLM
- Fast inference for Q&A
- Context-aware responses
- Fallback answer system

### Google Speech Recognition
- Free speech-to-text
- Ambient noise adjustment
- Timeout handling

## 📁 Project Structure

```
Remotebase_Hackathon/
├── agents/                 # Core agent modules
│   ├── browser_modules/   # Modular browser components
│   └── *.py              # Individual agents
├── templates/             # Web interface templates
├── static/               # CSS, JS, assets (if any)
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies  
├── web_interface.py     # Main Flask application
└── README.md           # This file
```

## 🎬 Demo Flow

1. **Homepage Navigation** - Shows GIKI Transport landing page
2. **Authentication** - Demonstrates sign-in functionality  
3. **Dashboard Tour** - Explores main user interface
4. **Profile Management** - Shows user profile features
5. **Ticket System** - Demonstrates ticket management
6. **Booking Process** - Interactive booking demonstration
7. **Q&A Sessions** - Real-time question answering throughout

## 🔍 Troubleshooting

### Audio Issues
- Ensure microphone permissions are granted
- Check ElevenLabs API key is valid
- Verify pygame audio initialization

### Browser Issues  
- Install latest Chrome/Chromium
- Check ChromeDriver compatibility
- Verify website accessibility

### API Issues
- Confirm API keys in `.env` file
- Check internet connectivity  
- Verify API rate limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **GIKI Transport** - Target demonstration platform
- **ElevenLabs** - AI voice synthesis  
- **Groq** - Fast LLM inference
- **Google** - Speech recognition services
- **Selenium** - Browser automation framework

## 📊 Technical Highlights

- **Modular Design**: Clean separation between voice, browser, and AI components
- **Real-time Q&A**: Seamless interruption and continuation of demos
- **Robust Error Handling**: Graceful fallbacks for all external services
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Scalable Architecture**: Easy to extend with new features and integrations

---

Built with ❤️ for the Remotebase Hackathon

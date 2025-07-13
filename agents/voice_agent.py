"""
Voice Agent: Handles Speech-to-Text (STT) and Text-to-Speech (TTS) operations.
Uses Google Speech Recognition (FREE) for STT and ElevenLabs for TTS.
"""

import time
import io
import tempfile
import os
import pygame
import speech_recognition as sr
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import audio libraries
try:
    import simpleaudio as sa
    SIMPLEAUDIO_AVAILABLE = True
except ImportError:
    SIMPLEAUDIO_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class VoiceAgent:
    """
    Voice Agent responsible for:
    1. Recording user voice input using Google Speech Recognition (FREE)
    2. Converting speech to text using Google STT (FREE)
    3. Converting text responses to speech using ElevenLabs (your API)
    4. Playing audio responses to user
    """
    
    def __init__(self):
        # Initialize Google Speech Recognition (FREE)
        self.recognizer = sr.Recognizer()
        
        # Try to initialize microphone, handle PyAudio errors gracefully
        try:
            self.microphone = sr.Microphone()
            self.use_microphone = True
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            print("✅ Microphone initialized successfully")
        except Exception as e:
            self.use_microphone = False
            print(f"⚠️  Microphone initialization failed: {str(e)}")
            print("💡 Will use text input as fallback")
        
        # Initialize ElevenLabs (your API)
        try:
            elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
            if elevenlabs_api_key:
                self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
                
                # Initialize pygame mixer for audio playback with higher volume
                pygame.mixer.init()
                pygame.mixer.music.set_volume(1.0)  # Set maximum volume
                self.volume = 0.8  # Default volume (0.0 to 1.0)
                self.audio_enabled = True
                print("✅ ElevenLabs TTS initialized successfully")
            else:
                print("⚠️ ELEVENLABS_API_KEY not found in environment")
                self.elevenlabs_client = None
                self.audio_enabled = False
                self.volume = 0.8  # Default volume even without TTS
            
        except Exception as e:
            print(f"⚠️  ElevenLabs initialization failed: {str(e)}")
            print("💡 Will use text output as fallback")
            self.elevenlabs_client = None
            self.audio_enabled = False
            self.volume = 1.0 # Default volume even without TTS
        
        print("✅ VoiceAgent initialized with Google STT (FREE) + ElevenLabs TTS")
    
    def listen_and_transcribe(self, use_silence_detection: bool = True) -> str:
        """
        Complete workflow: Record audio and transcribe to text using FREE Google STT.
        Falls back to text input if microphone is unavailable.
        
        Args:
            use_silence_detection: Not used in this implementation
            
        Returns:
            Transcribed text
        """
        try:
            # Debug: Voice agent action
            
            if self.use_microphone:
                # Use microphone if available
                with self.microphone as source:
                    print("🎤 Listening... (speak now)")
                    # Debug: Voice agent action
                    
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                
                # Transcribe using Google STT (FREE)
                # Debug: Voice agent action
                text = self.recognizer.recognize_google(audio)
                
                # Success: Voice agent
                return text
            else:
                # Fallback to text input if microphone unavailable
                print("🎤 Microphone not available, using text input:")
                text = input("Type your command: ").strip()
                if text:
                    # Success: Voice agent
                    return text
                else:
                    return "I didn't receive any input. Please try again."
            
        except sr.WaitTimeoutError:
            # Error: Voice agent
            return "I didn't hear anything. Please try again."
        except sr.UnknownValueError:
            # Error: Voice agent
            return "I couldn't understand what you said. Please try again."
        except sr.RequestError as e:
            # Error: Voice agent}")
            return "Speech recognition service is unavailable. Please try again."
        except Exception as e:
            # Error: Voice agent}")
            # Fallback to text input
            print("🎤 Voice input failed, using text input:")
            text = input("Type your command: ").strip()
            return text if text else "An error occurred while processing your input."
    
    def speak_response(self, text: str, voice_id: str = None):
        """
        Simple text-to-speech conversion and playback
        """
        try:
            print(f"🔊 Speaking: '{text[:30]}{'...' if len(text) > 30 else ''}'")
            
            if not self.elevenlabs_client or not self.audio_enabled:
                print(f"🔊 System: {text}")  # Fallback to text output
                return
            
            if not voice_id:
                voice_id = "21m00Tcm4TlvDq8ikWAM"
            
            # Generate speech
            audio_generator = self.elevenlabs_client.generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
            
            # Convert to bytes and play
            audio_data = b"".join(audio_generator)
            self.play_audio(audio_data)
            
        except Exception as e:
            print(f"❌ Voice error: {e}")
            print(f"🔊 {text}")  # Fallback to text
    
    def play_audio(self, audio_data: bytes):
        """
        Simple audio playback - just play it completely
        """
        # Try pygame first (most reliable)
        try:
            self.play_audio_pygame(audio_data)
            return
        except Exception as e:
            print(f"Pygame failed: {e}")
        
        # Try pydub as backup
        if PYDUB_AVAILABLE:
            try:
                audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
                play(audio_segment)
                # Simple wait for completion
                duration_seconds = len(audio_segment) / 1000.0
                time.sleep(duration_seconds + 0.5)  # Wait full duration + buffer
                print("✅ Pydub playback completed")
                return
            except Exception as e:
                print(f"Pydub failed: {e}")
        
        print("❌ All audio methods failed")
    
    def play_audio_windows(self, audio_data: bytes):
        """
        Play audio using Windows PowerShell.
        
        Args:
            audio_data: Audio bytes to play
        """
        import subprocess
        import uuid
        
        # Create a unique temporary file
        unique_id = str(uuid.uuid4())
        temp_file_path = os.path.join(tempfile.gettempdir(), f"voice_{unique_id}.mp3")
        
        try:
            # Write audio data to file
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(audio_data)
            
            # Use PowerShell to play the audio
            powershell_cmd = f'''
            Add-Type -AssemblyName presentationCore
            $mediaPlayer = New-Object system.windows.media.mediaplayer
            $mediaPlayer.open("{temp_file_path}")
            $mediaPlayer.Play()
            Start-Sleep -Seconds 5
            $mediaPlayer.Stop()
            $mediaPlayer.Close()
            '''
            
            result = subprocess.run([
                'powershell', '-command', powershell_cmd
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise Exception(f"PowerShell command failed: {result.stderr}")
            
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except:
                pass  # File might still be in use
    
    def play_audio_pygame(self, audio_data: bytes):
        """
        Play audio using pygame with robust blocking (preferred method).
        
        Args:
            audio_data: Audio bytes to play
        """
        import uuid
        
        # Create a unique temporary file
        unique_id = str(uuid.uuid4())
        temp_file_path = os.path.join(tempfile.gettempdir(), f"pygame_{unique_id}.mp3")
        
        try:
            # Write audio data to file
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(audio_data)
            
            # Initialize pygame mixer properly
            pygame.mixer.quit()  # Clean slate
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            
            # Load and play the audio
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            print(f"🔊 Playing audio... Volume: {self.volume}")
            
            # Simple blocking wait - let it complete naturally
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            print(f"✅ Audio completed")
            
            # Small pause for natural flow
            time.sleep(0.2)
            
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    print(f"🗑️ Cleaned up temp file: {temp_file_path}")
            except Exception as cleanup_error:
                print(f"⚠️ Cleanup warning: {cleanup_error}")
            except:
                pass  # File might still be in use
    
    def stop_audio(self):
        """Gentle audio stop if needed"""
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                print("🛑 Audio gently stopped")
        except:
            pass
    
    def get_voice_input(self):
        """Alias for listen_and_transcribe for backward compatibility"""
        return self.listen_and_transcribe()

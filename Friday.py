#!/usr/bin/env python3
"""
Friday Voice Assistant - Llama2 Powered
A completely voice-operated AI assistant with proper type annotations
"""

import os
import sys
import time
import datetime
import random
import webbrowser
import subprocess
import threading
import json
import re
from typing import Optional, Dict, List, Any, Tuple, Union

# Type checking and imports with proper error handling
try:
    import speech_recognition as sr
    print("✅ SpeechRecognition imported successfully")
    # Verify Google recognition is available
    test_recognizer = sr.Recognizer()
    if hasattr(test_recognizer, 'recognize_google'):
        print("✅ Google Speech Recognition available")
    else:
        print("⚠️ Google Speech Recognition method not found")
except ImportError:
    print("❌ SpeechRecognition not found. Install with: pip install SpeechRecognition")
    sys.exit(1)
except Exception as e:
    print(f"⚠️ SpeechRecognition import issue: {e}")
    print("   Try reinstalling: pip uninstall SpeechRecognition && pip install SpeechRecognition")
    sys.exit(1)

try:
    from gtts import gTTS
    print("✅ gTTS imported successfully")
except ImportError:
    print("❌ gTTS not found. Install with: pip install gtts")
    sys.exit(1)

try:
    import playsound
    print("✅ playsound imported successfully")
except ImportError:
    print("❌ playsound not found. Install with: pip install playsound==1.2.2")
    sys.exit(1)

# Optional imports with None fallbacks
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    print("✅ pyautogui imported successfully")
except ImportError:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui not found. System control features disabled.")

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
    print("✅ wikipedia imported successfully")
except ImportError:
    wikipedia = None
    WIKIPEDIA_AVAILABLE = False
    print("⚠️ wikipedia not found. Wikipedia features disabled.")

try:
    import requests
    REQUESTS_AVAILABLE = True
    print("✅ requests imported successfully")
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False
    print("⚠️ requests not found. Weather and news features disabled.")

try:
    from ollama import Client
    OLLAMA_AVAILABLE = True
    print("✅ ollama imported successfully")
except ImportError:
    Client = None
    OLLAMA_AVAILABLE = False
    print("⚠️ ollama not found. AI features will be limited. Install with: pip install ollama")

# Create and import music library
def create_music_library() -> None:
    """Create the music library file if it doesn't exist"""
    if not os.path.exists("music_library.py"):
        music_lib_content = '''# Music Library for Friday Voice Assistant
# Add your favorite songs here with their YouTube links

music: dict[str, str] = {
    # Popular English Songs
    "shape of you": "https://youtu.be/JGwWNGJdvx8",
    "blinding lights": "https://youtu.be/4NRXx6U8ABQ",
    "perfect": "https://youtu.be/2Vv-BfVoq4g",
    "someone like you": "https://youtu.be/hLQl3WQQoQ0",
    "despacito": "https://youtu.be/kJQP7kiw5Fk",
    "bad guy": "https://youtu.be/DyDfgMOUjCI",
    "uptown funk": "https://youtu.be/OPf0YbXqDm0",
    
    # Indian/Bollywood Songs
    "tum hi ho": "https://youtu.be/IJq0yyWug1k",
    "kal ho na ho": "https://youtu.be/tVMAQAsjsOU",
    "gerua": "https://youtu.be/AEIVhBS6baE",
    "channa mereya": "https://youtu.be/bzSTpdcs-EI",
    
    # Playlists
    "my playlist": "https://youtu.be/AbkEmIgJMcU?si=V6ETJmVWDU2zOEtq",
    "workout playlist": "https://youtu.be/iFGc9vpN338",
    "party songs": "https://youtu.be/ZbZSe6N_BXs",
    "romantic songs": "https://youtu.be/IJq0yyWug1k",
    "chill music": "https://youtu.be/5qap5aO4i9A",
    "study music": "https://youtu.be/7NOSDKb0HlU"
}
'''
        with open("music_library.py", "w", encoding="utf-8") as f:
            f.write(music_lib_content)
        print("✅ music_library.py created successfully!")

# Create music library
create_music_library()

# Import music library with proper error handling
try:
    import music_library
    print("✅ Music library loaded successfully")
except ImportError:
    print("❌ Failed to import music library")
    sys.exit(1)


class VoiceFridayAssistant:
    """Main Friday Voice Assistant class with Llama2 integration"""
    
    def __init__(self) -> None:
        """Initialize the voice assistant"""
        self.recognizer: sr.Recognizer = sr.Recognizer()
        self.is_listening: bool = True
        self.conversation_context: List[Dict[str, str]] = []
        
        # Initialize Llama2 client
        self.llama_client: Optional[Any] = None
        if OLLAMA_AVAILABLE and Client is not None:
            try:
                self.llama_client = Client(host='http://localhost:11434')
            except Exception:
                self.llama_client = None
        
        # Test Llama2 connection
        self.initialize_llama()
        
        # Voice settings
        self.voice_lang: str = "en"
        self.voice_slow: bool = False
        
        # Reminders storage
        self.active_reminders: List[Tuple[str, int]] = []

    def initialize_llama(self) -> None:
        """Initialize and test Llama2 connection"""
        if not OLLAMA_AVAILABLE or Client is None:
            self.speak("AI features limited. Ollama not installed.")
            print("⚠️ Ollama not available. Install with: pip install ollama")
            return
            
        if self.llama_client is None:
            self.speak("Warning: Llama2 model not available. I'll work with basic functions.")
            print("❌ Llama2 client initialization failed")
            return
            
        try:
            # Test if Llama2 is available
            response = self.llama_client.chat(
                model='llama2',
                messages=[{'role': 'user', 'content': 'Hello, are you working?'}]
            )
            self.speak("Llama2 AI model connected successfully!")
            print("✅ Llama2 model is ready")
        except Exception as e:
            self.speak("Warning: Llama2 model not available. I'll work with basic functions.")
            print(f"❌ Llama2 connection failed: {e}")
            print("To setup: 1) Install Ollama from ollama.ai")
            print("         2) Run: ollama pull llama2")
            print("         3) Run: ollama serve")
            self.llama_client = None

    def speak(self, text: str) -> None:
        """Convert text to speech"""
        print(f"Friday said: {text}")
        try:
            tts = gTTS(text=text, lang=self.voice_lang, slow=self.voice_slow)
            filename = f"voice_{int(time.time())}.mp3"
            tts.save(filename)
            playsound.playsound(filename)
            os.remove(filename)
        except Exception as e:
            print(f"Speech error: {e}")

    def listen(self, timeout: float = 5) -> str:
        """Listen for voice input"""
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5) # type: ignore
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = False

            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                # Use Google Speech Recognition with proper type handling
                command: str = self.recognizer.recognize_google(audio, language="en-IN") # pyright: ignore[reportAttributeAccessIssue]
                print(f"👤 You said: {command}")
                return command.lower().strip()
            except sr.WaitTimeoutError:
                return "timeout"
            except sr.UnknownValueError:
                self.speak("I couldn't understand that. Please try again.")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                self.speak("Speech service is unavailable right now.")
                return ""
            except Exception as e:
                print(f"Listen error: {e}")
                return ""

    def ask_llama(self, question: str, context_type: str = "general") -> str:
        """Get response from Llama2"""
        if not self.llama_client:
            # Fallback responses when Llama2 is not available
            fallback_responses: Dict[str, str] = {
                "hello": "Hello! I'm Friday, your voice assistant. How can I help you today?",
                "how are you": "I'm doing great and ready to help you with anything you need!",
                "what can you do": "I can help with opening websites, telling time, weather updates, calculations, reminders, and much more!",
                "default": "I'm sorry, my AI brain isn't fully connected right now, but I can still help with basic tasks like opening websites, telling time, and controlling your system."
            }
            
            question_lower = question.lower()
            for key, response in fallback_responses.items():
                if key in question_lower:
                    return response
            return fallback_responses["default"]
        
        try:
            # Prepare context-aware prompt
            system_prompts: Dict[str, str] = {
                "general": "You are Friday, a helpful voice assistant. Give concise, conversational responses suitable for text-to-speech. Keep responses under 100 words unless specifically asked for detailed information. Be friendly and natural.",
                "task": "You are Friday, a voice assistant helping with tasks. Provide step-by-step instructions clearly and concisely for voice delivery.",
                "creative": "You are Friday, a creative voice assistant. Provide engaging, imaginative content suitable for audio delivery."
            }
            
            system_prompt = system_prompts.get(context_type, system_prompts["general"])

            # Add conversation context
            messages: List[Dict[str, str]] = [{'role': 'system', 'content': system_prompt}]
            
            # Add recent conversation history (last 3 exchanges)
            for ctx in self.conversation_context[-6:]:
                messages.append(ctx)
            
            messages.append({'role': 'user', 'content': question})

            response = self.llama_client.chat(
                model='llama2',
                messages=messages,
                options={
                    'temperature': 0.7,
                    'max_tokens': 200
                }
            )
            
            # Handle response safely
            if isinstance(response, dict) and 'message' in response:
                ai_response = response['message']['content'].strip()
            else:
                ai_response = str(response).strip()
            
            # Update conversation context
            self.conversation_context.append({'role': 'user', 'content': question})
            self.conversation_context.append({'role': 'assistant', 'content': ai_response})
            
            # Keep only last 10 exchanges
            if len(self.conversation_context) > 20:
                self.conversation_context = self.conversation_context[-20:]
            
            return ai_response
            
        except Exception as e:
            print(f"Llama2 error: {e}")
            return "I'm having trouble connecting to my AI brain right now, but I'm still here to help with other tasks!"

    def get_weather(self, city: str = "Delhi") -> str:
        """Get weather information"""
        if not REQUESTS_AVAILABLE or requests is None:
            return "Weather service requires the requests package. Please install it."
            
        try:
            # Using a free weather API (replace with your API key)
            api_key = "YOUR_WEATHER_API_KEY"  # Get from openweathermap.org
            if api_key == "YOUR_WEATHER_API_KEY":
                return "Please configure weather API key for weather updates."
                
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            complete_url = f"{base_url}appid={api_key}&q={city}&units=metric"
            
            response = requests.get(complete_url, timeout=5)
            data = response.json()
            
            if data.get("cod") != "404":
                weather = data["weather"][0]["description"]
                temperature = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                
                return f"Weather in {city}: {weather}, {temperature} degrees, feels like {feels_like} degrees."
            else:
                return f"Sorry, I couldn't find weather information for {city}."
        except Exception:
            return "Weather service is currently unavailable."

    def set_reminder_voice(self, reminder_text: str, minutes: int) -> str:
        """Set a voice reminder"""
        def reminder_thread() -> None:
            time.sleep(minutes * 60)
            self.speak(f"Reminder alert! {reminder_text}")
            # Remove from active reminders
            if (reminder_text, minutes) in self.active_reminders:
                self.active_reminders.remove((reminder_text, minutes))
        
        # Add to active reminders
        self.active_reminders.append((reminder_text, minutes))
        threading.Thread(target=reminder_thread, daemon=True).start()
        return f"Reminder set for {minutes} minutes: {reminder_text}"

    def voice_calculator(self, expression: str) -> str:
        """Voice-friendly calculator"""
        try:
            # Convert voice input to mathematical expression
            expression = expression.replace("calculate", "").replace("what is", "").strip()
            expression = expression.replace("plus", "+").replace("add", "+")
            expression = expression.replace("minus", "-").replace("subtract", "-")
            expression = expression.replace("times", "*").replace("multiply", "*")
            expression = expression.replace("divided by", "/").replace("divide", "/")
            expression = expression.replace("to the power of", "**").replace("squared", "**2")
            expression = expression.replace("cubed", "**3")
            
            # Handle word numbers
            word_to_num: Dict[str, str] = {
                "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
                "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
                "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
                "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
                "eighteen": "18", "nineteen": "19", "twenty": "20"
            }
            
            for word, num in word_to_num.items():
                expression = expression.replace(word, num)
            
            result = eval(expression)
            return f"The answer is {result}"
        except Exception:
            return "I couldn't calculate that. Please try rephrasing the math problem."

    def handle_voice_command(self, command: str) -> str:
        """Process voice commands with Llama2 integration"""
        
        # Quick system commands (no AI needed)
        if any(exit_cmd in command for exit_cmd in ["exit", "quit", "goodbye friday"]):
            self.speak("Goodbye boss, Friday is going offline!")
            return "exit"
        
        elif any(sleep_cmd in command for sleep_cmd in ["stop listening", "sleep friday"]):
            self.speak("I'll stop listening. Say 'Friday' to wake me up again.")
            return "sleep"
        
        # Website opening commands
        elif any(site in command for site in ["open youtube", "youtube"]):
            webbrowser.open("https://youtube.com")
            self.speak("Opening YouTube")
            return "continue"
            
        elif any(site in command for site in ["open instagram", "instagram"]):
            webbrowser.open("https://instagram.com")
            self.speak("Opening Instagram")
            return "continue"
            
        elif any(site in command for site in ["open github", "github"]):
            webbrowser.open("https://github.com")
            self.speak("Opening GitHub")
            return "continue"
            
        elif any(site in command for site in ["open google", "google search"]):
            self.speak("What would you like me to search for?")
            search_query = self.listen()
            if search_query and search_query != "timeout":
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                self.speak(f"Searching Google for {search_query}")
            return "continue"
        
        # Time and date
        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"It's {current_time}")
            return "continue"
            
        elif "date" in command:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
            return "continue"
        
        # Weather
        elif "weather" in command:
            city = "Delhi"  # Default city
            if "in" in command:
                words = command.split()
                if "in" in words:
                    city_index = words.index("in") + 1
                    if city_index < len(words):
                        city = words[city_index]
            
            weather_info = self.get_weather(city)
            self.speak(weather_info)
            return "continue"
        
        # Calculator
        elif any(calc in command for calc in ["calculate", "math", "what is", "plus", "minus", "times", "divide"]):
            result = self.voice_calculator(command)
            self.speak(result)
            return "continue"
        
        # Reminders
        elif any(reminder_cmd in command for reminder_cmd in ["remind me", "set reminder"]):
            self.speak("What should I remind you about?")
            reminder_text = self.listen()
            if reminder_text and reminder_text != "timeout":
                self.speak("In how many minutes?")
                time_input = self.listen()
                try:
                    match = re.search(r'\d+', time_input)
                    if match:
                        minutes = int(match.group())
                        result = self.set_reminder_voice(reminder_text, minutes)
                        self.speak(result)
                    else:
                        self.speak("I didn't understand the time. Please try again.")
                except Exception:
                    self.speak("I didn't understand the time. Please try again.")
            return "continue"
        
        # System controls
        elif "volume up" in command:
            if PYAUTOGUI_AVAILABLE and pyautogui is not None:
                pyautogui.press("volumeup", presses=3)
                self.speak("Volume increased")
            else:
                self.speak("System control not available")
            return "continue"
            
        elif "volume down" in command:
            if PYAUTOGUI_AVAILABLE and pyautogui is not None:
                pyautogui.press("volumedown", presses=3)
                self.speak("Volume decreased")
            else:
                self.speak("System control not available")
            return "continue"
            
        elif "mute" in command:
            if PYAUTOGUI_AVAILABLE and pyautogui is not None:
                pyautogui.press("volumemute")
                self.speak("Audio muted")
            else:
                self.speak("System control not available")
            return "continue"
        
        # Wikipedia search
        elif any(info_cmd in command for info_cmd in ["tell me about", "information about"]):
            topic = command.replace("tell me about", "").replace("information about", "").strip()
            if not topic:
                self.speak("What would you like to know about?")
                topic = self.listen()
            
            if topic and topic != "timeout":
                if WIKIPEDIA_AVAILABLE and wikipedia is not None:
                    try:
                        info = wikipedia.summary(topic, sentences=2)
                        self.speak(info)
                    except Exception:
                        # Fallback to Llama2 or basic response
                        if self.llama_client:
                            response = self.ask_llama(f"Tell me about {topic}", "general")
                            self.speak(response)
                        else:
                            self.speak(f"I don't have detailed information about {topic} right now.")
                else:
                    # Use Llama2 if Wikipedia is not available
                    response = self.ask_llama(f"Tell me about {topic}", "general")
                    self.speak(response)
            return "continue"
        
        # Music/Entertainment
        elif command.startswith("play"):
            song = command.replace("play", "").strip()
            
            # Check if song exists in music library
            if hasattr(music_library, 'music') and song in music_library.music:
                webbrowser.open(music_library.music[song])
                self.speak(f"Playing {song}")
            else:
                # Search on YouTube if not in library
                search_query = song.replace(" ", "+")
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
                self.speak(f"Searching for {song} on YouTube")
            return "continue"
        
        # General AI conversation - Use Llama2
        else:
            # Determine context type
            context_type = "general"
            if any(word in command for word in ["how to", "steps", "guide", "tutorial"]):
                context_type = "task"
            elif any(word in command for word in ["story", "poem", "creative", "imagine"]):
                context_type = "creative"
            
            response = self.ask_llama(command, context_type)
            self.speak(response)
            return "continue"

    def run(self) -> None:
        """Main voice assistant loop"""
        self.speak("Friday voice assistant activated! I'm powered by Llama2 AI and completely voice operated.")
        self.speak("Say 'Friday' to get my attention, then speak your command.")
        
        while self.is_listening:
            try:
                # Listen for wake word
                print("🔍 Waiting for wake word 'Friday'...")
                wake_word = self.listen(timeout=10)
                
                if wake_word == "timeout":
                    continue
                    
                if "friday" in wake_word:
                    self.speak("Yes boss, I'm listening!")
                    
                    # Listen for command
                    command = self.listen(timeout=15)
                    
                    if command and command != "timeout":
                        result = self.handle_voice_command(command)
                        
                        if result == "exit":
                            break
                        elif result == "sleep":
                            # Wait for wake word again
                            continue
                    else:
                        self.speak("I'm ready when you are. Just say something!")
                
            except KeyboardInterrupt:
                self.speak("Shutting down Friday assistant. Goodbye!")
                break
            except sr.RequestError as e:
                print(f"Speech service error: {e}")
                self.speak("Speech recognition service is having issues. Please check your internet connection.")
                time.sleep(2)
            except Exception as e:
                print(f"Error: {e}")
                self.speak("I encountered an error, but I'm still here to help!")
                time.sleep(1)


def main() -> None:
    """Main entry point"""
    print("🤖 Starting Llama2-Powered Voice Friday Assistant...")
    print("📋 Setup Requirements:")
    print("   1. Install: pip install SpeechRecognition gtts playsound==1.2.2 pyautogui")
    print("   2. Install: pip install wikipedia requests ollama")
    print("   3. For AI features - Install Ollama: https://ollama.ai/")
    print("   4. For AI features - Pull Llama2: ollama pull llama2")
    print("   5. For AI features - Start Ollama: ollama serve")
    print("   6. Optional: Get weather API key from openweathermap.org")
    print("\n🎯 This assistant is entirely voice-operated!")
    print("💡 Say 'Friday' to activate, then speak your command")
    print("🔊 Everything is handled through voice - no typing needed!")
    print("⚠️  If some packages are missing, basic functions will still work!")
    print("\n" + "="*50)
    
    # Check for microphone permissions and speech recognition
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Microphone test: OK")
            # Test speech recognition methods
            if hasattr(r, 'recognize_google'):
                print("✅ Google Speech Recognition: Available")
            else:
                print("⚠️ Google Speech Recognition: Not available")
    except ImportError:
        print("⚠️ SpeechRecognition module not properly imported")
    except Exception as e:
        print(f"⚠️ Microphone issue: {e}")
        print("   Solutions:")
        print("   - Install: pip install pyaudio")
        print("   - On Windows: pip install pipwin && pipwin install pyaudio")
        print("   - Check microphone permissions in Windows settings")
    
    try:
        assistant = VoiceFridayAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Assistant stopped by user")
    except Exception as e:
        print(f"❌ Failed to start assistant: {e}")
        print("The assistant will work with limited features if some packages are missing.")


if __name__ == "__main__":
    main()
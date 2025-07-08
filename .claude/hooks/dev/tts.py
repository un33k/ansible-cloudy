import os
from typing import Optional, List, Dict, Literal
from abc import ABC, abstractmethod
from dotenv import load_dotenv


VoiceGender = Literal["male", "female"]
TTS_ProviderPriority = Literal["elevenlabs", "openai", "pyttsx3"]

# Default TTS provider priority - change this to adjust the default order
DEFAULT_TTS_PRIORITY: List[TTS_ProviderPriority] = ["elevenlabs", "openai", "pyttsx3"]

class TTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    def __init__(self, api_key: Optional[str] = None, voice_gender: VoiceGender = "female"):
        self.api_key = api_key
        self.voice_gender = voice_gender
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available"""
        pass
        
    @abstractmethod
    def speak(self, text: str) -> bool:
        """Speak the given text"""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider using Turbo v2.5"""
    
    @property
    def name(self) -> str:
        return "ElevenLabs"
    
    # Voice IDs for different genders
    VOICE_IDS = {
        "male": "ErXwobaYiN019PkySvjV",  # Antoni
        "female": "WejK3H1m7MI9CHnIjW9K"  # Default female voice
    }
    
    def is_available(self) -> bool:
        """Check if ElevenLabs is available"""
        if not self.api_key:
            return False
        try:
            import elevenlabs
            return True
        except ImportError:
            return False
            
    def speak(self, text: str) -> bool:
        """Speak text using ElevenLabs"""
        try:
            from elevenlabs.client import ElevenLabs
            from elevenlabs import play
            
            client = ElevenLabs(api_key=self.api_key)
            voice_id = self.VOICE_IDS.get(self.voice_gender, self.VOICE_IDS["female"])
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_turbo_v2_5",
                output_format="mp3_44100_128",
            )
            play(audio)
            return True
        except Exception as e:
            print(f"ElevenLabs error: {e}")
            return False


class OpenAIProvider(TTSProvider):
    """OpenAI TTS provider"""
    
    @property
    def name(self) -> str:
        return "OpenAI"
    
    # Voice names for different genders
    VOICES = {
        "male": "onyx",  # Male voice
        "female": "nova"  # Female voice
    }
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        if not self.api_key:
            return False
        try:
            import openai
            return True
        except ImportError:
            return False
            
    def speak(self, text: str) -> bool:
        """Speak text using OpenAI"""
        try:
            import asyncio
            return asyncio.run(self._async_speak(text))
        except Exception as e:
            print(f"OpenAI error: {e}")
            return False
            
    async def _async_speak(self, text: str) -> bool:
        """Async implementation of OpenAI TTS"""
        try:
            from openai import AsyncOpenAI
            from openai.helpers import LocalAudioPlayer
            
            client = AsyncOpenAI(api_key=self.api_key)
            voice = self.VOICES.get(self.voice_gender, self.VOICES["female"])
            async with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=text,
                instructions="Speak in a cheerful, positive yet professional tone.",
                response_format="mp3",
            ) as response:
                await LocalAudioPlayer().play(response)
            return True
        except Exception:
            return False


class Pyttsx3Provider(TTSProvider):
    """Offline TTS provider using pyttsx3"""
    
    @property
    def name(self) -> str:
        return "pyttsx3"
    
    def __init__(self, voice_gender: VoiceGender = "female"):
        super().__init__(api_key=None, voice_gender=voice_gender)
        
    def is_available(self) -> bool:
        """Check if pyttsx3 is available"""
        try:
            import pyttsx3
            return True
        except ImportError:
            return False
            
    def speak(self, text: str) -> bool:
        """Speak text using pyttsx3"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 0.8)
            
            # Try to set voice based on gender preference
            voices = engine.getProperty('voices')
            if voices:
                # Look for male/female voice
                for voice in voices:
                    if self.voice_gender == "male" and "male" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                    elif self.voice_gender == "female" and "female" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 error: {e}")
            return False


class TTSLoader:
    """Loads and manages TTS providers based on priority"""
    
    def __init__(self, priority: Optional[List[TTS_ProviderPriority]] = None, voice_gender: VoiceGender = "female"):
        """
        Initialize the TTS loader
        
        Args:
            priority: List of provider names in order of preference.
                     Default: ['elevenlabs', 'openai', 'pyttsx3']
            voice_gender: Voice gender preference ('male' or 'female')
        """
        load_dotenv()
        
        self.voice_gender = voice_gender
        self.providers: Dict[str, TTSProvider] = {
            'elevenlabs': ElevenLabsProvider(os.getenv('ELEVENLABS_API_KEYS'), voice_gender),
            'openai': OpenAIProvider(os.getenv('OPENAI_API_KEY'), voice_gender),
            'pyttsx3': Pyttsx3Provider(voice_gender)
        }
        
        self.priority = priority or DEFAULT_TTS_PRIORITY
        
    def get_provider(self) -> Optional[TTSProvider]:
        """
        Get the first available TTS provider based on priority
        
        Returns:
            TTSProvider instance or None if no provider is available
        """
        for provider_name in self.priority:
            provider = self.providers.get(provider_name.lower())
            if provider and provider.is_available():
                return provider
        return None
        
    def list_available(self) -> List[str]:
        """List all available providers"""
        available = []
        for name, provider in self.providers.items():
            if provider.is_available():
                available.append(name)
        return available
        
    def speak(self, text: str, provider_name: Optional[str] = None) -> bool:
        """
        Speak the given text using specified or best available provider
        
        Args:
            text: Text to speak
            provider_name: Optional specific provider to use
            
        Returns:
            True if successful, False otherwise
        """
        if provider_name:
            provider = self.providers.get(provider_name.lower())
            if provider and provider.is_available():
                return provider.speak(text)
            return False
            
        provider = self.get_provider()
        if provider:
            return provider.speak(text)
        return False


def load_tts(priority: Optional[List[TTS_ProviderPriority]] = None, voice_gender: VoiceGender = "female") -> TTSLoader:
    """
    Factory function to create a TTSLoader instance
    
    Args:
        priority: Optional list of provider names in order of preference
        voice_gender: Voice gender preference ('male' or 'female')
        
    Returns:
        Configured TTSLoader instance
    """
    return TTSLoader(priority, voice_gender)


if __name__ == "__main__":
    """Command line interface for TTS"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tts.py <text>")
        sys.exit(1)
    
    text = " ".join(sys.argv[1:])
    tts = load_tts()
    
    if not tts.speak(text):
        sys.exit(1)
    
    sys.exit(0)
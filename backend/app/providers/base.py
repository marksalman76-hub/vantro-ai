# Provider base classes

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional

class ProviderCategory(str, Enum):
    """Provider categories"""
    AVATAR_VIDEO = "avatar_video"      # Synthesia, HeyGen
    VOICE = "voice"                    # ElevenLabs, Google TTS
    TEXT_TO_VIDEO = "text_to_video"    # Pika, Runway
    MUSIC = "music"                    # Mubert, AIVA
    CAPTIONS = "captions"              # AssemblyAI, Google
    COMPOSITION = "composition"        # Shotstack, FFmpeg

class ProviderStatus(str, Enum):
    """Provider readiness status"""
    ACTIVE = "active"
    TEST_MODE = "test_mode"
    API_KEY_PENDING = "api_key_pending"
    DISABLED = "disabled"
    FAILED = "failed"

class BaseProvider(ABC):
    """Base provider class"""

    def __init__(self, name: str, category: ProviderCategory, status: ProviderStatus):
        self.name = name
        self.category = category
        self.status = status
        self.api_key = None

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute provider request"""
        pass

    @abstractmethod
    def estimate_cost(self, **kwargs) -> float:
        """Estimate cost in credits"""
        pass

    def set_api_key(self, api_key: str):
        """Set API key for provider"""
        self.api_key = api_key
        self.status = ProviderStatus.ACTIVE

    def is_ready(self) -> bool:
        """Check if provider is ready to use"""
        return self.status == ProviderStatus.ACTIVE and self.api_key is not None

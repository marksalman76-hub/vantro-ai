# AssemblyAI provider adapter

from ..base import BaseProvider, ProviderCategory, ProviderStatus

class AssemblyAIProvider(BaseProvider):
    """AssemblyAI captions provider"""

    def __init__(self):
        super().__init__(
            name="assemblyai",
            category=ProviderCategory.CAPTIONS,
            status=ProviderStatus.API_KEY_PENDING
        )

    async def execute(self, **kwargs) -> dict:
        """Generate captions with AssemblyAI"""
        if not self.is_ready():
            return {"error": "AssemblyAI API key not configured"}

        return {"status": "mock_response", "captions_url": "https://mock.assemblyai.io/captions.vtt"}

    def estimate_cost(self, duration_seconds: int = 120, **kwargs) -> float:
        """Estimate cost in credits"""
        # AssemblyAI: $0.015 per minute
        minutes = duration_seconds / 60
        return minutes * 1.5

import os
import tempfile
from openai import OpenAI

from .audio_player import play_audio


class OpenRouterTTS:
    """A class for interacting with TTS via OpenRouter.

    Synthesises text into speech using xAI's Grok Voice TTS model and
    plays the resulting audio via ``afplay`` with optional progress
    reporting.
    """

    MAX_TEXT_LENGTH = 15000

    def __init__(
        self,
        api_key=None,
        model="x-ai/grok-voice-tts-1.0",
        voice="Eve",
    ):
        """Initialise the OpenRouterTTS instance.

        Args:
            api_key: OpenRouter API key.
            model: TTS model identifier.
                Defaults to ``x-ai/grok-voice-tts-1.0``.
            voice: Voice preset name. Defaults to ``Eve``.
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        self.voice = voice

    def speak(self, text, progress_callback=None):
        """Synthesise text into speech, play it aloud, and delete the temp file.

        Args:
            text: The text to be synthesised into speech.
            progress_callback: Optional callable that accepts an integer
                percentage (0--99) during playback.

        Raises:
            Exception: If the API call or playback fails.
        """
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[: self.MAX_TEXT_LENGTH]

        temp_path = None
        try:
            with self.client.audio.speech.with_streaming_response.create(
                extra_headers={
                    "HTTP-Referer":       "https://github.com/thaikolja/dropzone-ai-reader",
                    "X-Title":            "Dropzone AI Reader",
                },
                model=self.model,
                voice=self.voice,
                input=text,
                response_format="mp3",
            ) as response:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    temp_path = f.name

                response.stream_to_file(temp_path)

            play_audio(temp_path, progress_callback=progress_callback)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

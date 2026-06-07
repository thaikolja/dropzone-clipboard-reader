import os
import tempfile
from groq import Groq

from .audio_player import play_audio
from action import GROQ_VOICE


class GroqTTS:
    """A class for interacting with the Groq Text-to-Speech (TTS) API.

    Synthesises text into speech using the Orpheus model and plays
    the resulting audio via ``afplay`` with optional progress reporting.
    """

    MAX_TEXT_LENGTH = 200

    def __init__(
        self,
        api_key=None,
        model="canopylabs/orpheus-v1-english",
        voice=str(GROQ_VOICE),
    ):
        """Initialise the GroqTTS instance.

        Args:
            api_key: Groq API key.
            model: TTS model identifier.
                Defaults to ``canopylabs/orpheus-v1-english``.
            voice: Voice preset name. Defaults to ``troy``.
        """
        self.client = Groq(api_key=api_key)
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
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format="wav",
            )

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            response.write_to_file(temp_path)

            play_audio(temp_path, progress_callback=progress_callback)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

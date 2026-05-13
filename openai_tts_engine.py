import os
import subprocess
import tempfile
import time

from openai import OpenAI


class OpenAITTS:
    """
    A class for interacting with the OpenAI Text-to-Speech (TTS) API (via OpenRouter)
    to synthesize and play audio.

    This class provides methods to initialize the OpenAI client, synthesize text into
    speech using a specified model and voice, and play the resulting audio. It also
    supports progress reporting during audio playback on macOS using `afplay` and `afinfo`.
    """

    def __init__(
        self,
        api_key=None,
        model: str = "openai/gpt-4o-mini-tts-2025-12-15",
        voice: str = "alloy",
    ):
        """Initialise the OpenAITTS instance with authentication and model configuration.

        Args:
            api_key: OpenRouter API key. Falls back to a default if not provided.
            model: The TTS model identifier to use for speech synthesis.
                Defaults to ``openai/gpt-4o-mini-tts-2025-12-15``.
            voice: The voice preset name for speech output.
                Defaults to ``alloy``.
        """
        # Accept an API key directly
        self.api_key = api_key

        # Create the OpenAI client with the resolved API key and OpenRouter base URL
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )

        # Store the TTS model ID and voice preset
        self.model = model
        self.voice = voice

    def speak(self, text, progress_callback=None):
        """Synthesise text into speech, play it aloud and report playback progress.

        Generates an MP3 audio file from the input text via the OpenAI TTS API,
        saves it to a temporary location, determines its duration with ``afinfo``,
        then plays it using ``afplay``. If a progress callback is supplied the
        method polls playback progress every 100 ms and reports it as a
        percentage from 0 to 99. The temporary MP3 file is always deleted after
        playback finishes.

        Args:
            text: The text to be synthesised into speech.
            progress_callback: An optional callable that accepts an integer
                percentage (0--99) and is invoked periodically during playback.
        """
        # Generate an audio stream from the input text using OpenAI's TTS API
        with self.client.audio.speech.with_streaming_response.create(
            extra_headers={
                "HTTP-Referer":       "https://github.com/thaikolja/dropzone-ai-reader",
                "X-OpenRouter-Title": "Dropzone AI Reader",
            },
            model=self.model,
            voice=self.voice,
            input=text,
            response_format="mp3"
        ) as response:
            # Write the binary MP3 data to a temporary file on disk
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            # Persist the API response to the temp file
            response.stream_to_file(temp_path)

        duration = None

        # Use afinfo (macOS built-in) to read the estimated duration in seconds
        try:
            output = subprocess.check_output(["afinfo", temp_path], text=True)
            for line in output.splitlines():
                if "estimated duration" in line:
                    duration = float(line.split(":")[-1].strip().split()[0])
                    break
        except Exception:
            pass

        if duration and duration > 0 and progress_callback:
            # Launch afplay as a background process so we can poll progress
            proc = subprocess.Popen(["afplay", temp_path])
            start = time.time()

            while proc.poll() is None:
                elapsed = time.time() - start
                percent = min(int((elapsed / duration) * 100), 99)
                progress_callback(percent)
                time.sleep(0.1)

            proc.wait()
        else:
            # Fall back to blocking playback
            subprocess.run(["afplay", temp_path])

        # Always clean up the temporary MP3 file
        os.unlink(temp_path)

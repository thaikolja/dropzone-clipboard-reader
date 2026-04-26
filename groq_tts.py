import os
import subprocess
import tempfile
import time

from groq import Groq


class GroqTTS:
    """
    A class for interacting with the Groq Text-to-Speech (TTS) API to synthesize and play audio.

    This class provides methods to initialize the Groq client, synthesize text into
    speech using a specified model and voice, and play the resulting audio. It also
    supports progress reporting during audio playback on macOS using `afplay` and `afinfo`.
    """

    def __init__(
        self,
        api_key=None,
        model: str = "canopylabs/orpheus-v1-english",
        voice: str = "troy",
    ):
        """Initialise the GroqTTS instance with authentication and model configuration.

        Args:
            api_key: Groq API key. Falls back to the GROQ_API_KEY environment
                variable if not provided.
            model: The TTS model identifier to use for speech synthesis.
                Defaults to ``canopylabs/orpheus-v1-english``.
            voice: The voice preset name for speech output.
                Defaults to ``troy``.
        """
        # Accept an API key directly or fall back to the environment variable
        # GROQ_API_KEY is used when calling from outside Dropzone (e.g., CLI tests)
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")

        # Create the Groq client with the resolved API key
        self.client = Groq(api_key=self.api_key)

        # Store the TTS model ID (canopylabs/orpheus-v1-english) and voice preset
        self.model = model
        self.voice = voice

    def speak(self, text, progress_callback=None):
        """Synthesise text into speech, play it aloud and report playback progress.

        Generates a WAV audio file from the input text via the Groq TTS API,
        saves it to a temporary location, determines its duration with ``afinfo``,
        then plays it using ``afplay``. If a progress callback is supplied the
        method polls playback progress every 100 ms and reports it as a
        percentage from 0 to 99. The temporary WAV file is always deleted after
        playback finishes.

        Args:
            text: The text to be synthesised into speech.
            progress_callback: An optional callable that accepts an integer
                percentage (0--99) and is invoked periodically during playback.
        """
        # Generate a WAV audio buffer from the input text using Groq's TTS API
        response = self.client.audio.speech.create(
            model=self.model, voice=self.voice, input=text, response_format="wav"
        )

        # Write the binary WAV data to a temporary file on disk
        # delete=False keeps the file around so afplay can read it
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        # Persist the API response (streamed or buffered) to the temp file
        response.write_to_file(temp_path)

        duration = None

        # Use afinfo (macOS built-in) to read the estimated duration in seconds
        # This allows us to report real playback progress via the callback
        try:
            output = subprocess.check_output(["afinfo", temp_path], text=True)
            for line in output.splitlines():
                if "estimated duration" in line:
                    # Extract "5.234" from "estimated duration: 5.234 sec"
                    duration = float(line.split(":")[-1].strip().split()[0])
                    break
        except Exception:
            # If afinfo fails or is unavailable, fall back to blocking playback
            pass

        if duration and duration > 0 and progress_callback:
            # Launch afplay as a background process so we can poll progress
            proc = subprocess.Popen(["afplay", temp_path])

            # Track elapsed time since playback started
            start = time.time()

            # Loop until afplay exits
            while proc.poll() is None:
                elapsed = time.time() - start

                # Calculate percentage complete, capped at 99 (dz.percent expects 0-100)
                percent = min(int((elapsed / duration) * 100), 99)

                # Notify Dropzone of the current progress
                progress_callback(percent)

                # Poll every 100ms to keep CPU usage low
                time.sleep(0.1)

            # Ensure the process has fully exited before cleaning up
            proc.wait()
        else:
            # Fall back to blocking playback (no progress reporting)
            subprocess.run(["afplay", temp_path])

        # Always clean up the temporary WAV file
        os.unlink(temp_path)

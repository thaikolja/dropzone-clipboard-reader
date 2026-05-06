# Dropzone Action Info
# Name:                 Clipboard AI Reader
# Description:          Reads text aloud using Groq or OpenAI TTS API
# Handles:              Files, Text
# Creator:              Kolja Nolte
# URL:                  https://github.com/thaikolja/dropzone-ai-clipboard-reader
# Events:               Clicked, Dragged
# KeyModifiers:         Command, Option, Control, Shift
# SkipConfig:           Yes
# RunsSandboxed:        Yes
# Version:              1.0.0
# MinDropzoneVersion:   4.0
# PythonPath:           venv/bin/python3

import os
import subprocess

from openai_tts_engine import OpenAITTS
from groq_tts_engine import GroqTTS

GROQ_VOICE = "troy"
OPENAI_VOICE = "alloy"


def _setup_config():
    """Show Pashua dialog to configure API keys and provider."""
    groq_key = os.environ.get('groq_api_key', '')
    openai_key = os.environ.get('openai_api_key', '')
    provider = os.environ.get('provider', 'Groq')

    config = f"""
    *.title = Clipboard AI Reader Configuration
    i.type = text
    i.text = This action can use either the Groq or OpenAI text-to-speech API. Please provide at lest one API key and select the provider you want to use.
    i.width = 400
    g.type = password
    g.label = Groq API Key for TTS
    g.default = {groq_key}
    g.width = 400
    o.type = password
    o.label = OpenAI API Key for TTS
    o.default = {openai_key}
    o.width = 400
    p.type = radiobutton
    p.label = Select the provider you want to use for text-to-speech synthesis:
    p.option = Groq
    p.option = OpenAI
    p.default = {provider}
    cb.type = cancelbutton
    db.type = defaultbutton
    """
    result = dz.pashua(config)

    if result.get('cb') == '1':
        return None

    dz.save_value('groq_api_key', result['g'])
    dz.save_value('openai_api_key', result['o'])
    dz.save_value('provider', result['p'])

    return result


def _get_config():
    """Retrieve configuration, prompting if necessary or if Command is held."""
    # Check if Command key is held to force re-configuration
    if os.environ.get('KEY_MODIFIERS') == 'Command':
        return _setup_config()

    groq_key = os.environ.get('groq_api_key')
    openai_key = os.environ.get('openai_api_key')
    provider = os.environ.get('provider')

    # If configuration is missing, prompt for it
    if not provider or (provider == 'Groq' and not groq_key) or (provider == 'OpenAI' and not openai_key):
        return _setup_config()

    return {
        'g': groq_key,
        'o': openai_key,
        'p': provider
    }


def _text_for_path(path):
    """Resolve a file path to the text that should be spoken aloud.

    ``.txt`` and ``.md`` files are read in full and their content is returned.
    All other file types return only the file name (without the directory
    portion).

    Args:
        path: Absolute or relative file path on disk.

    Returns:
        The file content (for ``.txt`` / ``.md``) or the base file name.
    """
    # Determine the file extension and normalise it to lowercase
    ext = os.path.splitext(path)[1].lower()

    # For plain-text and Markdown files, read and return the full content
    if ext in (".txt", ".md"):
        with open(path, "r") as f:
            return f.read()

    # For all other file types, speak only the filename (not the full path)
    return os.path.basename(path)


def _speak_text(text, config):
    """Synthesise text to speech and play it with a determinate progress bar.

    Args:
        text: The text string to be spoken aloud.
        config: Configuration dictionary with provider and API keys.
    """
    # Guard against empty or whitespace-only input
    if not text or not text.strip():
        dz.finish("No text provided")
        return

    provider = config['p']
    if provider == 'Groq':
        api_key = config['g']
        if not api_key:
            dz.fail("Groq API key not configured")
            return
        tts = GroqTTS(api_key=api_key, voice=GROQ_VOICE)
    else:
        api_key = config['o']
        if not api_key:
            dz.fail("OpenAI API key not configured")
            return
        tts = OpenAITTS(api_key=api_key, voice=OPENAI_VOICE)

    # Show an initial status message in the Dropzone grid
    dz.begin(f"Generating speech ({provider})...")

    # Enable the determinate progress bar so we can report playback progress
    dz.determinate(True)

    # Generate the audio and play it, updating the progress bar as playback advances
    tts.speak(text, progress_callback=lambda p: dz.percent(p))

    # Signal that the task finished successfully and remove the progress bar
    dz.url("")
    dz.finish("Done!")


def dragged():
    """Handle a drag-and-drop event from the Dropzone grid."""
    config = _get_config()
    if not config:
        dz.fail("Configuration required")
        return

    # Determine what was dropped: files or a text string
    dragged_type = os.environ.get("dragged_type", "text")

    if dragged_type == "files":
        text = " ".join(_text_for_path(p) for p in items)
    else:
        text = " ".join(items) if isinstance(items, list) else str(items)

    _speak_text(text, config)


def clicked():
    """Handle a click event on the action in the Dropzone grid."""
    config = _get_config()
    if not config:
        dz.fail("Configuration required")
        return

    # Fetch the current clipboard contents
    text = subprocess.check_output(["pbpaste"], text=True).strip()

    if not text:
        dz.finish("Clipboard is empty")
        return

    if os.path.isfile(text):
        text = _text_for_path(text)

    _speak_text(text, config)

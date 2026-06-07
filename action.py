# Dropzone Action Info
# Name:                 Clipboard Reader
# Description:          Reads text aloud using Groq or xAI TTS via OpenRouter
# Handles:              Files, Text
# Creator:              Kolja Nolte
# URL:                  https://github.com/thaikolja/dropzone-ai-clipboard-reader
# Events:               Clicked, Dragged
# KeyModifiers:         Command, Option, Control, Shift
# SkipConfig:           Yes
# RunsSandboxed:        Yes
# Version:              1.4.0
# MinDropzoneVersion:   4.0
# PythonPath:           venv/bin/python3

import os
import subprocess

from src.groq_engine import GroqTTS
from src.openrouter_engine import OpenRouterTTS

GROQ_VOICE = "troy" # Groq's TTS voice for general use (limited)
OPENROUTER_VOICE = "Rex" # xAI's TTS voice available via OpenRouter


def _setup_config():
    """Show Pashua dialog to configure API keys and provider."""
    groq_key = os.environ.get("groq_api_key", "")
    openrouter_key = os.environ.get("openai_api_key", "")
    provider = os.environ.get("provider", "Groq")
    # Map legacy "OpenAI" provider to "xAI" for backward compat
    display_provider = "xAI" if provider in ("OpenAI", "xAI") else provider

    config = f"""
    *.title = Clipboard AI Reader Configuration
    i.type = text
    i.text = This action can use either the Groq Orpheus or xAI Grok Voice text-to-speech API. Please provide at least one API key and select the provider you want to use.
    i.width = 400
    g.type = password
    g.label = Groq API Key for TTS
    g.default = {groq_key}
    g.width = 400
    o.type = password
    o.label = OpenRouter API Key (for xAI)
    o.default = {openrouter_key}
    o.width = 400
    p.type = radiobutton
    p.label = Select the provider you want to use for text-to-speech synthesis:
    p.option = Groq
    p.option = xAI
    p.default = {display_provider}
    cb.type = cancelbutton
    db.type = defaultbutton
    """
    result = dz.pashua(config)

    if result.get("cb") == "1":
        return None

    dz.save_value("groq_api_key", result["g"])
    dz.save_value("openai_api_key", result["o"])
    dz.save_value("provider", result["p"])

    return result


def _get_config():
    """Retrieve configuration, prompting if necessary or if Command is held."""
    # Check if Command key is held to force re-configuration
    if os.environ.get("KEY_MODIFIERS") == "Command":
        return _setup_config()

    groq_key = os.environ.get("groq_api_key")
    openrouter_key = os.environ.get("openai_api_key")
    provider = os.environ.get("provider")

    # If configuration is missing, prompt for it
    if (
        not provider
        or (provider == "Groq" and not groq_key)
        or (provider in ("xAI", "OpenAI") and not openrouter_key)
    ):
        return _setup_config()

    return {"g": groq_key, "o": openrouter_key, "p": provider}


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
    ext = os.path.splitext(path)[1].lower()

    if ext in (".txt", ".md"):
        try:
            with open(path, "r", errors="replace") as f:
                content = f.read()
            return content if content.strip() else os.path.basename(path)
        except (OSError, PermissionError):
            return os.path.basename(path)

    return os.path.basename(path)


def _speak_text(text, config):
    """Synthesise text to speech and play it with a determinate progress bar.

    Args:
        text: The text string to be spoken aloud.
        config: Configuration dictionary with provider and API keys.
    """
    if not text or not text.strip():
        dz.finish("No text provided")
        return

    provider = config["p"]
    if provider == "Groq":
        api_key = config["g"]
        if not api_key:
            dz.fail("Groq API key not configured")
            return
        tts = GroqTTS(api_key=api_key, voice=GROQ_VOICE)
    else:
        # Handles both "xAI" (new) and "OpenAI" (legacy) provider values
        api_key = config["o"]
        if not api_key:
            dz.fail("OpenRouter API key not configured")
            return
        tts = OpenRouterTTS(api_key=api_key, voice=OPENROUTER_VOICE)

    dz.begin(f"Generating speech ({provider})...")
    dz.determinate(True)

    try:
        tts.speak(text, progress_callback=lambda p: dz.percent(p))
    except Exception as e:
        dz.fail(f"Speech synthesis failed: {e}")
        return

    dz.url("")
    dz.finish("Done!")


def dragged():
    """Handle a drag-and-drop event from the Dropzone grid."""
    config = _get_config()
    if not config:
        dz.fail("Configuration required")
        return

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

    try:
        text = subprocess.check_output(["pbpaste"], text=True).strip()
    except (subprocess.CalledProcessError, OSError):
        dz.fail("Failed to read clipboard")
        return

    if not text:
        dz.finish("Clipboard is empty")
        return

    if os.path.isfile(text):
        text = _text_for_path(text)

    _speak_text(text, config)

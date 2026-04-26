# Dropzone Action Info
# Name:                 Groq Reader
# Description:          Reads text aloud using Groq's Orpheus TTS API
# Handles:              Files, Text
# Creator:              Kolja Nolte
# URL:                  https://github.com/thaikolja/dropzone-groq-reader
# Events:               Clicked, Dragged
# KeyModifiers:         Command, Option, Control, Shift
# SkipConfig:           No
# RunsSandboxed:        Yes
# Version:              1.0.0
# MinDropzoneVersion:   4.0
# OptionsNIB:           APIKey
# PythonPath:           venv/bin/python3

import os
import subprocess

from groq_tts import GroqTTS

VOICE = "troy"


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


def _speak_text(text, api_key):
    """Synthesise text to speech and play it with a determinate progress bar.

    Sets up the Dropzone grid status, creates a ``GroqTTS`` instance with the
    provided API key, and delegates to ``GroqTTS.speak()`` with a progress
    callback that updates the Dropzone progress bar.

    Args:
        text: The text string to be spoken aloud.
        api_key: A valid Groq API key for the TTS request.
    """
    # Guard against empty or whitespace-only input
    if not text or not text.strip():
        dz.finish("No text provided")
        return

    # Show an initial status message in the Dropzone grid
    dz.begin("Generating speech...")

    # Enable the determinate progress bar so we can report playback progress
    dz.determinate(True)

    # Create a TTS instance with the API key provided by the OptionsNIB
    tts = GroqTTS(api_key=api_key, voice=VOICE)

    # Generate the audio and play it, updating the progress bar as playback advances
    tts.speak(text, progress_callback=lambda p: dz.percent(p))

    # Signal that the task finished successfully and remove the progress bar
    dz.url("")
    dz.finish("Done!")


def dragged():
    """Handle a drag-and-drop event from the Dropzone grid.

    Triggered when the user drops files or text onto the action.  The dragged
    type is read from the ``dragged_type`` environment variable set by
    Dropzone.  Files are resolved via ``_text_for_path``, text strings are
    joined and passed directly to ``_speak_text``.

    Globals:
        items: List of dragged file paths or text strings, provided by
            Dropzone.
    """
    # Retrieve the Groq API key that was entered via the OptionsNIB panel
    api_key = os.environ.get(key="api_key")

    # Abort with a failure notification if no key was configured
    if not api_key:
        dz.fail("No API key configured")
        return

    # Determine what was dropped: files or a text string
    # Dropzone sets this environment variable automatically
    dragged_type = os.environ.get("dragged_type", "text")

    if dragged_type == "files":
        # For each dropped file, convert it to text (content for .txt/.md, name otherwise)
        # Join multiple files with a space so they are read in sequence
        text = " ".join(_text_for_path(p) for p in items)
    else:
        # Text drops come in as a list of strings; join them into a single string
        text = " ".join(items) if isinstance(items, list) else str(items)

    # Delegate to the shared speak helper
    _speak_text(text, api_key)


def clicked():
    """Handle a click event on the action in the Dropzone grid.

    Reads the current clipboard contents via ``pbpaste`` (macOS built-in).
    If the clipboard holds a file path, the path is resolved via
    ``_text_for_path``.  Otherwise the raw clipboard text is spoken aloud.
    """
    # Retrieve the Groq API key that was entered via the OptionsNIB panel
    api_key = os.environ.get("api_key")

    # Abort with a failure notification if no key was configured
    if not api_key:
        dz.fail("No API key configured")
        return

    # Fetch the current clipboard contents using pbpaste (macOS built-in)
    text = subprocess.check_output(["pbpaste"], text=True).strip()

    # Abort early if the clipboard is empty
    if not text:
        dz.finish("Clipboard is empty")
        return

    # If the clipboard contains a file path, resolve it via _text_for_path
    # e.g. /Users/name/Documents/notes.txt → file content
    # e.g. /Users/name/Photo.jpg           → "Photo.jpg"
    if os.path.isfile(text):
        text = _text_for_path(text)

    # Delegate to the shared speak helper
    _speak_text(text, api_key)

# AGENTS.md — Dropzone Clipboard Reader

## Architecture

This is a **Dropzone 4 action** (`.dzbundle`). Dropzone loads it and calls event handlers at runtime.

- **Entry point**: `action.py` — the header comment block (lines 1–13) is Dropzone's declarative config. Do not change it lightly; it controls events, key modifiers, sandboxing, and the Python interpreter path.
- **TTS engines** live in `src/`:
  - `src/groq_engine.py` — Groq Orpheus TTS (WAV output)
  - `src/openrouter_engine.py` — xAI Grok Voice TTS via OpenRouter (MP3 output)
- **Shared playback**: `src/audio_player.py` handles `afplay`/`afinfo`/progress polling, shared by both engines.

## Runtime model (Dropzone-injected globals)

These are **not imported** — Dropzone provides them at runtime:

- `dz` — Dropzone API object (`.pashua()`, `.save_value()`, `.begin()`, `.finish()`, `.fail()`, `.percent()`, `.determinate()`, `.url()`)
- `items` — list of dropped items (files or text), available inside `dragged()`
- `os.environ["dragged_type"]` — `"files"` or `"text"` depending on what was dropped
- `os.environ["KEY_MODIFIERS"]` — e.g. `"Command"` when ⌘ is held

## Configuration

- Uses **Pashua** (a macOS dialog tool built into Dropzone) for the config UI, called via `dz.pashua()`.
- API keys and provider choice are persisted through Dropzone's `dz.save_value()` / `os.environ.get()` mechanism (not `.env` files).
- Hold **⌘ (Command)** while clicking/dropping to force the config dialog to re-appear.
- `# SkipConfig: Yes` in the header tells Dropzone to skip its built-in config UI — the action handles it all in `_setup_config()`.
- The "xAI" provider routes through **OpenRouter** (`x-ai/grok-voice-tts-1.0` model, $15/M chars).
- The "Groq" provider uses **Groq Orpheus** (`canopylabs/orpheus-v1-english`, $22/M chars).

## Dev setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install openai groq
```

- The header `# PythonPath: venv/bin/python3` tells Dropzone to use the bundled venv at runtime. Keep dependencies installed there.
- No tests, no CI, no lint/typecheck config exists.

## macOS dependencies

The action relies on these built-in macOS CLI tools:
- `afplay` — audio playback
- `afinfo` — audio duration detection
- `pbpaste` — read clipboard (used in `clicked()`)

## Audio playback progress

The determinate progress bar (0–99%) works by polling `afplay` playback time against the estimated duration from `afinfo`. The progress callback is wired via `dz.percent()` → `dz.determinate(True)` in `action.py:_speak_text()`.

## Error handling

- Both TTS engines catch API errors and clean up temporary files before re-raising.
- `action.py:_speak_text()` wraps the entire speak call in a try/except and calls `dz.fail()` on error.
- `_text_for_path()` handles file read errors gracefully (falls back to basename).
- `clicked()` handles `pbpaste` failures gracefully.
- `audio_player.py` ensures temporary files are always deleted (via try/finally).
- Text is truncated to 15000 characters before sending to APIs to avoid length-related failures.

# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] — 2026-06-08

### Changed

- Replaced OpenAI/Kokoro provider with **xAI Grok Voice TTS** via OpenRouter
- Renamed `OpenAITTS` → `OpenRouterTTS` class, file `src/openai_engine.py` → `src/openrouter_engine.py`
- Default voice: `Eve` (one of 5 Grok voices: Eve, Ara, Rex, Sal, Leo)
- Increased text limit from 4000 to **15000 characters** (Grok's max)
- Config dialog: "OpenAI" option → "xAI"; label updated to "OpenRouter API Key (for xAI)"

### Fixed

- Backward compatibility: legacy "OpenAI" provider value still works

## [1.3.0] — 2026-06-08

### Changed

- Restructured code into `src/` package with shared `audio_player.py` module
- Switched OpenAI provider from direct API to OpenRouter with `hexgrad/kokoro-82m` model
- Updated default voice to `af_bella` (Kokoro voice) for the OpenRouter provider
- Renamed config dialog key label to "OpenRouter API Key"

### Added

- Error handling around API calls in both TTS engines
- Graceful handling of file read errors, clipboard failures, and playback errors
- Text length limiting (4000 chars) to prevent API failures on large inputs
- Temporary file cleanup guarantee via try/finally in audio player

### Fixed

- Config dialog typo ("at lest" → "at least")
- OpenRouter HTTP header (`X-Title` replaces `X-OpenRouter-Title`)
- File reading with `errors="replace"` to handle non-UTF-8 content

## [1.2.0] — 2026-05-07

### Added

- Integrated both Groq and OpenAI TTS providers
- Custom configuration dialog via Pashua (supports multiple API keys and provider selection)
- Support for re-configuring by holding the Command key during action trigger

### Changed

- Updated action name to "AI Reader"
- Switched from built-in OptionsNIB to custom Pashua-based configuration

## [1.1.0] — 2026-05-07

### Changed

- Switched from Groq Orpheus TTS to OpenAI TTS via OpenRouter
- Updated action name to "OpenAI Reader"
- Changed audio format from WAV to MP3
- Updated default voice to "alloy"

## [1.0.0] — 2026-04-26

### Added

- Initial release
- Click action reads clipboard content via Groq Orpheus TTS
- Drag support for text, `.txt`/`.md` files (content read aloud), and other files (filename read aloud)
- Real-time progress bar during audio playback
- API key configuration via Dropzone OptionsNIB
- The temporary WAV file is cleaned up after playback

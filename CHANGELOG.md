# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

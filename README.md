# Dropzone Groq Reader

[![GitHub Release](https://img.shields.io/github/v/release/thaikolja/dropzone-groq-reader?style=flat-square)](https://github.com/thaikolja/dropzone-groq-reader/releases) [![GitHub License](https://img.shields.io/github/license/thaikolja/dropzone-groq-reader?style=flat-square)](https://github.com/thaikolja/dropzone-groq-reader/blob/main/LICENSE) [![macOS](https://img.shields.io/badge/platform-macOS-lightgrey?style=flat-square)](https://support.apple.com/macos)

**Dropzone Groq Reader** is a custom [Dropzone](https://aptonic.com) action that reads text aloud using [Groq's Orpheus TTS API](https://console.groq.com/docs/text-to-speech). Multiple languages are included and chosen automatically based on the text.

## Features

- **Click** → reads the current clipboard text aloud
- **Drag text** → drops any text selection onto the action to hear it spoken
- **Drag files** → reads `.txt` / `.md` file contents; speaks the filename for other types
- **Progress bar** → shows real-time playback progress in the Dropzone grid
- **API key prompt** → enter your Groq API key once when adding the action

## Requirements

- [Dropzone 4+](https://aptonic.com)
- A [Groq](https://console.groq.com) account with a **free** API key
- The Orpheus TTS model terms must be accepted in your Groq console

## Installation

1. Download the latest `.dzbundle` from the [releases page](https://github.com/thaikolja/dropzone-groq-reader/releases)
2. Double-click the bundle to install it in Dropzone
3. When prompted, enter your free Groq API key
4. Start dragging text or click the action to read your clipboard

## Usage

| Action | Behaviour |
|---|---|
| Click | Reads the current clipboard |
| Drop `.txt` / `.md` | Reads the file content |
| Drop any other file | Reads the file name |
| Drop text | Reads the text |

## Development

```bash
git clone https://github.com/thaikolja/dropzone-groq-reader.git
cd dropzone-groq-reader
python3 -m venv venv
./venv/bin/pip install groq
```

## Authors

* Kolja Nolte (kolja.nolte@gmail.com)

## License

[MIT](LICENSE)

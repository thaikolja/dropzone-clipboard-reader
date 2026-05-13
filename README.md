# Dropzone AI Reader

[![GitHub Release](https://img.shields.io/github/v/release/thaikolja/dropzone-clipboard-reader?style=flat-square)](https://github.com/thaikolja/dropzone-ai-reader/releases) [![GitHub License](https://img.shields.io/github/license/thaikolja/dropzone-clipboard-reader?style=flat-square)](https://github.com/thaikolja/dropzone-ai-reader/blob/main/LICENSE) [![macOS](https://img.shields.io/badge/platform-macOS-lightgrey?style=flat-square)](https://support.apple.com/macos)

<div style="text-align:center;">
    <img width="265" height="265" style="margin:auto;display:flex;" alt="Hintergrund von „logo“ entfernt" src="https://github.com/user-attachments/assets/fc7e3176-2e06-43a3-84ca-a3e369e2119b" />
</div>

---

**Dropzone AI Reader** is a custom [Dropzone](https://aptonic.com) action that reads text aloud using either Groq or OpenAI's TTS API.

## Features

- **Click** → reads the current clipboard text aloud
- **Drag text** → drops any text selection onto the action to hear it spoken
- **Drag files** → reads `.txt` / `.md` file contents; speaks the filename for other types
- **Progress bar** → shows real-time playback progress in the Dropzone grid
- **Multi-provider support** → Choose between Groq and OpenAI
- **Custom configuration** → Enter both API keys and switch providers easily

## Requirements

- [Dropzone 4+](https://aptonic.com)
- A [Groq](https://console.groq.com) account and/or an [OpenRouter](https://openrouter.ai) account with API keys

## Installation

1. Download the latest `.dzbundle` from the [releases page](https://github.com/thaikolja/dropzone-ai-reader/releases)
2. Double-click the bundle to install it in Dropzone
3. On first use, a configuration dialog will appear to enter your API keys and select a provider
4. To change configuration later, hold the **Command (⌘)** key while clicking or dragging items onto the action

## Usage

| Action              | Behaviour                   |
|---------------------|-----------------------------|
| Click               | Reads the current clipboard |
| Drop `.txt` / `.md` | Reads the file content      |
| Drop any other file | Reads the file name         |
| Drop text           | Reads the text              |
| ⌘ + Click/Drop      | Opens configuration dialog  |

## Development

```bash
git clone https://github.com/thaikolja/dropzone-ai-reader.git
cd dropzone-ai-reader
python3 -m venv venv
./venv/bin/pip install openai groq
```

## Authors

* Kolja Nolte (kolja.nolte@gmail.com)

## License

[MIT](LICENSE)

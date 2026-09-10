# LDownlai

A lightweight YouTube downloader built with Python and yt-dlp. Elegant dark UI, minimal resource footprint, supports video (MP4) and audio (MP3) downloading with quality selection.

## Features

- Single video or playlist download
- MP4 video: 360p to 4K
- MP3 audio: 96kbps to 320kbps
- Playlist to MP3 conversion
- Preview with thumbnail and metadata
- Real-time progress with speed and ETA
- Cancel in-flight downloads
- Custom output directory

## Requirements

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) + [yt-dlp-ejs](https://github.com/yt-dlp/ejs)
- [ffmpeg](https://ffmpeg.org/) (bundled in release)
- A JavaScript runtime: [Deno](https://deno.com) (bundled in release) or Node.js 22+ — required by yt-dlp to solve YouTube's JS challenges since 2026

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Building

```bash
pip install pyinstaller
pyinstaller LDownlai.spec
```

The executable will be in `dist/LDownlai.exe`.

## Project Structure

```
LDownlai/
├── main.py              # Application entry point
├── LDownlai.spec        # PyInstaller build spec
├── app.ico              # Application icon
├── bin/                 # Bundled binaries (ffmpeg, deno)
├── requirements.txt     # Python dependencies
└── README.md
```

## License

MIT License — see [LICENSE](LICENSE).

## Author

**L'Abdouszlai**

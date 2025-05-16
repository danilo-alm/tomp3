# tomp3

**tomp3** is a command-line tool to batch convert audio files to high-quality MP3 format using FFmpeg. It supports parallel conversion, intelligent file skipping, optional deletion of originals, and customizable audio settings.

[![asciicast](https://asciinema.org/a/MoVkZr3BnlulPpEQAdwirBBf7.svg)](https://asciinema.org/a/MoVkZr3BnlulPpEQAdwirBBf7)


## 🚀 Features

- Batch convert `.flac`, `.wav`, and other audio files to MP3
- Input directory structure is preserved in the output (if applicable)
- Run multiple FFmpeg processes in parallel for faster conversion
- Optional deletion of original files
- Adjustable output bitrate, sample rate, quality, and channel mode (mono/stereo)
- Clean terminal UI with conversion status updates
- Dry run mode to preview which files will be converted


## 🛠 Installation

### Using `pipx` (recommended) or `pip`

Install the `tomp3` CLI tool globally with:

```bash
pipx install tomp3  # or pip
```

> 💡 `pipx` is preferred for CLI tools as it keeps dependencies isolated.


### 🛠️ From Source (for Development)

1. **Clone the repository**:

```bash
git clone https://github.com/danilo-alm/tomp3 && cd tomp3
```

2. **Install in editable mode** (so changes take effect immediately):

```bash
pip install --editable .
```

Or just run it with `uv`, without installing:

```bash
uv run -- python -m tomp3 <input_dir> [OPTIONS]
```


## ⚙️ Command-Line Arguments

| Argument                  | FFmpeg Equivalent             | Description                                                                |
| ------------------------- | ----------------------------- | -------------------------------------------------------------------------- |
| `input`                   | `-i`                          | Directory containing audio files to convert |
| `--output-dir DIR`        | `-o`                          | Output directory for converted files. Defaults to same as input|
| `--delete`                | *(manual delete)*             | Delete original files after successful conversion|
| `--target-extensions EXT` | N/A                           | Comma-separated list of file extensions to convert (default: `flac,wav`)|
| `--max-workers N`         | N/A                           | Number of parallel FFmpeg processes to run (default: `CPUs/2`)|
| `--dry-run`               | N/A                           | Only show which files would be converted, without running FFmpeg|
| `--mono`                  | `-ac 1`                       | Convert audio to mono (default is stereo)|
| `--quality N`             | `-q:a N`                 | LAME quality setting (`0` is best, `9` is worst, default: `0`)             |
| `--sample-rate SR`        | `-ar SR`                      | Sample rate in Hz for the output audio (default: `44100`)|
| `--bitrate BR`            | `-b:a BR`                     | Set constant output bitrate (e.g., `192k`). Overrides quality if specified|
| `--overwrite`             | `-y` | Overwrite existing converted files|
| `--no-ui` | N/A | Disable UI


### 🚀 Usage Examples

#### 📁 Convert `.flac` files from a folder to MP3s in a different output directory

```bash
tomp3 ~/Downloads/recordings --output-dir ~/Music/mp3s --target-extensions=flac
```

#### 🎧 Convert all `.flac` and `.wav` files in `~/Music` to mono MP3s and delete the originals

```bash
tomp3 ~/Music --delete --mono
```

#### 🔍 Preview what would be converted (dry run)

```bash
tomp3 ~/Music --dry-run
```

#### 🔊 Convert with a specific constant bitrate

```bash
tomp3 ./vocals --bitrate 192k
```

#### 🧵 Use 12 FFmpeg processes for parallel conversion

```bash
tomp3 ./dataset --max-workers=12
```

#### ⚠️ Overwrite previously converted MP3s

```bash
tomp3 ./mixes --overwrite
```



## 📝 License

This project is licensed under the **GNU General Public License v3.0**.

You are free to use, modify, and distribute this software under the terms of the license.
However, any derivative work must also be distributed under the same license.

For the full license text, see the [`LICENSE`](./LICENSE) file or visit [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).

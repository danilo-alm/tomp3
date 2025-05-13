# tomp3

**tomp3** is a command-line tool to batch convert audio files to high-quality MP3 format using FFmpeg. It supports parallel conversion, intelligent file skipping, optional deletion of originals, and customizable audio settings.

[![asciicast](https://asciinema.org/a/MoVkZr3BnlulPpEQAdwirBBf7.svg)](https://asciinema.org/a/MoVkZr3BnlulPpEQAdwirBBf7)

---

## 🚀 Features

- Batch convert `.flac`, `.wav`, and other audio files to MP3
- Input directory structure is preserved in the output (if applicable)
- Run multiple FFmpeg processes in parallel for faster conversion
- Optional deletion of original files
- Adjustable output bitrate, sample rate, quality, and channel mode (mono/stereo)
- Clean terminal UI with conversion status updates
- Dry run mode to preview which files will be converted

---

## 🛠 Installation

Make sure you have **Python** and [**FFmpeg**](https://www.ffmpeg.org/) installed.

[Install `uv`](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) if you haven't already:

```bash
pipx install uv  # (or pip)
````

---

## 📦 Usage

```bash
uv run -- python -m tomp3 <input_directory> [OPTIONS] 
```

### Example

```bash
uv run -- python -m tomp3 ~/Music --delete --mono
```

This command will convert all `.flac` and `.wav` files in `~/Music` to mono MP3s and delete the originals.

---

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

---

## 🧪 Dry Run Mode

You can preview what will be converted without executing any conversions:

```bash
uv run -- python -m tomp3 <input_directory> --dry-run
```

---

## 🧼 Clean Conversion Logic

* Files are only processed if the output does not exist (unless `--overwrite` is used)
* Conversion progress is shown in a clean TUI
* Original files are deleted only if `--delete` is passed *and* the conversion succeeds

---

## 📝 License

This project is licensed under the **GNU General Public License v3.0**.

You are free to use, modify, and distribute this software under the terms of the license.
However, any derivative work must also be distributed under the same license.

For the full license text, see the [`LICENSE`](./LICENSE) file or visit [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).

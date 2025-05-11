import argparse
import multiprocessing
from pathlib import Path
from typing import NamedTuple


class Args(NamedTuple):
    input: Path
    output_dir: Path | None
    delete: bool
    target_extensions: set[str]
    cpus: int
    bitrate: str
    dry_run: bool
    mono: bool
    quality: int
    sample_rate: int


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description="Convert audio files to MP3 format with high quality settings."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input file or directory to convert"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for converted files. If not specified, "
             "converted files will be placed in the same directory as input."
    )

    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete input files after successful conversion"
    )

    parser.add_argument(
        "--target-extensions",
        type=str,
        default="flac,wav",
        help="Comma-separated list of file extensions to convert (default: flac,wav)"
    )

    cores_default = max(1, multiprocessing.cpu_count() // 2)
    parser.add_argument(
        "--cpus",
        type=int,
        default=cores_default,
        help=f"Number of CPU cores to use (default: {cores_default})"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without actually converting"
    )

    parser.add_argument(
        "--mono",
        action="store_true",
        help="Convert to mono audio (default: stereo)"
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=0,
        help="Quality setting for LAME (0-9, where 0 is best quality, default: 0)"
    )
    
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="Sample rate for output audio (default: 44100)"
    )

    parser.add_argument(
        "--bitrate",
        type=str,
        help="Output bitrate (no default for Variable Bit Rate)"
    )

    args = parser.parse_args()

    target_extensions = {
        f".{ext.strip().lower()}" 
        for ext in args.target_extensions.split(",")
    }

    return Args(
        input=args.input,
        output_dir=args.output_dir,
        delete=args.delete,
        target_extensions=target_extensions,
        cpus=args.cpus,
        bitrate=args.bitrate,
        dry_run=args.dry_run,
        mono=args.mono,
        quality=args.quality,
        sample_rate=args.sample_rate
    )

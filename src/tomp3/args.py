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
        "--bitrate",
        type=str,
        default="320k",
        help="Output bitrate (default: 320k)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without actually converting"
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
        dry_run=args.dry_run
    )

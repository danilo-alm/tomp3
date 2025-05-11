import logging
from pathlib import Path

import ffmpeg

from tomp3.args import Args, parse_args
from tomp3.converter import Converter
from tomp3.converter.path_resolver import OutputPathResolver
from tomp3.log_config import setup_logger
from tomp3.ui import ConversionUI
from tomp3.ui.file_status import FileStatus


def main() -> None:
    args = parse_args()
    logger = setup_logger(dry_run=args.dry_run)

    converter = build_converter(args, logger)

    if args.input.is_file():
        convert_single_file(converter, args.input)
    elif args.input.is_dir():
        convert_directory(converter, args, logger)
    else:
        raise ValueError("Invalid input. Provide a file or directory.")


def build_converter(args: Args, logger: logging.Logger) -> Converter:
    return Converter(
        output_path_resolver=OutputPathResolver(args.input, args.output_dir),
        bitrate=args.bitrate,
        cleanup_after_conversion=args.delete,
        logger=logger
    )


def convert_single_file(converter: Converter, fpath: Path) -> None:
    converter.to_mp3(fpath)


def convert_directory(converter: Converter, args: Args, logger: logging.Logger) -> None:
    tui = ConversionUI()
    fpaths = scan_directory(args.input, args.target_extensions)
    tui.set_file_list(fpaths)
    logger.info(f"Found {len(fpaths)} files to convert in '{args.input}'.")

    for fpath in fpaths:
        try:
            tui.update_file_status(fpath, FileStatus.CONVERTING)
            converter.to_mp3(fpath)
            tui.update_file_status(fpath, FileStatus.CONVERTED)
        except ffmpeg.Error as e:
            tui.update_file_status(fpath, FileStatus.ERROR)
            logger.exception(e)


def scan_directory(directory: Path, extensions: set[str]) -> list[Path]:
    return [
        f.resolve()
        for f in directory.rglob("*")
        if f.is_file() and f.suffix.lower() in extensions
    ]


if __name__ == "__main__":
    main()
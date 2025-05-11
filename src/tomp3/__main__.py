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
    args: Args = parse_args()
    logger = setup_logger(
        console=args.dry_run
    )
        
    opr = OutputPathResolver(args.input, args.output_dir)
    converter = Converter(
        output_path_resolver=opr,
        bitrate=args.bitrate,
        cleanup_after_conversion=args.delete,
        logger=logger
    )

    if args.input.is_file():
        handle_file(converter=converter, fpath=args.input)
    elif args.input.is_dir():
        handle_directory(
            converter=converter,
            dpath=args.input,
            target_extensions=args.target_extensions,
            tui=ConversionUI(),
            logger=logger
        )
    else:
        raise Exception("Invalid input. Please provide either file or directory.")

def handle_file(converter: Converter, fpath: Path) -> Path:
    output = converter.to_mp3(fpath)
    return output

def handle_directory(
        converter: Converter,
        dpath: Path,
        target_extensions: set[str],
        tui: ConversionUI,
        logger: logging.Logger
    ) -> None:
    logger.info(f"Scanning directory: {dpath}")
    fpaths = list(
        f for f in dpath.rglob("*")
        if f.is_file()
        and f.suffix.lower() in target_extensions
    )
    tui.set_file_list(fpaths)
    logger.info(f"Found {len(fpaths)} files to convert.")

    # Use later for estimating remaining time
    # size = sum(f.stat().st_size for f in files)

    for fpath in fpaths:
        try:
            tui.update_file_status(fpath, FileStatus.CONVERTING)
            handle_file(converter, fpath)
            tui.update_file_status(fpath, FileStatus.CONVERTED)
        except ffmpeg.Error as e:
            tui.update_file_status(fpath, FileStatus.ERROR)
            logger.exception(e)


if __name__ == "__main__":
    main()

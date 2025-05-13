import logging
import subprocess
import time
from pathlib import Path
from typing import Callable, Generator

from tomp3.args import Args, parse_args
from tomp3.log_config import setup_logger
from tomp3.path_resolver import OutputPathResolver
from tomp3.ui import ConversionUI
from tomp3.ui.file_status import FileStatus
from tomp3.ui.null_ui import NullUI
from tomp3.ui.ui_protocol import TUIProtocol


def main() -> None:
    args = parse_args()
    logger = setup_logger(dry_run=args.dry_run)

    if args.input_dir.exists() and args.input_dir.is_dir():
        path_resolver = OutputPathResolver(
            args.input_dir,
            args.output_dir,
            args.dry_run
        )
        handle_directory(args, path_resolver, logger)
    else:
        raise ValueError("Please provide a valid directory.")


def handle_directory(
        args: Args,
        path_resolver: OutputPathResolver,
        logger: logging.Logger
    ) -> None:
    fpaths = get_files_to_convert(args.input_dir, args.target_extensions, logger)
    output_fpaths = (path_resolver.resolve(fpath) for fpath in fpaths)

    if dry_run(args, fpaths, output_fpaths, logger):
        return

    tui: TUIProtocol = initialize_ui(args) if args.tui else NullUI()
    tui.set_file_list(fpaths)

    ffmpeg_args = build_ffmpeg_args(args)
    running_processes: dict[subprocess.Popen[bytes], Path] = {}

    def cleanup() -> None:
        cleanup_finished_processes(running_processes, tui, args)

    for ifpath, ofpath in zip(fpaths, output_fpaths):
        while len(running_processes) >= args.max_workers:
            cleanup()
            time.sleep(0.1)

        if should_skip_conversion(ofpath, args, tui, logger, ifpath):
            continue

        cmd = ["ffmpeg", "-i", str(ifpath), *ffmpeg_args, str(ofpath)]
        logger.debug(f"Running command: {' '.join(cmd)}")

        process = start_conversion_process(cmd)
        running_processes[process] = ifpath
        tui.update_file_status(ifpath, FileStatus.CONVERTING)

    wait_for_all_processes(running_processes, cleanup)

    tui.force_update()
    time.sleep(0.5)
    tui.stop()


def dry_run(
        args: Args,
        fpaths: list[Path],
        output_fpaths: Generator[Path],
        logger: logging.Logger
    ) -> bool:
    if args.dry_run:
        for ifpath, ofpath in zip(fpaths, output_fpaths):
            logger.info(f"Would convert: {ifpath} -> {ofpath}")
        return True
    return False


def initialize_ui(args: Args) -> ConversionUI:
    return ConversionUI(visible_files=max(20, args.max_workers + 5))


def get_files_to_convert(
        input_dir: Path,
        extensions: set[str],
        logger: logging.Logger
    ) -> list[Path]:
    fpaths = scan_directory(input_dir, extensions)
    logger.info(f"Found {len(fpaths)} files to convert in '{input_dir}'.")
    return fpaths


def scan_directory(directory: Path, extensions: set[str]) -> list[Path]:
    return [
        f.resolve()
        for f in directory.rglob("*")
        if f.is_file() and f.suffix.lower() in extensions
    ]


def build_ffmpeg_args(
        args: Args,
    ) -> list[str]:
    cmd = [
        "-acodec", "libmp3lame",
        "-ar", str(args.sample_rate) if args.sample_rate else "44100",
        "-ac", "1" if args.mono else "2",
    ]

    if args.bitrate:
        cmd += ["-b:a", str(args.bitrate)]
    if args.quality:
        cmd += ["-q:a", str(args.quality)]
    if args.overwrite:
        cmd.append("-y")
    
    return cmd


def cleanup_finished_processes(
    running_processes: dict[subprocess.Popen[bytes], Path],
    tui: TUIProtocol,
    args: Args
) -> None:
    for process in list(running_processes):
        if process.poll() is None:
            continue

        success = process.returncode == 0
        fpath = running_processes.pop(process)

        tui.update_file_status(
            fpath, FileStatus.CONVERTED if success else FileStatus.ERROR
        )

        if success and args.delete:
            fpath.unlink()


def should_skip_conversion(
        output_path: Path,
        args: Args,
        tui: TUIProtocol,
        logger: logging.Logger,
        fpath: Path
    ) -> bool:
    if output_path.exists() and not args.overwrite:
        tui.update_file_status(fpath, FileStatus.CONVERTED)
        logger.info(f"Skipping: {fpath} -> {output_path} as it already exists.")
        return True
    return False


def start_conversion_process(cmd: list[str]) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )


def wait_for_all_processes(
    running_processes: dict[subprocess.Popen[bytes], Path],
    cleanup_fn: Callable[[], None]
) -> None:
    for process in list(running_processes):
        process.wait()
        cleanup_fn()


if __name__ == "__main__":
    main()

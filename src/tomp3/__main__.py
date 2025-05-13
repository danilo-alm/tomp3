import logging
import subprocess
import time
from pathlib import Path

from tomp3.args import Args, parse_args
from tomp3.log_config import setup_logger
from tomp3.path_resolver import OutputPathResolver
from tomp3.ui import ConversionUI
from tomp3.ui.file_status import FileStatus


def main() -> None:
    args = parse_args()
    logger = setup_logger(dry_run=args.dry_run)
    path_resolver = OutputPathResolver(
        input_root=args.input,
        output_root=args.output_dir,
    )
    
    if args.input.is_dir():
        handle_directory(args, path_resolver, logger)


def handle_directory(
        args: Args,
        path_resolver: OutputPathResolver,
        logger: logging.Logger
    ) -> None:

    def cleanup_finished_processes() -> None:
        finished = []
        for p in list(running_processes):
            if p.poll() is None:
                continue

            success = p.returncode == 0
            fpath = running_processes.pop(p)
            tui.update_file_status(
                fpath,
                FileStatus.CONVERTED if success else FileStatus.ERROR
            )

            if success and args.delete:
                fpath.unlink()

            finished.append(p)
    
    tui = ConversionUI(visible_files=max(20, args.max_workers + 5))
    fpaths = scan_directory(args.input, args.target_extensions)
    tui.set_file_list(fpaths)
    logger.info(f"Found {len(fpaths)} files to convert in '{args.input}'.")
    
    ffmpeg_args = build_ffmpeg_args(args)

    MAX_PROCESSES = args.max_workers
    running_processes: dict[subprocess.Popen[bytes], Path] = {}

    for fpath in fpaths:
        while len(running_processes) >= MAX_PROCESSES:
            cleanup_finished_processes()
            time.sleep(0.1)
        
        output_path = path_resolver.resolve(fpath)

        if output_path.exists() and not args.overwrite:
            tui.update_file_status(fpath, FileStatus.CONVERTED)
            logger.info(f"Skipping: {fpath} -> {output_path} as it already exists.")
        else:
            cmd = ["ffmpeg", "-i", str(fpath), *ffmpeg_args, str(output_path)]
            print('Running command:', ' '.join(cmd))
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            running_processes[process] = fpath
            tui.update_file_status(fpath, FileStatus.CONVERTING)

    for p in list(running_processes):
        p.wait()
        cleanup_finished_processes()
    
    tui.force_update()
    time.sleep(0.5)
    tui.stop()


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


def scan_directory(directory: Path, extensions: set[str]) -> list[Path]:
    return [
        f.resolve()
        for f in directory.rglob("*")
        if f.is_file() and f.suffix.lower() in extensions
    ]


if __name__ == "__main__":
    main()

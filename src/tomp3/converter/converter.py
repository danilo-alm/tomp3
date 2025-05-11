import logging
from pathlib import Path

import ffmpeg

from .path_resolver import OutputPathResolver


class Converter:
    def __init__(
            self,
            output_path_resolver: OutputPathResolver,
            bitrate: str,
            cleanup_after_conversion: bool,
            logger: logging.Logger
        ) -> None:
        self.output_path_resolver = output_path_resolver
        self.bitrate = bitrate
        self.cleanup_after_conversion = cleanup_after_conversion
        self.logger = logger

    def to_mp3(self, fpath: Path) -> Path:
        output_path = self.output_path_resolver.resolve(fpath)

        try:
            stream = ffmpeg.input(str(fpath))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='libmp3lame',
                audio_bitrate=self.bitrate,
                ar='44100',  # Sample rate
                ac=2,  # Number of audio channels (stereo)
                **{'q:a': '0'}  # Highest quality setting for LAME
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            self.logger.info(f"Converted {fpath} to {output_path}")

            if self.cleanup_after_conversion:
                fpath.unlink(missing_ok=True)
                self.logger.info(f"Deleted original file: {fpath}")

            return output_path

        except ffmpeg.Error as e:
            message = f"Conversion failed: {e.stderr.decode() if e.stderr else str(e)}"
            raise ffmpeg.Error(message)
 
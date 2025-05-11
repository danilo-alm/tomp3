import logging
from pathlib import Path
from typing import Any

import ffmpeg

from .path_resolver import OutputPathResolver


class Converter:
    def __init__(
            self,
            output_path_resolver: OutputPathResolver,
            cleanup_after_conversion: bool,
            bitrate: str,
            quality: int,
            mono: bool,
            sample_rate: int,
            logger: logging.Logger
        ) -> None:
        self.output_path_resolver = output_path_resolver
        self.cleanup_after_conversion = cleanup_after_conversion
        self.logger = logger

        self.bitrate = bitrate
        self.quality = quality
        self.mono = mono
        self.sample_rate = sample_rate

    def to_mp3(self, fpath: Path) -> Path:
        output_path = self.output_path_resolver.resolve(fpath)
        kwargs = self._build_output_kwargs()

        try:
            stream = ffmpeg.input(str(fpath))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='libmp3lame',
                **kwargs
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            self.logger.info(f"Converted {fpath} to {output_path}")

            if self.cleanup_after_conversion:
                fpath.unlink(missing_ok=True)
                self.logger.info(f"Deleted original file: {fpath}")

            return output_path

        except ffmpeg.Error as e:
            message = f"Conversion failed: {e.stderr.decode() if e.stderr else str(e)}"
            raise ffmpeg.Error(message, e.stdout, e.stderr) from e
 
    def _build_output_kwargs(self) -> dict[str, Any]:
        kwargs = {
            'audio_bitrate': self.bitrate,
            'ar': self.sample_rate,
            'ac': 1 if self.mono else 2,
            'q:a': self.quality
        }
        return {k: v for k, v in kwargs.items() if v is not None}
from pathlib import Path
from typing import Optional

import ffmpeg

from tomp3 import logger


class Converter:
    def __init__(
            self,
            output_dir: Optional[Path],
            bitrate: str,
            cleanup_after_conversion: bool,
        ) -> None:
        self.output_dir = output_dir
        self.bitrate = bitrate
        self.cleanup_after_conversion = cleanup_after_conversion

        if self.output_dir is not None:
            if self.output_dir.is_file():
                raise ValueError("Output directory cannot be a file.")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {self.output_dir}")

    def to_mp3(self, input_path: Path) -> Path:
        output_path = self._get_output_path(input_path)

        try:
            stream = ffmpeg.input(str(input_path))
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
            logger.info(f"Converted {input_path} to {output_path}")

            if self.cleanup_after_conversion:
                input_path.unlink(missing_ok=True)
                logger.info(f"Deleted original file: {input_path}")

            return output_path

        except ffmpeg.Error as e:
            message = f"Conversion failed: {e.stderr.decode() if e.stderr else str(e)}"
            raise ffmpeg.Error(message)
        
    def _get_output_path(self, input_path: Path) -> Path:
        if self.output_dir is None:
            return input_path.with_suffix('.mp3')

        if input_path.is_absolute():
            rel_path = input_path.relative_to(input_path.anchor)
        else:
            rel_path = input_path

        rel_path = Path(*rel_path.parts[1:])
        output_path = self.output_dir / rel_path.parent / f"{input_path.stem}.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

from pathlib import Path
from typing import Optional


class CueSheetHandler:
    def has_cue_sheet(self, path: Path) -> Optional[Path]:
        if path.is_file():
            path = path.parent
        return next(f for f in path.glob("*.cue") if f.is_file())
    
    def convert_cue_sheet(self, cue_file: Path) -> None:
        content = cue_file.read_text()
        lines = content.splitlines()

        for i, line in enumerate(lines):
            if line.lstrip().startswith('FILE'):
                lines[i] = self._convert_file_line(line)
                break
        else:
            raise ValueError(f"No FILE line found to convert in {cue_file}")

        cue_file.write_text("\n".join(lines))
    
    def _convert_file_line(self, line: str) -> str:
        line_parts = line.split()
        original_path = Path(' '.join(line_parts[1:-1]).strip('"'))
        converted_path = original_path.with_suffix(".mp3")
        return ' '.join((line_parts[0], f"\"{converted_path}\"", "MP3"))
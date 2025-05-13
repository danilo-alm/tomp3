from pathlib import Path
from typing import Optional


class OutputPathResolver:
    def __init__(
            self,
            input_root: Optional[Path],
            output_root: Optional[Path],
            dry_run: bool = False
        ) -> None:
        if not input_root:
            raise ValueError("input_root cannot be None.")

        self.input_root = input_root.resolve()
        self.output_root = output_root.resolve() if output_root else None
        self.dry_run = dry_run

        if self.input_root and not self.input_root.exists():
            raise ValueError(f"Input root path does not exist: {self.input_root}")
        if self.output_root and not self.dry_run:
            self.output_root.mkdir(parents=True, exist_ok=True)

    def resolve(self, fpath: Path) -> Path:
        if not self.output_root:
            return fpath.with_suffix('.mp3')

        if not self.input_root:
            raise ValueError("Cannot resolve path structure: input_root is required.")

        try:
            rel_path = fpath.resolve().relative_to(self.input_root)
        except ValueError:
            message = f"File {fpath} is not inside the input root {self.input_root}"
            raise ValueError(message)

        output_path = self.output_root / rel_path.with_suffix('.mp3')
        if not self.dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

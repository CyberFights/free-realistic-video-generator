from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Optional


@dataclass
class StoredFile:
    path: str
    url: str


class LocalStorage:
    def __init__(self, base_dir: Optional[str] = None, public_url: Optional[str] = None):
        self.base_dir = Path(base_dir or os.getenv("LOCAL_STORAGE_DIR", "./storage"))
        self.public_url = public_url or os.getenv("PUBLIC_STORAGE_URL", "http://localhost:8000/storage")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file_obj: BinaryIO, folder: str, original_name: str) -> StoredFile:
        target_dir = self.base_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)

        safe_name = original_name.replace(" ", "_")
        file_path = target_dir / safe_name

        with open(file_path, "wb") as out:
            out.write(file_obj.read())

        relative_path = f"{folder}/{safe_name}"
        return StoredFile(
            path=str(file_path),
            url=f"{self.public_url}/{relative_path}",
        )


storage = LocalStorage()

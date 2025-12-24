
from __future__ import annotations
import os


class PersonaStore:
    def __init__(self, persona_dir: str):
        self.persona_dir = persona_dir
        os.makedirs(self.persona_dir, exist_ok=True)

    def list_files(self) -> list[str]:
        os.makedirs(self.persona_dir, exist_ok=True)
        files = []
        for name in os.listdir(self.persona_dir):
            p = os.path.join(self.persona_dir, name)
            if os.path.isfile(p):
                files.append(name)
        files.sort(key=lambda s: s.lower())
        return files

    def read(self, filename: str) -> str:
        if not filename:
            return ""
        path = os.path.join(self.persona_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def write(self, filename: str, content: str) -> bool:
        if not filename:
            return False
        os.makedirs(self.persona_dir, exist_ok=True)
        path = os.path.join(self.persona_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content or "")
            return True
        except Exception:
            return False

    def create(self, filename: str, content: str = "") -> bool:
        filename = (filename or "").strip()
        if not filename:
            return False
        if os.path.sep in filename or filename.startswith("."):
            return False
        path = os.path.join(self.persona_dir, filename)
        if os.path.exists(path):
            return False
        return self.write(filename, content)

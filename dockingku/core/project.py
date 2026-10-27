"""Satu proyek docking = satu folder biasa dengan project.json."""
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

SUBDIRS = ("receptor", "ligands", "pockets", "docking", "analysis", "report")


@dataclass
class Project:
    root: Path
    name: str
    created: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    params: dict = field(default_factory=dict)  # parameter per langkah
    steps: dict = field(default_factory=dict)  # status per langkah: todo, running, done, failed

    @classmethod
    def create(cls, parent: Path, name: str) -> "Project":
        slug = re.sub(r"[^\w-]+", "-", name).strip("-") or "proyek"
        root = parent / slug
        for sub in SUBDIRS:
            (root / sub).mkdir(parents=True, exist_ok=True)
        project = cls(root=root, name=name)
        project.save()
        return project

    @classmethod
    def open(cls, root: Path) -> "Project":
        data = json.loads((root / "project.json").read_text(encoding="utf-8"))
        return cls(root=root, **data)

    def save(self):
        data = {"name": self.name, "created": self.created, "params": self.params, "steps": self.steps}
        (self.root / "project.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def path(self, sub: str, filename: str = "") -> Path:
        return self.root / sub / filename

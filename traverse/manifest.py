"""The stage contract. A stage reads exactly one manifest and writes exactly one.

The manifest is the only thing one stage may know about another. Its sha is
the content identity every verdict row carries as input_manifest_sha and
output_manifest_sha, so a row can be traced to the exact bytes each stage saw.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from traverse import canon

@dataclass(frozen=True)
class Item:
    id: str
    path: str
    bytes: int
    sha256: str
    extra: dict = field(default_factory=dict)

@dataclass(eq=False)
class Manifest:
    stage: str
    run_id: str
    items: list[Item]
    created_at: str
    meta: dict = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        # Equality is the content identity: two manifests are equal when their
        # shas are. to_dict() sorts items by id, so a stage may keep its items in
        # its own order (serve lists cells, then outputs) and still equal its
        # saved-and-loaded copy. Comparing shas, not dicts, keeps values that are
        # equal in Python but not in canonical bytes (1 and True) unequal.
        if not isinstance(other, Manifest):
            return NotImplemented
        return self.sha() == other.sha()

    __hash__ = None  # mutable, so unhashable, as the generated dataclass was

    def to_dict(self) -> dict:
        return {
            "kind": "MANIFEST",
            "stage": self.stage,
            "run_id": self.run_id,
            "created_at": self.created_at,
            "meta": self.meta,
            "items": [asdict(i) for i in sorted(self.items, key=lambda i: i.id)],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Manifest":
        if d.get("kind") != "MANIFEST":
            raise ValueError(f"not a manifest: kind={d.get('kind')!r}")
        return cls(
            stage=d["stage"],
            run_id=d["run_id"],
            items=[Item(**i) for i in d["items"]],
            created_at=d["created_at"],
            meta=d.get("meta", {}),
        )

    def sha(self) -> str:
        return canon.sha256_of(self.to_dict())

    def save(self, path: Path) -> str:
        canon.write_json(path, self.to_dict())
        return self.sha()

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        return cls.from_dict(canon.read_json(path))

    def total_bytes(self) -> int:
        return sum(i.bytes for i in self.items)

def file_item(id: str, path: Path, rel_to: Path, **extra) -> Item:
    data = path.read_bytes()
    return Item(
        id=id,
        path=path.resolve().relative_to(rel_to.resolve()).as_posix(),
        bytes=len(data),
        sha256=canon.sha256_hex(data),
        extra=dict(extra),
    )

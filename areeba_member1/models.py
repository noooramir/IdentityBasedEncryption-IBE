from __future__ import annotations

from dataclasses import dataclass



@dataclass(slots=True)
class User:
    id: int
    identity: str
    private_key: str | None = None


    def public_dict(self) -> dict[str, int | str]:
        return {"id": self.id, "identity": self.identity}

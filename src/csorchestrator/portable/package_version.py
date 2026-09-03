from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PackageVersion:
    name: str
    version: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "PackageVersion":
        return cls(**data)

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass
class Expected(Generic[T, E]):
    """A class that represents a value that can either be
    a success (with a value) or an error (with an error message)."""

    value: T | None = None
    error: E | None = None

    @classmethod
    def make_value(cls, result: T) -> "Expected[T,E]":
        return cls(value=result)

    @classmethod
    def make_error(cls, error: E) -> "Expected[T,E]":
        return cls(error=error)

    def __post_init__(self) -> None:
        if (self.value is None) == (self.error is None):
            raise ValueError("Expected must have exactly one of value or error")

    @property
    def is_ok(self) -> bool:
        return self.error is None

    @property
    def is_error(self) -> bool:
        return self.error is not None

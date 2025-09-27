"""Compatibility helpers for optional tqdm dependency."""

from __future__ import annotations

from typing import Iterable, Iterator, Optional, TypeVar

T = TypeVar("T")

try:  # pragma: no cover - exercised when tqdm is available
    from tqdm import tqdm as tqdm  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - triggered in minimal installs

    class _DummyTqdm(Iterator[T]):
        """Minimal tqdm replacement when the real dependency is unavailable."""

        def __init__(
            self,
            iterable: Optional[Iterable[T]] = None,
            *args,
            total: Optional[int] = None,
            **kwargs,
        ) -> None:
            self._iterable = iterable
            self._iterator = iter(iterable) if iterable is not None else iter(())
            self.total = total if total is not None else (len(iterable) if hasattr(iterable, "__len__") else None)
            self.n = 0

        def __iter__(self) -> Iterator[T]:
            return self

        def __next__(self) -> T:  # Support Iterator protocol directly
            item = next(self._iterator)
            self.n += 1
            return item

        def update(self, n: int = 1) -> None:
            self.n += n

        def set_description(self, *args, **kwargs) -> None:  # noqa: D401 - passthrough
            """No-op placeholder for tqdm API compatibility."""

        def set_postfix(self, *args, **kwargs) -> None:
            pass

        def set_postfix_str(self, *args, **kwargs) -> None:
            pass

        def close(self) -> None:
            pass

        def __enter__(self) -> "_DummyTqdm":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    def tqdm(iterable: Optional[Iterable[T]] = None, *args, **kwargs) -> _DummyTqdm:
        return _DummyTqdm(iterable, *args, **kwargs)

__all__ = ["tqdm"]

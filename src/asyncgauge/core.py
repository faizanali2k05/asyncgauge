from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from time import monotonic
from typing import Any, Awaitable, Callable


@dataclass(frozen=True)
class ProbeResult:
    name: str
    ok: bool
    elapsed: float
    error: str | None = None
    value: Any = None

    @property
    def status(self) -> str:
        return "ok" if self.ok else "error"

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ok": self.ok,
            "status": self.status,
            "elapsed": self.elapsed,
            "error": self.error,
            "value": self.value,
        }


async def run_probe(name: str, probe: Callable[[], Any | Awaitable[Any]], timeout: float = 5.0) -> ProbeResult:
    if not name:
        raise ValueError("probe name must not be empty")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    started = monotonic()
    try:
        result = probe()
        if inspect.isawaitable(result):
            result = await asyncio.wait_for(result, timeout)
        return ProbeResult(name, True, monotonic() - started, value=result)
    except Exception as exc:  # probes must report, not crash, the health endpoint
        return ProbeResult(name, False, monotonic() - started, error=f"{type(exc).__name__}: {exc}")


async def run_all(probes: dict[str, Callable[[], Any | Awaitable[Any]]], timeout: float = 5.0) -> list[ProbeResult]:
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    results = await asyncio.gather(*(run_probe(name, probe, timeout) for name, probe in probes.items()))
    return sorted(results, key=lambda result: result.name)


def healthy(results: list[ProbeResult]) -> bool:
    """Return whether every probe in a result set succeeded."""

    return all(result.ok for result in results)

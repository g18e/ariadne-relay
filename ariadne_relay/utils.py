import asyncio
from typing import Any, Callable, Optional


def is_coroutine_callable(obj: Optional[Callable[..., Any]]) -> bool:
    if obj is None:
        return False
    if asyncio.iscoroutinefunction(obj):
        return True
    if hasattr(obj, "__call__") and asyncio.iscoroutinefunction(
        getattr(obj, "__call__")
    ):
        return True
    return False

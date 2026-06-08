import logging
import time
from functools import wraps
from typing import Any

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ai_decision_engine")


def timed_node(name: str):
    """Wrap a LangGraph node to log execution time and state summary."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(state, *args, **kwargs):
            domain = getattr(state, "domain", "unknown")
            logger.info("[%s] start | domain=%s", name, domain)
            start = time.perf_counter()
            try:
                result = fn(state, *args, **kwargs)
                elapsed = time.perf_counter() - start
                summary = _result_summary(name, result)
                logger.info("[%s] done  | %.3fs | %s", name, elapsed, summary)
                return result
            except Exception as exc:
                elapsed = time.perf_counter() - start
                logger.error("[%s] error | %.3fs | %s: %s", name, elapsed, type(exc).__name__, exc)
                raise
        return wrapper
    return decorator


def _result_summary(node: str, result: dict[str, Any]) -> str:
    if not result:
        return "empty"
    parts = []
    for key, val in result.items():
        if isinstance(val, list):
            parts.append(f"{key}={len(val)} items")
        elif isinstance(val, str) and len(val) > 60:
            parts.append(f"{key}={repr(val[:57])}...")
        else:
            parts.append(f"{key}={repr(val)}")
    return " | ".join(parts)

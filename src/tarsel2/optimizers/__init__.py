"""Optional coverage-matrix purification.

Each optimizer rewrites the window set before scoring. They are applied in the
order listed in the project yaml.
"""

from .base import BaseMatrixOptimizer
from .canal import CanalOptimizer
from .mss import MSSOptimizer
from .span_merge import SpanMergeOptimizer

REGISTRY = {
    "canal": CanalOptimizer,
    "mss": MSSOptimizer,
    "span_merge": SpanMergeOptimizer,
}

__all__ = [
    "BaseMatrixOptimizer",
    "CanalOptimizer",
    "MSSOptimizer",
    "SpanMergeOptimizer",
    "REGISTRY",
    "build_optimizers",
]


def build_optimizers(names):
    """Instantiate optimizers by name, preserving the configured order."""
    built = []
    for name in names or []:
        key = str(name).strip().lower()
        if key not in REGISTRY:
            raise ValueError(
                f"unknown optimizer: {name} (available: {sorted(REGISTRY)})"
            )
        built.append(REGISTRY[key]())
    return built

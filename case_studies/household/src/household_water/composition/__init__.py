"""Composition strategies for multi-step treatment unit simulation.

This package implements three composition strategies:
- cascade: Sequential HTTP calls between sub-model services (Strategy A)
- assembly: Coupled ODE system solved jointly (Strategy B)
- lumped: Algebraic fallback using removal efficiencies (Strategy C)
"""

from .cascade import cascade_simulate
from .lumped import lumped_simulate

__all__ = ["cascade_simulate", "lumped_simulate"]

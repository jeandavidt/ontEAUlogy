"""Strategy B — Assembly composition via coupled ODE system.

This strategy combines ODE systems from multiple sub-units into a single
joint system and solves them together. Currently a placeholder for future
implementation when tight coupling between sub-steps is needed.
"""

from typing import Any, Dict

from ..schemas.common import CompositionRequest


def assemble_and_solve(request: CompositionRequest) -> Dict[str, Any]:
    """Execute assembly composition: coupled ODE system.

    This is a placeholder implementation. Full assembly would:
    1. Look up sub-unit physics modules by IRI pattern
    2. Concatenate state vectors: y = [y_unit1, y_unit2, ...]
    3. Couple via outlet/inlet linkage terms in combined rhs
    4. Call solve_ivp on assembled system

    Args:
        request: CompositionRequest with sub_unit_iris and inputs.

    Returns:
        Dictionary indicating assembly strategy is not yet implemented,
        suggesting use of cascade or lumped strategies instead.

    Raises:
        NotImplementedError: Always, until full implementation is added.
    """
    raise NotImplementedError(
        "Assembly composition strategy (coupled ODE) is not yet implemented. "
        "Use 'cascade' or 'lumped' strategies instead."
    )

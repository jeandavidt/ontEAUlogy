"""Strategy A — Cascade composition via sequential HTTP calls.

Each sub-unit is simulated in sequence, with the output of step N
becoming the input to step N+1. Uses httpx for async HTTP calls.
"""

from typing import Any, Dict, List

import httpx

from ..schemas.common import CompositionRequest


# Mapping of output field names to input field names for inter-step translation
_OUTPUT_TO_INPUT_MAP = {
    "effluent_flow_m3d": "influent_flow_m3d",
    "effluent_cod_mg_l": "influent_cod_mg_l",
    "effluent_bod_mg_l": "influent_bod_mg_l",
    "effluent_tss_mg_l": "influent_tss_mg_l",
    "effluent_nh4_mg_l": "influent_nh4_mg_l",
    "effluent_tp_mg_l": "influent_tp_mg_l",
    "permeate_flow_m3d": "influent_flow_m3d",
    "permeate_tds_mg_l": "feed_tds_mg_l",
    "permeate_conductivity_us_cm": "feed_conductivity_us_cm",
    "permeate_turbidity_ntu": "feed_turbidity_ntu",
    "infiltrated_flow_m3d": "influent_flow_m3d",
}


def _map_output_to_next_input(
    step_output: Dict[str, Any], sub_unit_iri: str
) -> Dict[str, float]:
    """Map output fields from one step to input fields for the next step.

    Args:
        step_output: Output dictionary from the previous simulation step.
        sub_unit_iri: IRI of the sub-unit (for context-specific mappings).

    Returns:
        Dictionary mapped to input field names for the next step.
    """
    mapped: Dict[str, float] = {}
    for out_key, value in step_output.items():
        if out_key in _OUTPUT_TO_INPUT_MAP:
            in_key = _OUTPUT_TO_INPUT_MAP[out_key]
            mapped[in_key] = float(value)
    return mapped


async def cascade_simulate(request: CompositionRequest) -> Dict[str, Any]:
    """Execute cascade composition: sequential HTTP calls to sub-models.

    Each sub-unit is simulated in order. The output of step N is mapped
    to become the input of step N+1. All intermediate SimulationRun IRIs
    are recorded.

    Args:
        request: CompositionRequest with sub_unit_iris, sub_unit_endpoints,
            inputs, simulation_mode, etc.

    Returns:
        Dictionary with:
        - final_outputs: Output from the last step (mapped to standard names)
        - step_run_iris: List of simulation_run_iri from each step
        - intermediate_outputs: List of output dicts from each step

    Raises:
        httpx.HTTPError: If any sub-model call fails.
        ValueError: If sub_unit_iris and sub_unit_endpoints lengths mismatch.
    """
    if len(request.sub_unit_iris) != len(request.sub_unit_endpoints):
        raise ValueError(
            f"sub_unit_iris ({len(request.sub_unit_iris)}) and "
            f"sub_unit_endpoints ({len(request.sub_unit_endpoints)}) must have same length"
        )

    current_inputs: Dict[str, float] = dict(request.inputs)
    step_run_iris: List[str] = []
    intermediate_outputs: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for sub_iri, endpoint in zip(request.sub_unit_iris, request.sub_unit_endpoints):
            # Build payload for this step
            payload: Dict[str, Any] = {
                **current_inputs,
                "simulation_mode": request.simulation_mode.value,
            }
            if request.scenario_iri:
                payload["scenario_iri"] = request.scenario_iri
            if request.dynamic_config:
                payload["dynamic_config"] = request.dynamic_config.model_dump()

            # Call sub-model's /simulate endpoint
            resp = await client.post(f"{endpoint}/simulate", json=payload)
            resp.raise_for_status()
            step_output = resp.json()

            # Record run IRI if present
            run_iri = step_output.get("simulation_run_iri")
            if run_iri:
                step_run_iris.append(run_iri)

            intermediate_outputs.append(step_output)

            # Map output to next step's input (unless this is the last step)
            current_inputs = _map_output_to_next_input(step_output, sub_iri)

    return {
        "final_outputs": intermediate_outputs[-1]
        if intermediate_outputs
        else current_inputs,
        "step_run_iris": step_run_iris,
        "intermediate_outputs": intermediate_outputs,
        "composition_strategy": "cascade",
        "n_steps": len(request.sub_unit_iris),
    }

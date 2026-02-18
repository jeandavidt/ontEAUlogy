"""Strategy C — Lumped composition via algebraic removal efficiencies.

When sub-model services are unavailable or fast screening is needed,
this strategy applies sequential first-order removal using default
removal fractions for each sub-unit type.
"""

from typing import Any, Dict, List

from ..schemas.common import CompositionRequest


# Default removal fractions by unit type (identified by IRI substring)
_DEFAULT_REMOVALS: Dict[str, Dict[str, float]] = {
    "Membrane_bioreactor": {
        "cod": 0.95,
        "bod": 0.97,
        "tss": 0.99,
        "nh4": 0.85,
        "tp": 0.60,
    },
    "Reverse_osmosis": {
        "tds": 0.99,
        "conductivity": 0.98,
        "turbidity": 0.99,
    },
    "Infiltration": {
        "cod": 0.70,
        "tss": 0.90,
        "nh4": 0.50,
    },
}

# Mapping of input pollutant names to removal categories
_POLLUTANT_MAP = {
    "influent_cod_mg_l": "cod",
    "influent_bod_mg_l": "bod",
    "influent_tss_mg_l": "tss",
    "influent_nh4_mg_l": "nh4",
    "influent_tp_mg_l": "tp",
    "feed_tds_mg_l": "tds",
    "feed_conductivity_us_cm": "conductivity",
    "feed_turbidity_ntu": "turbidity",
}

# Output field names by pollutant category
_OUTPUT_FIELDS = {
    "cod": ["effluent_cod_mg_l", "permeate_cod_mg_l"],
    "bod": ["effluent_bod_mg_l"],
    "tss": ["effluent_tss_mg_l"],
    "nh4": ["effluent_nh4_mg_l"],
    "tp": ["effluent_tp_mg_l"],
    "tds": ["permeate_tds_mg_l"],
    "conductivity": ["permeate_conductivity_us_cm"],
    "turbidity": ["permeate_turbidity_ntu"],
}


def _identify_unit_type(unit_iri: str) -> str:
    """Identify unit type from IRI for removal lookup."""
    for unit_type in _DEFAULT_REMOVALS.keys():
        if unit_type in unit_iri:
            return unit_type
    return ""


def _apply_removals(
    inputs: Dict[str, float], removals: Dict[str, float]
) -> Dict[str, float]:
    """Apply removal fractions to input concentrations.

    Args:
        inputs: Input concentrations (influent_* or feed_* fields).
        removals: Removal fractions by pollutant category.

    Returns:
        Output concentrations after applying removals.
    """
    outputs: Dict[str, float] = dict(inputs)

    for in_field, pollutant in _POLLUTANT_MAP.items():
        if in_field in inputs and pollutant in removals:
            removal_frac = removals[pollutant]
            in_val = inputs[in_field]
            out_val = in_val * (1 - removal_frac)

            # Map to appropriate output field
            for out_field in _OUTPUT_FIELDS.get(pollutant, []):
                outputs[out_field] = round(out_val, 4)

    # Flow conservation (assume no losses for lumped model)
    if "influent_flow_m3d" in inputs:
        outputs["effluent_flow_m3d"] = inputs["influent_flow_m3d"]
        outputs["permeate_flow_m3d"] = inputs["influent_flow_m3d"]

    return outputs


def lumped_simulate(request: CompositionRequest) -> Dict[str, Any]:
    """Execute lumped composition: algebraic removal without HTTP calls.

    Uses default removal efficiencies for each sub-unit type identified
    in the sub_unit_iris list. Applies removals sequentially.

    Args:
        request: CompositionRequest with sub_unit_iris and inputs.

    Returns:
        Dictionary with:
        - final_outputs: Output after all removal steps
        - intermediate_outputs: List of output dicts from each step
        - removal_summary: Dict showing removal fractions applied
        - composition_strategy: "lumped"

    Note:
        This is a fast fallback that requires no external service calls.
        Results may differ from physics-based cascade due to simplified
        first-order assumptions.
    """
    current_inputs: Dict[str, float] = dict(request.inputs)
    intermediate_outputs: List[Dict[str, Any]] = []
    removal_summary: Dict[str, Dict[str, float]] = {}

    for i, sub_iri in enumerate(request.sub_unit_iris):
        unit_type = _identify_unit_type(sub_iri)
        removals = _DEFAULT_REMOVALS.get(unit_type, {})

        # Apply removals to get step output
        step_output = _apply_removals(current_inputs, removals)

        # Record what was applied
        removal_summary[f"step_{i}"] = {
            "unit_iri": sub_iri,
            "unit_type": unit_type,
            "removals_applied": dict(removals),
        }

        intermediate_outputs.append(step_output)

        # Map outputs to next step's inputs
        next_inputs: Dict[str, float] = {}
        for key, value in step_output.items():
            # Map effluent back to influent naming for next step
            if key.startswith("effluent_"):
                next_key = key.replace("effluent_", "influent_")
                next_inputs[next_key] = value
            elif key.startswith("permeate_"):
                # Map permeate to feed for RO-style outputs
                if "flow" in key:
                    next_inputs["influent_flow_m3d"] = value
                elif "tds" in key:
                    next_inputs["feed_tds_mg_l"] = value
                elif "conductivity" in key:
                    next_inputs["feed_conductivity_us_cm"] = value
                elif "turbidity" in key:
                    next_inputs["feed_turbidity_ntu"] = value
            else:
                next_inputs[key] = value

        current_inputs = next_inputs

    return {
        "final_outputs": intermediate_outputs[-1]
        if intermediate_outputs
        else current_inputs,
        "intermediate_outputs": intermediate_outputs,
        "removal_summary": removal_summary,
        "composition_strategy": "lumped",
        "n_steps": len(request.sub_unit_iris),
    }

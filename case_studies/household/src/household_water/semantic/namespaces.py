"""RDF namespace definitions and field→IRI mappings for household models."""
from rdflib import Namespace

WF   = Namespace("https://ugentbiomath.github.io/waterframe#")
CAP  = Namespace("https://ugentbiomath.github.io/waterframe/capability#")
HC1  = Namespace("https://ugentbiomath.github.io/ontology/index.ttl#")
CASE = Namespace("https://w3id.org/waterframe/case/household/")

MBR_VAR_IRIS = {
    "effluent_cod_mg_l":      WF.EffluentCOD,
    "biomass_x_mg_l":         WF.BiomassConcentration,
    "dissolved_o2_mg_l":      WF.DissolvedOxygen,
    "cod_removal_pct":        WF.CODRemovalEfficiency,
    "energy_kwh_d":           WF.EnergyConsumption,
    "sludge_production_kg_d": WF.SludgeProduction,
    "effluent_flow_m3d":      WF.EffluentFlow,
    "effluent_tss_mg_l":      WF.EffluentTSS,
    "effluent_nh4_mg_l":      WF.EffluentNH4,
    "effluent_tp_mg_l":       WF.EffluentTP,
    "sludge_kg_d":            WF.SludgeProduction,
    "recovery_fraction":      WF.RecoveryFraction,
}

RO_VAR_IRIS = {
    "permeate_flow_m3d":           WF.PermeateFlow,
    "concentrate_flow_m3d":        WF.ConcentrateFlow,
    "permeate_tds_mg_l":           WF.PermeateTDS,
    "permeate_conductivity_us_cm": WF.PermeateConductivity,
    "recovery_fraction":           WF.RecoveryFraction,
    "energy_kwh_d":                WF.EnergyConsumption,
    "water_flux_m_s":              WF.WaterFlux,
    "salt_flux_mol_m2_s":          WF.SaltFlux,
    "osmotic_pressure_pa":         WF.OsmoticPressure,
}

INFILTRATION_VAR_IRIS = {
    "infiltrated_flow_m3d": WF.InfiltratedFlow,
    "removed_cod_fraction": WF.CODRemovalEfficiency,
    "removed_tss_fraction": WF.TSSRemovalEfficiency,
    "removed_nh4_fraction": WF.NH4RemovalEfficiency,
    "effluent_cod_mg_l":    WF.EffluentCOD,
    "effluent_tss_mg_l":    WF.EffluentTSS,
    "effluent_nh4_mg_l":    WF.EffluentNH4,
    "hrt_days":             WF.HydraulicRetentionTime,
}

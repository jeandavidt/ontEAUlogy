"""Stub implementations for water system components.

Provides FastAPI-based stub models for:
- Drinking Water Plants (DWP)
- Wastewater Treatment Plants (WWTP)
- Industries
- Residential Districts
- Rivers/Water Bodies
"""

from .dwp import DrinkingWaterPlantStub
from .wwtp import WastewaterTreatmentPlantStub
from .industry import IndustryStub
from .residential import ResidentialStub
from .river import RiverStub

__all__ = [
    "DrinkingWaterPlantStub",
    "WastewaterTreatmentPlantStub",
    "IndustryStub",
    "ResidentialStub",
    "RiverStub",
]

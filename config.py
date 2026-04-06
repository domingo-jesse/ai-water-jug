from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class EstimationMode(str, Enum):
    CONSERVATIVE = "Conservative"
    MEDIUM = "Medium"
    HIGH = "High"
    CUSTOM = "Custom"


@dataclass(frozen=True)
class ModeAssumption:
    ml_per_1k_tokens: float
    include_indirect_default: bool
    description: str


@dataclass(frozen=True)
class AppConfig:
    mode_defaults: Dict[EstimationMode, ModeAssumption] = field(
        default_factory=lambda: {
            EstimationMode.CONSERVATIVE: ModeAssumption(
                ml_per_1k_tokens=0.5,
                include_indirect_default=False,
                description="Lower-bound heuristic for direct cooling-heavy accounting.",
            ),
            EstimationMode.MEDIUM: ModeAssumption(
                ml_per_1k_tokens=5.0,
                include_indirect_default=True,
                description="Middle-range assumption that blends direct and indirect factors.",
            ),
            EstimationMode.HIGH: ModeAssumption(
                ml_per_1k_tokens=25.0,
                include_indirect_default=True,
                description="Upper-bound scenario where infrastructure impact is higher.",
            ),
        }
    )
    indirect_multiplier: float = 1.6
    default_daily_budget_ml: float = 750.0
    default_bottle_size_ml: float = 500.0
    jug_capacity_ml: float = 3000.0
    eco_streak_increment_threshold_ml: float = 1e-6


APP_CONFIG = AppConfig()

from dataclasses import dataclass
from typing import Dict

from config import APP_CONFIG, EstimationMode


@dataclass
class WaterEstimate:
    user_tokens: int
    assistant_tokens: int
    total_tokens: int
    base_ml: float
    final_ml: float
    mode: str
    include_indirect: bool


class WaterEstimator:
    def __init__(self):
        self.config = APP_CONFIG

    def resolve_assumptions(
        self,
        mode: EstimationMode,
        include_indirect_toggle: bool,
        custom_ml_per_1k_tokens: float,
        custom_include_indirect: bool,
    ) -> Dict:
        if mode == EstimationMode.CUSTOM:
            ml_per_1k = max(0.0, custom_ml_per_1k_tokens)
            include_indirect = custom_include_indirect
        else:
            assumption = self.config.mode_defaults[mode]
            ml_per_1k = assumption.ml_per_1k_tokens
            include_indirect = include_indirect_toggle

        return {
            "ml_per_1k_tokens": ml_per_1k,
            "include_indirect": include_indirect,
            "indirect_multiplier": self.config.indirect_multiplier,
        }

    def estimate_exchange(
        self,
        user_tokens: int,
        assistant_tokens: int,
        mode: EstimationMode,
        include_indirect_toggle: bool,
        custom_ml_per_1k_tokens: float,
        custom_include_indirect: bool,
    ) -> WaterEstimate:
        assumptions = self.resolve_assumptions(
            mode,
            include_indirect_toggle,
            custom_ml_per_1k_tokens,
            custom_include_indirect,
        )
        total_tokens = user_tokens + assistant_tokens
        base_ml = (total_tokens / 1000.0) * assumptions["ml_per_1k_tokens"]
        final_ml = (
            base_ml * assumptions["indirect_multiplier"]
            if assumptions["include_indirect"]
            else base_ml
        )

        return WaterEstimate(
            user_tokens=user_tokens,
            assistant_tokens=assistant_tokens,
            total_tokens=total_tokens,
            base_ml=base_ml,
            final_ml=final_ml,
            mode=mode.value,
            include_indirect=assumptions["include_indirect"],
        )

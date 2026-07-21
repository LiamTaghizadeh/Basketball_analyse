import numpy as np
import pandas as pd


class EffectSizeCalculator:

    @staticmethod
    def calculate_cohens_d(group1, group2):

        group1 = pd.Series(group1).dropna()
        group2 = pd.Series(group2).dropna()

        if len(group1) < 2 or len(group2) < 2:
            raise ValueError(
                "Each group must contain at least two observations."
            )

        n1 = len(group1)
        n2 = len(group2)

        mean1 = group1.mean()
        mean2 = group2.mean()

        std1 = group1.std(ddof=1)
        std2 = group2.std(ddof=1)

        pooled_std = np.sqrt(
            (
                ((n1 - 1) * (std1 ** 2))
                +
                ((n2 - 1) * (std2 ** 2))
            )
            /
            (n1 + n2 - 2)
        )

        if pooled_std == 0:
            raise ValueError(
                "Pooled standard deviation is zero."
            )

        d = (mean1 - mean2) / pooled_std

        return {
            "method": "Cohen's d",
            "effect_size": float(d),
            "absolute_effect_size": float(abs(d)),
            "interpretation": EffectSizeCalculator.interpret_effect_size(d),
            "group1_size": n1,
            "group2_size": n2
        }

    @staticmethod
    def interpret_effect_size(d):

        d = abs(d)

        if d < 0.20:
            return "Negligible Effect"

        elif d < 0.50:
            return "Small Effect"

        elif d < 0.80:
            return "Medium Effect"

        return "Large Effect"
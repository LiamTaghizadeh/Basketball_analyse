import numpy as np
import pandas as pd
from scipy import stats


class ConfidenceIntervalCalculator:

    @staticmethod
    def mean_difference_ci(group1, group2, confidence=0.95):

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

        diff = mean1 - mean2

        # standard error
        se = np.sqrt(
            (group1.var(ddof=1) / n1)
            +
            (group2.var(ddof=1) / n2)
        )

        # degrees of freedom
        df = (
            (group1.var(ddof=1) / n1 +
             group2.var(ddof=1) / n2) ** 2
            /
            (
                ((group1.var(ddof=1) / n1) ** 2) / (n1 - 1)
                +
                ((group2.var(ddof=1) / n2) ** 2) / (n2 - 1)
            )
        )

        alpha = 1 - confidence

        t_value = stats.t.ppf(
            1 - alpha / 2,
            df
        )

        margin_error = t_value * se

        lower = diff - margin_error
        upper = diff + margin_error

        return {
            "method": "Mean Difference Confidence Interval",
            "confidence_level": confidence,
            "mean_difference": float(diff),
            "lower_bound": float(lower),
            "upper_bound": float(upper),
            "sample_size_group1": n1,
            "sample_size_group2": n2
        }
import pandas as pd


class DescriptiveStatistics:

    @staticmethod
    def summarize(data):

        data = pd.Series(data).dropna()

        if len(data) == 0:
            raise ValueError(
                "No data available."
            )

        return {
            "sample_size": int(len(data)),
            "mean": float(data.mean()),
            "std": float(data.std(ddof=1)),
            "min": float(data.min()),
            "q1": float(data.quantile(0.25)),
            "median": float(data.median()),
            "q3": float(data.quantile(0.75)),
            "max": float(data.max())
        }
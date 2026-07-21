import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import shapiro, mannwhitneyu
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class StaticalAnalysis:

    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, alpha: float = 0.05):
        self.df1 = df1
        self.df2 = df2
        self.alpha = alpha

    def shapiro(self, df_num: int, column_name: str):
        target_df = self.df1 if df_num == 1 else self.df2
        statistic, p_value = shapiro(target_df[column_name])
        return {
            "test": "Shapiro-Wilk",
            "statistic": statistic,
            "p_value": p_value,
            "is_normal": p_value >= self.alpha,
        }

    def plot_kde_boxplot_side_by_side(self, col1: str, col2: str = None,
                                       label1: str = "Group 1", label2: str = "Group 2"):
        if col2 is None:
            col2 = col1

        series1 = self.df1[col1]
        series2 = self.df2[col2]

        kde1 = stats.gaussian_kde(series1)
        kde2 = stats.gaussian_kde(series2)

        x_min = min(series1.min(), series2.min())
        x_max = max(series1.max(), series2.max())
        x_vals = np.linspace(x_min, x_max, 500)

        y_vals1 = kde1(x_vals)
        y_vals2 = kde2(x_vals)

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=(
                f"KDE Comparison - {col1} vs {col2}",
                f"Box Plot Comparison - {col1} vs {col2}",
            ),
        )

        # Both KDEs overlaid on the same panel
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals1,
                mode="lines",
                name=label1,
                fill="tozeroy",
                line=dict(color="royalblue"),
                opacity=0.6,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals2,
                mode="lines",
                name=label2,
                fill="tozeroy",
                line=dict(color="indianred"),
                opacity=0.6,
            ),
            row=1,
            col=1,
        )

        # Both boxplots placed side by side on the same panel
        fig.add_trace(
            go.Box(
                y=series1,
                name=label1,
                boxpoints="outliers",
                marker_color="royalblue",
            ),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Box(
                y=series2,
                name=label2,
                boxpoints="outliers",
                marker_color="indianred",
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title_text=f"Distribution Comparison: {col1} vs {col2}",
            showlegend=True,
            template="plotly_white",
            height=500,
        )

        fig.show()

    def smart_hypothesis_test(self, col1: str, col2: str):
        g1 = self.df1[col1]
        g2 = self.df2[col2]

        _, p_norm1 = stats.shapiro(g1)
        _, p_norm2 = stats.shapiro(g2)

        if p_norm1 > self.alpha and p_norm2 > self.alpha:
            _, p_levene = stats.levene(g1, g2)
            equal_var = p_levene > self.alpha

            stat, p_val = stats.ttest_ind(g1, g2, equal_var=equal_var)
            test_name = "Independent t-test" if equal_var else "Welch's t-test"
        else:
            stat, p_val = stats.mannwhitneyu(g1, g2, alternative='two-sided')
            test_name = "Mann-Whitney U test"

        return {
            "test_used": test_name,
            "statistic": stat,
            "p_value": p_val,
            "normality_p_values": (p_norm1, p_norm2)
        }

    def z_score(self, df_num: int, column_name: str):
        target_df = self.df1 if df_num == 1 else self.df2
        return stats.zscore(target_df[column_name])

    def plot_top_players(self, name_column: str, value_column: str,
                          title: str = None, top_n: int = None):
        data = self.df1[[name_column, value_column]].copy()

        if top_n:
            data = data.head(top_n)

        data_sorted = data.sort_values(value_column, ascending=True)

        fig = go.Figure()

        # Stems: a thin line from 0 to each player's value
        for _, row in data_sorted.iterrows():
            fig.add_shape(
                type="line",
                x0=0,
                x1=row[value_column],
                y0=row[name_column],
                y1=row[name_column],
                line=dict(color="indianred", width=3),
            )

        # Dots at the end of each stem, labeled with the value
        fig.add_trace(
            go.Scatter(
                x=data_sorted[value_column],
                y=data_sorted[name_column],
                mode="markers+text",
                marker=dict(size=20, color="indianred", line=dict(width=2, color="darkred")),
                text=data_sorted[value_column],
                textposition="middle right",
                textfont=dict(size=13, color="darkred"),
                name=value_column,
            )
        )

        fig.update_layout(
            title_text=title or f"{value_column.replace('_', ' ').title()} by Player",
            xaxis_title=value_column.replace('_', ' ').title(),
            yaxis_title="Player",
            template="plotly_white",
            showlegend=False,
            height=400,
            margin=dict(l=140, r=60, t=60, b=40),
        )

        fig.show()

        return data_sorted

import pandas as pd
from scipy.stats import  shapiro, ttest_ind, mannwhitneyu, f_oneway, kruskal, chi2_contingency


class StatisticalTester:
    
    def __init__(self, alpha=0.05):
        self.alpha = alpha

    def is_normal(self, data):
        data = data.dropna()
        return shapiro(data).pvalue >= self.alpha

    def two_period_test( self, df, value_column, hypothesis_name, group_column="period_group", alternative="greater"):
        
        past = df[df[group_column] == "past_period"][value_column].dropna()
        recent = df[df[group_column] == "recent_period"][value_column].dropna()

        if self.is_normal(past) and self.is_normal(recent):
            test_name = "Welch t-test"
            stat, p_value = ttest_ind( recent, past, equal_var=False, alternative=alternative)
        else:
            test_name = "Mann-Whitney U"
            stat, p_value = mannwhitneyu( recent, past, alternative=alternative )

        return {
            "hypothesis_name": hypothesis_name,
            "test_type": "two_period_comparison",
            "selected_test": test_name,
            "statistic": stat,
            "p_value": p_value,
            "is_significant": p_value < self.alpha,
            "past_mean": past.mean(),
            "recent_mean": recent.mean(),
            "mean_difference": recent.mean() - past.mean(),
            "past_count": len(past),
            "recent_count": len(recent)
        }

    def multi_group_test( self, df, value_column, group_column, hypothesis_name ):
        groups = [
            group[value_column].dropna()
            for _, group in df.groupby(group_column)
        ]

        groups = [
            group
            for group in groups
            if len(group) >= 3
        ]

        if all(self.is_normal(group) for group in groups):
            test_name = "One-way ANOVA"
            stat, p_value = f_oneway(*groups)
        else:
            test_name = "Kruskal-Wallis"
            stat, p_value = kruskal(*groups)

        group_summary = df.groupby(group_column)[value_column].agg( ["count", "mean", "median"] )

        return {
            "hypothesis_name": hypothesis_name,
            "test_type": "multi_group_comparison",
            "selected_test": test_name,
            "statistic": stat,
            "p_value": p_value,
            "is_significant": p_value < self.alpha,
            "group_summary": group_summary
        }

    def chi_square_test( self, df, row_column, column_column, hypothesis_name):
        
        table = pd.crosstab(df[row_column], df[column_column])
        stat, p_value, dof, _ = chi2_contingency(table)

        return {
            "hypothesis_name": hypothesis_name,
            "test_type": "categorical_dependency",
            "selected_test": "Chi-square test",
            "statistic": stat,
            "p_value": p_value,
            "degrees_of_freedom": dof,
            "is_significant": p_value < self.alpha,
            "contingency_table": table
        }

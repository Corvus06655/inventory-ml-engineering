import pandas as pd
from scipy.stats import ttest_ind
from sklearn.metrics import classification_report


METRICS = [
    "invoice_quantity",
    "invoice_dollars",
    "Freight",
    "days_po_to_invoice",
    "days_to_pay",
    "total_brand",
    "total_quantity",
    "total_dollar",
    "avg_receving_dely",
]


def detect(model, x_test, y_test, model_name):
    """Evaluate a classifier using a classification report."""
    pred = model.predict(x_test)

    print(f"\nModel: {model_name}")
    print(classification_report(y_test, pred))


def feature_significance(df):
    """
    Compare flagged and normal invoices using Welch's t-test.
    Returns significant features, non-significant features, and results.
    """
    flagged = df[df["flagged_invoice"] == 1]
    normal = df[df["flagged_invoice"] == 0]

    significant_features = []
    non_significant_features = []
    results = []

    for metric in METRICS:
        flagged_mean = flagged[metric].mean()
        normal_mean = normal[metric].mean()

        t_stat, p_value = ttest_ind(
            flagged[metric].dropna(),
            normal[metric].dropna(),
            equal_var=False,
        )

        if p_value < 0.05:
            significant_features.append(metric)
            results.append(
                {
                    "metrics": metric,
                    "flagged_mean": round(flagged_mean, 2),
                    "normal_mean": round(normal_mean, 2),
                    "p_value": round(p_value, 3),
                }
            )
        else:
            non_significant_features.append(metric)

    return significant_features, non_significant_features, results


def show_feature_importance(model, feature_names):
    """Return Random Forest feature importance as a sorted DataFrame."""
    feature_importance = pd.DataFrame(
        {
            "Feature": feature_names,
            "importance": model.feature_importances_,
        }
    ).sort_values(by="importance", ascending=False)

    return feature_importance

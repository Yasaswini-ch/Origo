import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from .feature_extraction import FeatureExtractor


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_CSV = DATA_DIR / "training_data.csv"
SUCCESS_MODEL_PATH = MODELS_DIR / "success_predictor.pkl"
MODEL_COMPARISON_REPORT = REPORTS_DIR / "model_comparison.txt"
CONFUSION_MATRIX_PNG = REPORTS_DIR / "confusion_matrix.png"


def load_data():
    df = pd.read_csv(TRAIN_CSV)
    return df


def build_feature_matrix(df: pd.DataFrame):
    extractor = FeatureExtractor()
    features = []
    for _, row in df.iterrows():
        fv = extractor.transform_to_list(
            row["input_idea"],
            row["input_features"],
            row["input_stack"],
        )
        features.append(fv)
    X = np.array(features, dtype=float)
    y = df["success"].astype(int).values
    return X, y


def train_models(X_train, X_test, y_train, y_test):
    results = []

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "svm_rbf": SVC(kernel="rbf", probability=True, random_state=42),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        conf = confusion_matrix(y_test, y_pred)

        results.append(
            {
                "name": name,
                "model": model,
                "accuracy": acc,
                "report": report,
                "confusion_matrix": conf,
            }
        )

    return results


def save_confusion_matrix(conf_matrix: np.ndarray, labels: list[str]):
    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(conf_matrix, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(conf_matrix.shape[1]),
        yticks=np.arange(conf_matrix.shape[0]),
        xticklabels=labels,
        yticklabels=labels,
        ylabel="True label",
        xlabel="Predicted label",
        title="Confusion Matrix",
    )

    thresh = conf_matrix.max() / 2.0 if conf_matrix.max() > 0 else 0.5
    for i in range(conf_matrix.shape[0]):
        for j in range(conf_matrix.shape[1]):
            ax.text(
                j,
                i,
                format(conf_matrix[i, j], "d"),
                ha="center",
                va="center",
                color="white" if conf_matrix[i, j] > thresh else "black",
            )

    fig.tight_layout()
    fig.savefig(CONFUSION_MATRIX_PNG)
    plt.close(fig)


def save_model_comparison(results):
    lines: list[str] = []
    lines.append("Model comparison for success prediction\n")

    for res in results:
        name = res["name"]
        acc = res["accuracy"]
        report = res["report"]
        lines.append(f"Model: {name}")
        lines.append(f"Accuracy: {acc:.4f}")
        lines.append("Precision / Recall / F1-score:")
        for label in ["0", "1", "weighted avg"]:
            if label in report:
                metrics = report[label]
                lines.append(
                    f"  {label}: precision={metrics['precision']:.4f}, "
                    f"recall={metrics['recall']:.4f}, f1={metrics['f1-score']:.4f}"
                )
        lines.append("")

    best = max(results, key=lambda r: r["accuracy"])
    lines.append("Best model:")
    lines.append(f"  Name: {best['name']}")
    lines.append(f"  Accuracy: {best['accuracy']:.4f}")

    if hasattr(best["model"], "feature_importances_"):
        lines.append("  Feature importances (from RandomForest):")
        importances = best["model"].feature_importances_
        feature_names = [
            "prompt_length",
            "word_count",
            "feature_count",
            "num_technologies",
            "has_react",
            "has_fastapi",
        ]
        for name, score in zip(feature_names, importances):
            lines.append(f"    {name}: {score:.4f}")

    with MODEL_COMPARISON_REPORT.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    df = load_data()
    X, y = build_feature_matrix(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = train_models(X_train, X_test, y_train, y_test)

    # Save best model
    best = max(results, key=lambda r: r["accuracy"])
    joblib.dump(best["model"], SUCCESS_MODEL_PATH)

    # Save confusion matrix for best model
    save_confusion_matrix(best["confusion_matrix"], labels=["failure", "success"])

    # Save text report
    save_model_comparison(results)

    print(f"Saved best success model to {SUCCESS_MODEL_PATH}")
    print(f"Saved model comparison report to {MODEL_COMPARISON_REPORT}")
    print(f"Saved confusion matrix plot to {CONFUSION_MATRIX_PNG}")


if __name__ == "__main__":
    main()

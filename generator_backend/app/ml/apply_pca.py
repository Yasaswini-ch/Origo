from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from .feature_extraction import FeatureExtractor


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_CSV = DATA_DIR / "training_data.csv"
PCA_MODEL_PATH = MODELS_DIR / "pca_model.pkl"
PCA_PLOT_PATH = REPORTS_DIR / "pca_visualization.png"


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


def main():
    df = load_data()
    X, y = build_feature_matrix(df)

    pca = PCA(n_components=2, random_state=42)
    X_reduced = pca.fit_transform(X)

    joblib.dump(pca, PCA_MODEL_PATH)

    fig, ax = plt.subplots(figsize=(6, 5))
    scatter = ax.scatter(
        X_reduced[:, 0],
        X_reduced[:, 1],
        c=y,
        cmap="bwr",
        alpha=0.7,
        edgecolors="k",
    )
    legend = ax.legend(
        handles=scatter.legend_elements()[0],
        labels=["Failure", "Success"],
        title="Outcome",
    )
    ax.add_artist(legend)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("PCA of Project Feature Space")
    fig.tight_layout()
    fig.savefig(PCA_PLOT_PATH)
    plt.close(fig)

    print(f"Saved PCA model to {PCA_MODEL_PATH}")
    print(f"Saved PCA visualization to {PCA_PLOT_PATH}")


if __name__ == "__main__":
    main()

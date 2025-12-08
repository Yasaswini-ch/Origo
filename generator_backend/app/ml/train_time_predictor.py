from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from .feature_extraction import FeatureExtractor


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_CSV = DATA_DIR / "training_data.csv"
TIME_MODEL_PATH = MODELS_DIR / "time_predictor.pkl"
ACTUAL_PREDICTED_PNG = REPORTS_DIR / "actual_vs_predicted.png"


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
    y = df["generation_time_seconds"].astype(float).values
    return X, y


def train_models(X_train, X_test, y_train, y_test):
    results = []

    models = {
        "linear_regression": LinearRegression(),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=200, random_state=42
        ),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        # Older sklearn versions may not support the 'squared' argument, so
        # we compute RMSE manually from MSE for compatibility.
        mse = mean_squared_error(y_test, y_pred)
        rmse = float(np.sqrt(mse))
        r2 = r2_score(y_test, y_pred)

        results.append(
            {
                "name": name,
                "model": model,
                "mae": mae,
                "rmse": rmse,
                "r2": r2,
                "y_test": y_test,
                "y_pred": y_pred,
            }
        )

    return results


def save_actual_vs_predicted_plot(y_true: np.ndarray, y_pred: np.ndarray):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(y_true, y_pred, alpha=0.7)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", label="Ideal")
    ax.set_xlabel("Actual generation time (s)")
    ax.set_ylabel("Predicted generation time (s)")
    ax.set_title("Actual vs Predicted Generation Time")
    ax.legend()
    fig.tight_layout()
    fig.savefig(ACTUAL_PREDICTED_PNG)
    plt.close(fig)


def main():
    df = load_data()
    X, y = build_feature_matrix(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    results = train_models(X_train, X_test, y_train, y_test)

    # For regression, we pick the best model based on lowest RMSE
    best = min(results, key=lambda r: r["rmse"])
    joblib.dump(best["model"], TIME_MODEL_PATH)

    save_actual_vs_predicted_plot(best["y_test"], best["y_pred"])

    print(f"Saved best time prediction model to {TIME_MODEL_PATH}")
    print(f"Saved actual vs predicted plot to {ACTUAL_PREDICTED_PNG}")

    print("\nModel performance:")
    for res in results:
        print(f"Model: {res['name']}")
        print(f"  MAE: {res['mae']:.4f}")
        print(f"  RMSE: {res['rmse']:.4f}")
        print(f"  R^2: {res['r2']:.4f}")


if __name__ == "__main__":
    main()

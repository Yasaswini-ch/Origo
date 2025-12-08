# Origo ML Module (app/ml)

This folder contains the ML components used to predict:

- The probability that a code generation will **succeed**.
- The estimated **generation time** in seconds.

The backend can call a single prediction interface to show these estimates to users
*before* starting a generation.

## Folder Structure

- `create_sample_data.py` — generate synthetic training data.
- `feature_extraction.py` — `FeatureExtractor` to convert text to numeric features.
- `train_success_predictor.py` — train 3 classification models, save best.
- `train_time_predictor.py` — train 2 regression models, save best.
- `apply_pca.py` (optional) — run PCA and visualize the feature space.
- `predictor.py` — `GenerationPredictor` interface for backend.
- `data/` — training CSVs.
- `models/` — saved `.pkl` models.
- `reports/` — evaluation reports and plots.

All paths below are relative to the repo root: `generator_backend/app/ml/`.

---

## 1. Environment Setup

From the repo root (`windsurf-project-2`):

```bash
py -3.11 -m venv venv
# PowerShell
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements-dev.txt
pip install scikit-learn joblib matplotlib pandas
```

---

## 2. Generate Synthetic Training Data

```bash
python -m generator_backend.app.ml.create_sample_data
```

This will create:

- `generator_backend/app/ml/data/training_data.csv` with ~150 samples.

Simple vs complex projects are simulated as:

- Simple ideas → higher success rate, shorter times.
- Complex ideas → lower success rate, longer times.

---

## 3. Train Classification Models (Success Prediction)

```bash
python -m generator_backend.app.ml.train_success_predictor
```

This script:

1. Loads `data/training_data.csv`.
2. Uses `FeatureExtractor` to build feature vectors:
   - `prompt_length`
   - `word_count`
   - `feature_count`
   - `num_technologies`
   - `has_react`
   - `has_fastapi`
3. Splits into 80/20 train/test.
4. Trains 3 models:
   - Logistic Regression
   - Random Forest Classifier (100 trees)
   - SVM (RBF kernel)
5. Evaluates accuracy, precision, recall, F1, confusion matrix.
6. Saves the **best** model by accuracy to:
   - `models/success_predictor.pkl`
7. Saves reports to:
   - `reports/model_comparison.txt`
   - `reports/confusion_matrix.png`

---

## 4. Train Regression Models (Time Prediction)

```bash
python -m generator_backend.app.ml.train_time_predictor
```

This script:

1. Loads `data/training_data.csv`.
2. Uses the same features as classification.
3. Target: `generation_time_seconds`.
4. Splits into 80/20 train/test.
5. Trains 2 models:
   - Linear Regression
   - Random Forest Regressor
6. Evaluates:
   - MAE (Mean Absolute Error)
   - RMSE (Root Mean Squared Error)
   - R² score
7. Saves the **best** model by lowest RMSE to:
   - `models/time_predictor.pkl`
8. Saves a scatter plot to:
   - `reports/actual_vs_predicted.png`

---

## 5. Optional: PCA Visualization

```bash
python -m generator_backend.app.ml.apply_pca
```

This script:

1. Builds the same feature matrix as above.
2. Applies PCA with `n_components=2`.
3. Saves the PCA model to:
   - `models/pca_model.pkl`
4. Saves a 2D scatter plot colored by success/failure to:
   - `reports/pca_visualization.png`

This is primarily for visualization / syllabus coverage.

---

## 6. Prediction Interface for Backend

Use `GenerationPredictor` to get predictions inside the FastAPI backend.

```python
from generator_backend.app.ml.predictor import GenerationPredictor

predictor = GenerationPredictor()
result = predictor.predict(
    idea="Build a CRM for freelancers",
    features="contacts, deals, proposals",
    stack="react fastapi postgres",
)

# Example result structure:
# {
#     "success_probability": 0.85,
#     "estimated_time_seconds": 12.3,
#     "confidence": "high",  # high / medium / low
# }
```

`GenerationPredictor` will:

1. Load `models/success_predictor.pkl` and `models/time_predictor.pkl`.
2. Use `FeatureExtractor` to transform `(idea, features, stack)` into the 6D feature vector.
3. Return a dictionary with:
   - `success_probability` — float in `[0, 1]`.
   - `estimated_time_seconds` — float.
   - `confidence` — `"high" | "medium" | "low"` based on success probability.

Backend can expose this via endpoints such as:

- `POST /predict` with JSON body `{ idea, features, stack }`.

---

## 7. Typical Backend Flow

1. Frontend collects user inputs for idea, features, tech stack.
2. Backend calls `GenerationPredictor.predict(...)` with these fields.
3. Backend returns prediction payload to frontend.
4. Frontend shows: `85% chance of success, estimated 12s` before running the full generation.

---

## 8. Retraining Workflow

When real generation logs become available:

1. Construct a new CSV with the same schema as `training_data.csv`.
2. Replace or add it under `data/`.
3. Rerun:
   - `python -m generator_backend.app.ml.train_success_predictor`
   - `python -m generator_backend.app.ml.train_time_predictor`
4. (Optional) Rerun `python -m generator_backend.app.ml.apply_pca`.
5. Restart the backend so it reloads the new models.

import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor


def build_preprocessor(categorical_cols, numeric_cols):
    cat_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='MISSING')),
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse=False))
    ])

    num_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    preprocessor = ColumnTransformer([
        ('cat', cat_pipe, categorical_cols),
        ('num', num_pipe, numeric_cols)
    ], remainder='drop')

    return preprocessor


def train_models(X: pd.DataFrame, y_reg: pd.Series, y_clf: pd.Series, categorical_cols, numeric_cols, output_dir: str):
    p = Path(output_dir)
    p.mkdir(parents=True, exist_ok=True)

    pre = build_preprocessor(categorical_cols, numeric_cols)

    # Classification model for Win probability
    clf = Pipeline([
        ('pre', pre),
        ('model', XGBClassifier(n_estimators=200, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss', random_state=42))
    ])

    clf.fit(X, y_clf)

    # Regression model for BidAmount
    reg = Pipeline([
        ('pre', pre),
        ('model', XGBRegressor(n_estimators=200, learning_rate=0.05, random_state=42))
    ])

    reg.fit(X, y_reg)

    # Save artifacts
    joblib.dump(clf, p / 'win_model.joblib')
    joblib.dump(reg, p / 'bid_model.joblib')
    # Save preprocessor separately
    joblib.dump(pre, p / 'preprocessor.joblib')
    print(f"Saved models to {p}")

    return {'clf': p / 'win_model.joblib', 'reg': p / 'bid_model.joblib', 'pre': p / 'preprocessor.joblib'}


def load_models(model_dir: str):
    p = Path(model_dir)
    clf = joblib.load(p / 'win_model.joblib')
    reg = joblib.load(p / 'bid_model.joblib')
    pre = joblib.load(p / 'preprocessor.joblib')
    return clf, reg, pre

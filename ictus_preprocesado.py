import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from imblearn.over_sampling import SMOTE

from ictus_utils import (
    NUMERIC_COLS, CATEGORICAL_COLS, BINARY_COLS, TARGET_COL,
    RANDOM_STATE, TEST_SIZE, KNN_NEIGHBORS, SMOTE_K_NEIGHBORS, CAT_IMPUTER_FILL,
)


def preprocesar_ictus(df: pd.DataFrame):
    """
    Preprocesa el dataset de ictus.
    Devuelve: X_train, X_test, y_train, y_test, X_clean
    X_clean tiene las columnas tras OHE (necesario para reindexar el paciente nuevo).
    """
    df = df.copy()

    # ── 1. Separar target ──
    y = df[TARGET_COL].copy()
    X = df.drop(columns=[TARGET_COL])

    # ── 2. Imputar categóricas con valor fijo (antes del OHE) ──
    for col in CATEGORICAL_COLS:
        if col in X.columns:
            X[col] = X[col].fillna(CAT_IMPUTER_FILL)

    # ── 3. One-Hot Encoding de variables categóricas ──
    X = pd.get_dummies(X, columns=CATEGORICAL_COLS, drop_first=False)

    # ── 4. Asegurar que binarias sean numéricas ──
    for col in BINARY_COLS:
        if col in X.columns:
            X[col] = pd.to_numeric(X[col], errors="coerce")

    # ── 5. Imputar valores nulos numéricos con KNN ──
    cols_num = [c for c in X.columns
                if c in NUMERIC_COLS + BINARY_COLS or X[c].dtype in [float, int]]
    imputer = KNNImputer(n_neighbors=KNN_NEIGHBORS)
    X[cols_num] = imputer.fit_transform(X[cols_num])

    # ── 6. Guardar estructura de columnas para reindexar paciente nuevo ──
    X_clean = X.copy()

    # ── 7. Train/Test split estratificado ───
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # ── 8. SMOTE para corregir el fuerte desbalanceo (~4.8% positivos) ──
    try:
        smote = SMOTE(k_neighbors=SMOTE_K_NEIGHBORS, random_state=RANDOM_STATE)
        X_train, y_train = smote.fit_resample(X_train, y_train)
    except Exception:
        # Si hay muy pocas muestras en algún fold, continuar sin SMOTE
        pass

    return X_train, X_test, y_train, y_test, X_clean

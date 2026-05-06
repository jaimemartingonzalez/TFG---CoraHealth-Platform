

import pandas as pd
import streamlit as st
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTENC
from utils import (NUMERIC_COLS, CATEGORICAL_COLS, TARGET_COL,
                   RANDOM_STATE, TEST_SIZE, KNN_NEIGHBORS, SMOTE_K_NEIGHBORS,
                   CAT_IMPUTER_FILL)
import joblib
from utils import BASE_DIR

@st.cache_data(show_spinner="ð§ Imputando y limpiando datos...")
def preprocesar(df: pd.DataFrame):
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # 1. Numericas: KNN Imputer
    X_num = X[NUMERIC_COLS].apply(pd.to_numeric, errors='coerce')
    imputer_num = KNNImputer(n_neighbors=KNN_NEIGHBORS)
    X_num_imp = pd.DataFrame(
        imputer_num.fit_transform(X_num),
        columns=NUMERIC_COLS, index=X.index
    )

    # 2. Categoricas: Imputer "Unknown" 
    X_cat = X[CATEGORICAL_COLS].copy().astype(str)
    imputer_cat = SimpleImputer(strategy="constant", fill_value=CAT_IMPUTER_FILL)
    X_cat_imp = pd.DataFrame(
        imputer_cat.fit_transform(X_cat),
        columns=CATEGORICAL_COLS, index=X.index
    )

    # 3. Combinar 
    X_clean_raw = pd.concat([X_num_imp, X_cat_imp], axis=1)

    # 4. Train / Test split 
    X_train, X_test, y_train, y_test = train_test_split(
        X_clean_raw, y, test_size=TEST_SIZE,
        random_state=RANDOM_STATE, stratify=y
    )

    # 5. SMOTE-NC (trabaja con las categorias como texto)
    cat_idx = [X_clean_raw.columns.get_loc(c) for c in CATEGORICAL_COLS]
    smote_nc = SMOTENC(
        categorical_features=cat_idx,
        random_state=RANDOM_STATE,
        k_neighbors=SMOTE_K_NEIGHBORS
    )
    X_train_smote, y_train_smote = smote_nc.fit_resample(X_train, y_train)

    # 6. One-Hot Encoding Final 
    # Convertimos todo a numeros (0/1) para que el modelo no de error
    # Concatenamos temporalmente para asegurar que train y test tengan las mismas columnas
    X_combined = pd.concat([X_train_smote, X_test])
    X_combined_encoded = pd.get_dummies(X_combined, columns=CATEGORICAL_COLS, drop_first=True)
    
    # Separamos de nuevo
    X_train_final = X_combined_encoded.iloc[:len(X_train_smote)].copy()
    X_test_final = X_combined_encoded.iloc[len(X_train_smote):].copy()

    # X_clean tambien debe estar encodeado para que coincida con lo que el modelo espera
    X_clean_encoded = pd.get_dummies(X_clean_raw, columns=CATEGORICAL_COLS, drop_first=True)

    ruta_columnas = BASE_DIR / "models" / "columnas_modelo.joblib"
    if not ruta_columnas.exists():
        joblib.dump(list(X_train_final.columns), ruta_columnas)
  

    return X_train_final, X_test_final, y_train_smote, y_test, X_clean_encoded

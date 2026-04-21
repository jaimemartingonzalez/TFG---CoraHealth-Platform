

import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from utils import RANDOM_STATE, BEST_WEIGHT_RF

@st.cache_resource(show_spinner="🌲 Entrenando Random Forest...")
def entrenar(_X_train, _y_train):
    """
    @st.cache_resource: el modelo entrenado se comparte entre sesiones.
    Prefijo _ → Streamlit no intenta hashear los arrays numpy.
    """
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight=BEST_WEIGHT_RF,   
        criterion="log_loss",
        n_jobs=-1,
        random_state=RANDOM_STATE
    )
    modelo.fit(_X_train, _y_train)
    return {
        "modelo": modelo,
        "scaler": None,
        "features": list(_X_train.columns)
        }

def predecir(resultado: dict, X):                 
    return (
        resultado["modelo"].predict(X),
        resultado["modelo"].predict_proba(X)[:, 1]
    )

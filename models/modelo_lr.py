
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from utils import RANDOM_STATE

@st.cache_resource(show_spinner="📈 Entrenando Regresión Logística...")
def entrenar(_X_train, _y_train):
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(_X_train)
    modelo = LogisticRegression(
        random_state=RANDOM_STATE,
        max_iter=1000,
        class_weight="balanced"   
    )
    modelo.fit(X_sc, _y_train)
    return {                                      
        "modelo":   modelo,
        "scaler":   scaler,                       
        "features": list(_X_train.columns)
    }
def predecir(resultado: dict, X):                
    X_sc = resultado["scaler"].transform(X)
    return (
        resultado["modelo"].predict(X_sc),
        resultado["modelo"].predict_proba(X_sc)[:, 1]
    )


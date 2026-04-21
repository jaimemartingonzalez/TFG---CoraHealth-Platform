import streamlit as st
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from utils import RANDOM_STATE

@st.cache_resource(show_spinner="🧠 Entrenando Red Neuronal MLP...")
def entrenar(_X_train, _y_train):
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(_X_train)
    modelo = MLPClassifier(
        hidden_layer_sizes=(100, 50),
        activation="relu",
        solver="adam",
        alpha=0.001,
        max_iter=500,
        random_state=RANDOM_STATE,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        tol=1e-4
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
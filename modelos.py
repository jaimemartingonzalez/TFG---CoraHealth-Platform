import joblib
import importlib
import streamlit as st
from sklearn.metrics import (roc_auc_score,
                              log_loss, accuracy_score, f1_score,
                              precision_score, recall_score)
from utils import MODELOS_DISPONIBLES, BASE_DIR

MODELS_DIR = BASE_DIR / "models"

@st.cache_resource(show_spinner="⚙️ Cargando modelo...")
def cargar_modelo(nombre: str) -> dict:
    ruta = MODELS_DIR / f"{MODELOS_DISPONIBLES[nombre]}.joblib"
    if not ruta.exists():
        st.error(f"❌ Modelo '{nombre}' no encontrado. Reinicia la app para entrenarlo.")
        st.stop()
    resultado = joblib.load(ruta)
    resultado.setdefault("scaler",   None)
    resultado.setdefault("features", None)
    return resultado

@st.cache_resource(show_spinner=False)
def cargar_columnas_modelo():
    ruta_columnas = MODELS_DIR / "columnas_modelo.joblib"
    if not ruta_columnas.exists():
        st.error("❌ Columnas del modelo no encontradas. Reinicia la app.")
        st.stop()
    return joblib.load(ruta_columnas)

METRICAS_CONFIG = [
    {"nombre": "Accuracy",        "fn": lambda yt, p, pr: round(accuracy_score(yt, p), 3)},
    {"nombre": "Sensibilidad(1)", "fn": lambda yt, p, pr: round(recall_score(yt, p, pos_label=1, zero_division=0), 3)},
    {"nombre": "Especificidad(0)","fn": lambda yt, p, pr: round(recall_score(yt, p, pos_label=0, zero_division=0), 3)},
    {"nombre": "F1(1)",           "fn": lambda yt, p, pr: round(f1_score(yt, p, pos_label=1, zero_division=0), 3)},
    {"nombre": "Precision(1)",    "fn": lambda yt, p, pr: round(precision_score(yt, p, pos_label=1, zero_division=0), 3)},
    {"nombre": "AUC-ROC",         "fn": lambda yt, p, pr: round(roc_auc_score(yt, pr), 3)},
    {"nombre": "Log-Loss",        "fn": lambda yt, p, pr: round(log_loss(yt, pr), 3)},
]

def calcular_metricas(y_test, preds, probas) -> dict:
    return {m["nombre"]: m["fn"](y_test, preds, probas) for m in METRICAS_CONFIG}

def entrenar_y_evaluar(nombre: str, X_train, X_test, y_train, y_test):
    ruta = MODELS_DIR / f"{MODELOS_DISPONIBLES[nombre]}.joblib"

    if not ruta.exists():
        with st.spinner(f"⏳ Entrenando {nombre} por primera vez..."):
            modulo = importlib.import_module(MODELOS_DISPONIBLES[nombre])
            resultado = modulo.entrenar(X_train, y_train)

            # Validar estructura del dict antes de guardar
            assert "modelo"   in resultado, f"{nombre}: falta clave 'modelo'"
            assert "scaler"   in resultado, f"{nombre}: falta clave 'scaler'"
            assert "features" in resultado, f"{nombre}: falta clave 'features'"

            joblib.dump(resultado, ruta)

    resultado = cargar_modelo(nombre)
    modulo = importlib.import_module(MODELOS_DISPONIBLES[nombre])
    preds, probas = modulo.predecir(resultado, X_test)  

    metricas = calcular_metricas(y_test, preds, probas)
    
    return resultado, preds, probas, metricas

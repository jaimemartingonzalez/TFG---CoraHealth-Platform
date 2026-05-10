import joblib
import importlib
import sys
import streamlit as st
from sklearn.metrics import classification_report, roc_auc_score, log_loss

from ictus_utils import MODELOS_DISPONIBLES_ICTUS, BASE_DIR

MODELS_DIR = BASE_DIR / "models"
sys.path.insert(0, str(BASE_DIR))

@st.cache_resource(show_spinner="⚙️ Cargando modelo de ictus...")
def cargar_modelo_ictus(nombre: str) -> dict:
    nombre_archivo = MODELOS_DISPONIBLES_ICTUS[nombre].split(".")[-1]
    ruta = MODELS_DIR / f"{nombre_archivo}.joblib"
    if not ruta.exists():
        st.error(f"❌ Modelo '{nombre}' no encontrado. Reinicia la app para entrenarlo.")
        st.stop()
    resultado = joblib.load(ruta)
    resultado.setdefault("scaler", None)
    resultado.setdefault("features", None)
    return resultado


@st.cache_resource(show_spinner=False)
def cargar_columnas_modelo_ictus():
    ruta_columnas = MODELS_DIR / "columnas_modelo_ictus.joblib"
    if not ruta_columnas.exists():
        st.error("❌ Columnas del modelo de ictus no encontradas. Reinicia la app.")
        st.stop()
    return joblib.load(ruta_columnas)


def entrenar_y_evaluar_ictus(nombre: str, X_train, X_test, y_train, y_test):
    nombre_archivo = MODELOS_DISPONIBLES_ICTUS[nombre].split(".")[-1]
    ruta = MODELS_DIR / f"{nombre_archivo}.joblib"

    if not ruta.exists():
        with st.spinner():
            modulo = importlib.import_module(MODELOS_DISPONIBLES_ICTUS[nombre])
            resultado = modulo.entrenar(X_train, y_train)

            assert "modelo" in resultado,   f"{nombre}: falta clave 'modelo'"
            assert "scaler" in resultado,   f"{nombre}: falta clave 'scaler'"
            assert "features" in resultado, f"{nombre}: falta clave 'features'"

            joblib.dump(resultado, ruta)

    resultado = cargar_modelo_ictus(nombre)
    modulo = importlib.import_module(MODELOS_DISPONIBLES_ICTUS[nombre])
    preds, probas = modulo.predecir(resultado, X_test)

    rep = classification_report(
        y_test, preds, output_dict=True,
        target_names=["No Ictus", "Ictus"]
    )
    metricas = {
        "Accuracy":        round(rep["accuracy"], 3),
        "Sensibilidad(1)": round(rep["Ictus"]["recall"], 3),
        "Especificidad(0)":round(rep["No Ictus"]["recall"], 3),
        "F1(1)":           round(rep["Ictus"]["f1-score"], 3),
        "AUC-ROC":         round(roc_auc_score(y_test, probas), 3),
        "Precision(1)":    round(rep["Ictus"]["precision"], 3),
        "Log-Loss":        round(log_loss(y_test, probas), 3),
    }
    return resultado, preds, probas, metricas

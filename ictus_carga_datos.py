
import pandas as pd
import streamlit as st
from ictus_utils import DATA_PATH, NUMERIC_COLS


@st.cache_data(show_spinner="📂 Cargando base de datos de ictus (~5.000 pacientes)...")
def cargar_datos_ictus() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(f"❌ No se encontró el CSV en: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH, low_memory=False, encoding='utf-8')

    # Eliminar columna id (no aporta información predictiva)
    if "id" in df.columns:
        df.drop(columns=["id"], inplace=True)

    # bmi tiene "N/A" como string → convertir a numérico
    df["bmi"] = pd.to_numeric(df["bmi"], errors="coerce")

    # Resto de numéricas
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ever_married: "Yes"/"No" → 1/0
    if "ever_married" in df.columns:
        df["ever_married"] = df["ever_married"].map({"Yes": 1, "No": 0})

    if "smoking_status" in df.columns:
        df["smoker"] = df["smoking_status"].apply(
            lambda x: 1 if str(x).strip().lower() in ["smokes", "formerly smoked"] else 0
        )
        df.drop(columns=["smoking_status"], inplace=True)

    return df


@st.cache_data(show_spinner=False)
def obtener_estadisticas_ictus(df: pd.DataFrame) -> dict:
    return {
        "shape": df.shape,
        "nulos": df.isnull().sum().to_dict(),
        "describe": df.describe().to_dict(),
        "distribucion_target": df["stroke"].value_counts(normalize=True).to_dict(),
    }

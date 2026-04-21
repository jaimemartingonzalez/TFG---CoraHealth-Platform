
import pandas as pd
import streamlit as st
from utils import DATA_PATH, NUMERIC_COLS

@st.cache_data(show_spinner="ðŸ“‚ Cargando historiales clí­nicos (~92k pacientes)...")
def cargar_datos() -> pd.DataFrame():
    if not DATA_PATH.exists():
        st.error(f"❌ No se encontró el CSV en: {DATA_PATH}")
        st.stop()
    df = pd.read_csv(DATA_PATH, low_memory=False, encoding='utf-8')
    # Recorremos solo las columnas que sabemos que DEBEN ser números
    for col in NUMERIC_COLS:
        if col in df.columns:
            # Convierte el '-' en NaN y el resto en números reales
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    for col in ["smoking", "alcohol_use"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = 1 - df[col]   # invierte 0↔1
            
    return df

@st.cache_data(show_spinner=False)
def obtener_estadisticas(df: pd.DataFrame) -> dict:
    return {
        "shape": df.shape,
        "nulos": df.isnull().sum().to_dict(),
        "describe": df.describe().to_dict(),
        "distribucion_target": df["heartdisease"].value_counts(normalize=True).to_dict(),
    }

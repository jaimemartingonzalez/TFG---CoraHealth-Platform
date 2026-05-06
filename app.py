import streamlit as st
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(page_title="CoraHealth", page_icon="❤️", layout="wide")

# Navegación con nombres personalizados en el panel lateral
pg = st.navigation([
    st.Page("pages/inicio.py",                     title="🏠 Inicio"),
    st.Page("pages/informacion_cardiovascular.py",  title="📚 Información CardioVascular Relevante"),
    st.Page("pages/riesgo_cv.py",                  title="💗 Predicción Riesgo CV"),
    st.Page("pages/riesgo_ictus.py",               title="🧠 Riesgo Ictus (BETA)"),
])

# Disclaimer 
if "disclaimer_ok" not in st.session_state:
    st.session_state.disclaimer_ok = False

if not st.session_state.disclaimer_ok:
    st.markdown("""
        <div style="background-color:#FFDE21; color:#000; padding:2rem;
            border:6px solid #ffa442; border-radius:15px; margin:2rem 0;
            box-shadow:0 4px 12px rgba(0,0,0,0.2); text-align:center;">
            <h2 style='color:#000; margin-bottom:1rem;'>⚠️ Aviso importante ⚠️</h2>
            <p style='font-size:1.1rem; line-height:1.6; color:#000;'>
                Esta es solo una herramienta de apoyo al diagnóstico.<br>
                <strong>No sustituye en ningún momento el criterio médico.</strong><br>
                Siempre consulta tus resultados con un profesional sanitario.
            </p>
        </div>
    """, unsafe_allow_html=True)

    aceptado = st.checkbox("✅ OK, lo he entendido", key="chk_disclaimer")
    if st.button("Continuar a ❤️ CoraHealth ❤️"):
        if aceptado:
            st.session_state.disclaimer_ok = True
            st.rerun()
        else:
            st.error("Debes marcar \"OK, lo he entendido\" para continuar.")
else:
    pg.run()

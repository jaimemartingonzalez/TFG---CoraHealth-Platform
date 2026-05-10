import streamlit as st
from pathlib import Path
import sys
import base64
from utils import BASE_DIR

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.markdown("""
        <style>
            .main-content {
                background-color: #FF6961; /* Rojo-pastel */
                color: white;
                padding: 2rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: center;
            }
            .image-gallery img {
                cursor: pointer;
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-content"><h1>¡Bienvenido a la plataforma CoraHealth! </h1><p>La plataforma pensada para ayudar a mejorar tu salud cardiovascular.</p></div>', unsafe_allow_html=True)



st.write ("")
st.write ("")

st.write ("El corazón es la bomba de la vida! Por ello siempre queremos ayudar a mejorar tu salud, para que te encuentres mejor y hagas más fácil tu vida y la de los tuyos!")
ruta_video = BASE_DIR / "images" / "sistema_cardiovascular.mp4"
video_b64 = base64.b64encode(ruta_video.read_bytes()).decode()
st.markdown(f"""
<div style="
    display: flex;
    justify-content: center;
    align-items: center;
    height: 50vh;
">
    <video autoplay loop muted playsinline
        style="width: 50%; height: auto; border-radius: 10px;">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)


st.write("Recuerda que ésta no es una herramienta de diagnóstico, está pensada para ayudar a la toma de decisiones, no ha de sustituirla.")



# Desplegable con las opciones
OPT_CV   = "Calculadora Riesgo Enfermedad CardioVascular"
OPT_INFO = "Información importante sobre las enfermedades cardiovasculares"
OPT_ICTUS = "Calculadora Riesgo de ICTUS (BETA version)"

opcion = st.selectbox("Selecciona la página a la que quieres dirigirte:", [OPT_INFO, OPT_CV, OPT_ICTUS])

if st.button("Continuar"):
    if opcion == OPT_INFO:
        st.switch_page("pages/informacion_cardiovascular.py")
    elif opcion == OPT_CV:
        st.switch_page("pages/riesgo_cv.py")
    elif opcion == OPT_ICTUS:
        st.switch_page("pages/riesgo_ictus.py")





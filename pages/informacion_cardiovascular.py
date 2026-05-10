import streamlit as st
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import IMAGES_DIR


st.set_page_config(page_title="❤️ Enfermedades Cardiovasculares - Importancia", page_icon="👨‍⚕️", layout="wide")

st.markdown("""
    <style>
        .rosa-box { background-color: #FF6961; color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; text-align: center; }
        .texto-seccion { font-size: 1.1rem; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="rosa-box"><h1>Enfermedades Cardiovasculares</h1>', unsafe_allow_html=True)



def seccion_texto_media(texto, media_file, titulo_media, subtitulo_media, texto_derecha=False):
    """
    Muestra texto + imagen O vídeo (detecta automáticamente por extensión).
    Si es vídeo, oculta la barra de controles.
    Formatos imagen: jpg, jpeg, png, gif
    Formatos vídeo: mp4, mov, avi, webm
    """
    EXTENSIONES_VIDEO = {'.mp4', '.mov', '.avi', '.webm'}
    EXTENSIONES_IMAGEN = {'.jpg', '.jpeg', '.png', '.gif'}

    extension = Path(media_file).suffix.lower()
    media_path = IMAGES_DIR / media_file

    def render_media():
        if extension in EXTENSIONES_VIDEO:
            st.html("""
                <style>
                    video::-webkit-media-controls { display: none !important; }
                    video::-webkit-media-controls-panel { display: none !important; }
                    video::-webkit-media-controls-play-button { display: none !important; }
                </style>
            """)
            st.video(str(media_path), loop=True, autoplay=True, muted=True)
            if titulo_media:
                st.caption(titulo_media)
            if subtitulo_media:
                st.caption(subtitulo_media)
        elif extension in EXTENSIONES_IMAGEN:
            st.image(str(media_path), caption=titulo_media, width="content")
            if subtitulo_media:
                st.caption(subtitulo_media)
        else:
            st.error(f"❌ Formato no soportado: {extension}")

    cols = st.columns(2)
    if texto_derecha:
        with cols[0]:
            render_media()
        with cols[1]:
            st.markdown(texto, unsafe_allow_html=True)
    else:
        with cols[0]:
            st.markdown(texto, unsafe_allow_html=True)
        with cols[1]:
            render_media()




seccion_texto_media(
    """
    El sistema cardiovascular es una red vital que transporta sangre, oxígeno y nutrientes a todos los tejidos del cuerpo humano, mientras elimina desechos como el dióxido de carbono. Está compuesto por el corazón (la bomba principal), los vasos sanguíneos (arterias, venas y capilares) y la sangre misma, funcionando como un circuito cerrado de alta presión para mantener la homeostasis y el metabolismo celular.<br> <br>
    
    El corazón, un órgano muscular del tamaño de un puño ubicado en el centro del tórax, late unas 100.000 veces al día bombeando 7.500 litros de sangre a través de cuatro cavidades: aurículas y ventrículos derechos e izquierdos. La sangre oxigenada sale del ventrículo izquierdo por la aorta hacia los órganos, mientras la desoxigenada regresa al ventrículo derecho vía venas cavas para reoxigenarse en los pulmones; esta sincronía rítmica asegura que cada célula reciba lo necesario para sobrevivir. <br> <br>
    
    Es por ello que es fundamental que funcione correctamente nuestro sistema cardiovascular, ya que si no, no llega el oxígeno ni los nutrientes a las células de nuestro cuerpo, dañando diferentes órganos y pudiendo causar diferentes complicaciones.
    """,
    "corazon_latiendo.mp4",  
    "",
    ""
)


st.markdown('<div class="rosa-box"><h2>Infarto de Miocardio</h2></div>', unsafe_allow_html=True) # Título sección de Infarto de Miocardio

seccion_texto_media(
    """
    El infarto de miocardio es la muerte de las células musculares del corazón que se encarga de bombear la sangre al resto del cuerpo. La causa principal de un infarto de miocardio es la aterosclerosis, una acumulación de placa grasa y colesterol en las arterias coronarias, que puede romperse y formar un coágulo que bloquea el flujo sanguíneo al corazón.
    """,
    "aterosclerosis.jpg",
    "Obstrucción en arteria coronaria",
    ""
)

st.markdown('<div class="rosa-box"><h2>Ictus - Accidente Cerebrovascular</h2></div>', unsafe_allow_html=True) # Título sección Ictus

seccion_texto_media(
    """
    <br> 
    
    El ictus, también conocido como accidente cerebrovascular o derrame, sucede cuando se interrumpe el flujo sanguíneo al cerebro por distintas causas. Los síntomas aparecen bruscamente y requieren atención inmediata.
    
    
    Pese a la detección temprana, sus consecuencias varían, pero incluyen afasia (alteración del habla), hemiparesia (parálisis de la mitad del cuerpo), déficits cognitivos, alteraciones emocionales y, en el peor caso, la muerte.
    """,
    "ictus.jpg",
    "",
    "",
    texto_derecha=True
)

seccion_texto_media(
    """
    <br> 
    
    Cuando se interrumpa el flujo sanguíneo al cerebro por una obstrucción se denomina ictus isquémico, puede ser por la presencia de un trombo (taponamiento de los vasos del cerebro) o por la presencia de un émbolo (taponamiento de un vaso lejos del cerebro pero que impide el correcto flujo de la sangre hacia él.)
    
    Cuando se interrumpa el flujo sanguíneo al cerebro por una rotrura de una arteria se denomia ictus hemorrágico, puede además causar cefálea y alteraciones en la coagulación sanguínea.
    """,
    "ictus_types.png",
    "Ictus isquémico por trombo (izquierda) e ictus hemorrágico (derecha)",
    "",
    texto_derecha=True
)


st.markdown('<div class="rosa-box"><h2>Estadísticas de incidencia globales</h2></div>', unsafe_allow_html=True) # Título sección Incidencia



seccion_texto_media(
    """
    <br> 
    
    El infarto de miocardio ocurre por obstrucción de las arterias coronarias, impidiendo el flujo sanguíneo al corazón, mientras que el ictus resulta de bloqueos o rupturas en vasos cerebrales, causando daños neurológicos graves.
    
    Ambas son prevenibles en un 80% mediante control de factores como hipertensión, tabaquismo, obesidad y dieta inadecuada, pero su detección tardía agrava el pronóstico. Más del 75% de estas muertes suceden en países de ingresos bajos y medios, donde el acceso a atención primaria es limitado. 
    
    Según la OMS, en 2022 estas patologías provocaron 19,8 millones de fallecimientos, equivalentes al 32% de todas las muertes globales, con el 85% atribuidas directamente a infartos e ictus.<br><br>
    <strong>Importancia Clínica:</strong> 
    
    Ambas son prevenibles en un 80% mediante control de factores como hipertensión, tabaquismo, obesidad y dieta inadecuada, pero su detección tardía agrava el pronóstico. Más del 75% de estas muertes suceden en países de ingresos bajos y medios.
    """,
    "causes_deaths.png",
    "Causas anuales de muerte según la OMS (2016)",
    "Las enfermedades cardiovasculares se sitúan en el primer lugar, cada año aumentando"
)

seccion_texto_media(
    """
    <strong>Incidencia Mundial (diferencia de 20 años):</strong> 
    
    En el año 2000 se dieron 6.8 millones de muertes por enfermedad cardiovascular, mientras en en 2019 ese número aunmentó hasta 9 millones de muertes, un 30% más. 
    
    En cuanto al ictus, podemos ver que aumentó de 5.5 millones a 6.2 millones de muertes anuales en 20 años. 
    
    Sólo por estas dos causas, su suma da más de 15 millones de muertes anuales, sin contar con las severas complicaciones que provocan y que posteriormente conducen a la muerte. 
    
    Se puede observar cómo claramente las enfermedades Cardiovasculares y el Ictus constituyen las 2 primeras causas de muerte, y que en 20 años han aumentado 
    """,
    "causes_deaths_2.png",
    "Comparativa de la OMS de causas de muertes globales pasadas 2 décadas",
    "",
    texto_derecha=True
)


seccion_texto_media(
    """
    <strong>Gasto en el tratamiento de estas patologías:</strong> 
    
    Las ECV imponen una carga económica masiva: en la Unión Europea, cuestan 210.000 millones de euros anuales a sistemas sanitarios y sociales, afectando a 50 millones de personas.
    
    Globalmente, los gastos en tratamiento, hospitalizaciones y pérdida de productividad superan los cientos de miles de millones
    
    Con optimizaciones en prevención secundaria que podrían evitar 67.170 muertes anuales en siete países europeos. Invertir en control de riesgos reduce esta carga de forma rentable, además de mejorar la calidad de vida de los pacientes de forma drástica.
    """,
    "spending_cv_disease.png",
    "",
    "Gasto anual de la Unión Europera en tratar enfermedades cardiovasculares",
    texto_derecha=True
)


# Pie de página
st.markdown('<div class="rosa-box"><p>Fuentes: OMS, AHA, Fundación Española del Corazón. Datos actualizados a febrero 2026.</p></div>', unsafe_allow_html=True)


# Crear columnas para poner el botón de regreso al inicio centrado
left_spacer, center_col, right_spacer = st.columns([1, 0.3, 1])

with center_col:
    if st.button("Volver al inicio"): 
        st.switch_page("pages/inicio.py")



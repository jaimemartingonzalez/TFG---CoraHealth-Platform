import streamlit as st
import sys
import warnings
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib



warnings.filterwarnings('ignore')

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from carga_datos import cargar_datos
from preprocesado import preprocesar
from modelos import entrenar_y_evaluar
from utils import NUMERIC_COLS, CATEGORICAL_COLS, MODELOS_DISPONIBLES, IMAGES_DIR, BASE_DIR
from visualizador import (mostrar_comparativa_paciente, mostrar_selector_rango_edad)
import importlib


TRADUCCION_COLUMNAS = {
    "age":               "Edad (años)",
    "resting_bp":        "Tensión arterial (mmHg)",
    "cholesterol":       "Colesterol (mg/dL)",
    "maxhr":             "FC máxima (bpm)",
    "weight":            "Peso (kg)",
    "height":            "Altura (cm)",
    "glucose":           "Glucosa (mg/dL)",
}

# ── Configuración ──
st.set_page_config(page_title="Riesgo CV", page_icon="💗", layout="wide")
    

st.title("💗 Predicción del Riesgo Cardiovascular")
st.write("Sube tus datos, obtén tu predicción y compara tu perfil con la media global de ~92.000 pacientes.")

def calcular_imputaciones_por_edad(df: pd.DataFrame, edad: int, delta: int) -> dict:
    df_rango = df[df["age"].between(edad - delta, edad + delta)]
    
    if len(df_rango) < 10:
        df_rango = df
        fallback = True
    else:
        fallback = False

    maxhr_imp = float(pd.to_numeric(df_rango["maxhr"], errors='coerce').median())
    ecg_imp   = str(df_rango["RestingECG"].dropna().mode()[0]) \
                if not df_rango["RestingECG"].dropna().empty else "Normal"
    slope_imp = str(df_rango["ST_Slope"].dropna().mode()[0]) \
                if not df_rango["ST_Slope"].dropna().empty else "Flat"

    return {
        "maxhr_median":     maxhr_imp,
        "resting_ecg_mode": ecg_imp,
        "st_slope_mode":    slope_imp,
        "n_pacientes":      len(df_rango),
        "fallback_global":  fallback
    }


# CARGAR DATOS GLOBALES (instantáneo tras primera carga)

with st.spinner("Cargando base de datos global..."):
    df_global = cargar_datos()
    X_train, X_test, y_train, y_test, X_clean = preprocesar(df_global)


ruta_columnas = BASE_DIR / "models" / "columnas_modelo.joblib"
if not ruta_columnas.exists():
    joblib.dump(list(X_clean.columns), ruta_columnas)


# VALIDACIÓN, antes de cualquier lectura de session_state

CLAVES_ESPERADAS = {"pred", "prob", "campos_imputados", "valores_paciente", "age", "maxhr_final"}
if (
    st.session_state.get("resultado_prediccion") is not None
    and not CLAVES_ESPERADAS.issubset(st.session_state.resultado_prediccion.keys())
):
    st.session_state.resultado_prediccion = None

# Inicializar si no existe
if "resultado_prediccion" not in st.session_state:
    st.session_state.resultado_prediccion = None



# SECCIÓN 1: FORMULARIO DE INTRODUCCIÓN DE DATOS

st.header("🩺 Introduce tus datos clínicos")

st.info("""
**📋 Sobre la precisión de la predicción**

Cuantos más campos rellenes y más precisos sean los valores, 
más fiable será la estimación del modelo. Los campos opcionales 
(sin asterisco) se estiman automáticamente a partir de la media 
poblacional si no se proporcionan, lo que puede reducir la precisión.

> ⚕️ **Esta herramienta tiene fines académicos (TFG) y no sustituye  
> el diagnóstico ni el juicio clínico de un profesional médico.**
""")

nombre_modelo = st.selectbox(
    "🤖 Modelo de predicción:",
    list(MODELOS_DISPONIBLES.keys()),
    key="modelo_prediccion"
)



# ── Inicializar session_state ───
if "resultado_prediccion" not in st.session_state:
    st.session_state.resultado_prediccion = None


# ── CAMPOS OBLIGATORIOS ──
st.markdown("### Datos personales y hábitos")
st.markdown(
    "Los campos marcados con <span style='color:red'>**\\***</span> son **obligatorios**.",
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)
age = c1.number_input(
    "Edad *",
    min_value=10, max_value=110, value=50, step=1,
    help="Edad en años completos (10–110)"
)
sex = c2.selectbox(
    "Sexo *",
    ["M", "F"],
    help="M = Masculino, F = Femenino (sexo biológico)"
)

st.markdown("##### 📏 Medidas corporales")
c3, c4 = st.columns(2)
weight = c3.number_input(
    "Peso (kg) *",
    min_value=30.0, max_value=250.0, value=75.0, step=0.5,
    help="Peso en kilogramos"
)
height = c4.number_input(
    "Altura (cm) *",
    min_value=50.0, max_value=230.0, value=170.0, step=0.5,
    help="Altura en centímetros"
)

st.markdown("##### 🩸 Analítica básica (valores habituales en una analítica estándar)")
c5, c6, c7 = st.columns(3)
restingbp = c5.number_input(
    "Tensión arterial en reposo (mmHg) *",
    min_value=40, max_value=220, value=120, step=1,
    help="Tensión sistólica en reposo. Normal: 90–130 mmHg"
)
cholesterol = c6.number_input(
    "Colesterol total (mg/dL) *",
    min_value=80, max_value=600, value=200, step=1,
    help="Colesterol total. Deseable: <200 mg/dL. Elevado: >240 mg/dL"
)
glucose = c7.number_input(
    "Glucosa en ayunas (mg/dL) *",
    min_value=50, max_value=500, value=90, step=1,
    help="Glucosa en ayunas. Normal: 70–100 mg/dL. Hiperglucemia: >126 mg/dL"
)

st.markdown("##### 🚬 Hábitos de vida")
c8, c9, c10 = st.columns(3)
smoking = c8.selectbox(
    "Tabaquismo *",
    ["No", "Sí"],
    help="¿Fumas actualmente o has fumado de forma habitual?"
)
alcoholuse = c9.selectbox(
    "Consumo de alcohol *",
    ["No (0 veces/semana)", "Sí (>2 veces/semana)"],
    help="¿Cuál es tu consumo actual de alcohol?"
)
physicalactivity = c10.selectbox(
    "Actividad física *",
    ["No (0 veces/semana)", "Sí (>2 veces/semana)"],
    help="¿Practicas ejercicio físico a lo largo de la semana?"
)

# ── CAMPOS OPCIONALES ──
st.markdown("---")
with st.expander(
    "➕ Campos opcionales — requieren pruebas clínicas específicas "
    "(mejorarán notablemente la precisión si los tienes disponibles)"
):
    st.markdown("""
    Estos datos provienen de pruebas que no siempre están disponibles fuera de 
    un entorno clínico. Si no los conoces, déjalos en **"No disponible"** y el 
    modelo usará la media poblacional como estimación.
    """)

    maxhr_option = st.checkbox(
        "Tengo el dato de Frecuencia Cardíaca Máxima (prueba de esfuerzo)",
        value=False,
        key="maxhr_checkbox"
    )
    maxhr = None
    if maxhr_option:
        maxhr = st.number_input(
            "FC máxima alcanzada (bpm)",
            min_value=60, max_value=220, value=150, step=1,
            help="Frecuencia cardíaca máxima en una prueba de esfuerzo. "
                 "Estimación orientativa: 220 − edad"
        )

    col_ecg1, col_ecg2 = st.columns(2)
    RestingECG_opt = col_ecg1.selectbox(
        "ECG en reposo",
        ["No disponible", "Normal", "ST", "LVH"],
        help="ST = alteración del segmento ST   ||   LVH = hipertrofia ventricular izquierda. "
             "Requiere electrocardiograma a interpretación por parte de un profesional sanitario."
    )
    STSlope_opt = col_ecg2.selectbox(
        "Pendiente del segmento ST (prueba de esfuerzo)",
        ["No disponible", "↑", "---", "↓"],
        help="↑ = ascendente (normal)   ||   --- = plana   ||   ↓ = descendente (patológico). "
             "Requiere electrocardiograma de esfuerzo."
    )

# ── AVISO Y BOTÓN ───
st.caption(
    "🔴 * Campo obligatorio. "
    "Si algún valor obligatorio parece fuera de rango, aparecerá un aviso tras enviar."
)



# ── Selector de abanico de edad para imputación ──
st.markdown("##### 🎯 Rango de edad para imputar campos opcionales")

delta_imputacion = st.slider(
    "Abanico de edad (± años respecto a tu edad):",
    min_value=2,     
    max_value=20,
    value=2,
    step=1,
    key="delta_imputacion",
    help="Se usarán pacientes con edades entre las edades seleccionadas años para imputar."
)

edad_min_imp = max(18, age - delta_imputacion)
edad_max_imp = min(110, age + delta_imputacion)
rango_total  = edad_max_imp - edad_min_imp + 1

# ── Aviso de fiabilidad según el abanico ──
if delta_imputacion <= 7:
    st.success(
        f"✅ Abanico ajustado ({edad_min_imp}–{edad_max_imp} años, ±{delta_imputacion} años): "
        "imputación precisa con pacientes de edad muy similar a la tuya."
    )
elif delta_imputacion <= 13:
    st.warning(
        f"⚠️ Abanico moderado ({edad_min_imp}–{edad_max_imp} años, ±{delta_imputacion} años): "
        "la imputación introduce algo de variabilidad. La predicción puede ser algo menos precisa."
    )
else:
    st.error(
        f"🔴 Abanico amplio ({edad_min_imp}–{edad_max_imp} años, ±{delta_imputacion} años): "
        "alta variabilidad en la imputación. Se recomienda introducir los campos opcionales "
        "manualmente para mejorar la fiabilidad de la predicción."
    )

# ── Calcular imputaciones con el delta seleccionado ──
imputaciones = calcular_imputaciones_por_edad(df_global, age, delta=delta_imputacion)

# Mostrar información del grupo resultante
n_pac = imputaciones["n_pacientes"]
if imputaciones["fallback_global"]:
    st.caption(
        f"ℹ️ Menos de 10 pacientes en el rango {edad_min_imp}–{edad_max_imp} años. "
        "Se usa la media global como fallback."
    )
else:
    st.caption(f"👥 Pacientes en el rango seleccionado: **{n_pac:,}**")




submitted = st.button(
    "🚀 Calcular riesgo cardiovascular",
    width='stretch',
    type="primary"
)



# SECCIÓN 2: VALIDACIONES FISIOLÓGICAS + PREDICCIÓN

if submitted:

    st.session_state.delta_confirmado_inf = None
    st.session_state.delta_confirmado_sup = None

    # ── Recalcular imputaciones frescas en el momento del submit ──
    imputaciones = calcular_imputaciones_por_edad(df_global, age, delta=delta_imputacion)

    # ── 1. Asignar valores finales (usuario > imputación) ──
    maxhr_final      = maxhr if maxhr is not None else imputaciones["maxhr_median"]
    RestingECG_final = RestingECG_opt if RestingECG_opt != "No disponible" \
                       else imputaciones["resting_ecg_mode"]
    _st_slope_mode   = imputaciones["st_slope_mode"]  # para el MAP_STSLOPE

    # ── 2. Validaciones fisiológicas (avisan pero no bloquean) ──
    alertas = []

    if restingbp < 90:
        alertas.append("⚠️ Tensión arterial muy baja (<90 mmHg). Verifica que la medición es correcta.")
    elif restingbp > 180:
        alertas.append("⚠️ Tensión arterial muy elevada (>180 mmHg). Consulta con un médico urgentemente.")

    if cholesterol < 100:
        alertas.append("⚠️ Colesterol inusualmente bajo (<100 mg/dL). Confirma el valor de la analítica.")
    elif cholesterol > 300:
        alertas.append("⚠️ Colesterol muy elevado (>300 mg/dL). Se recomienda valoración médica.")

    if glucose < 70:
        alertas.append("⚠️ Glucosa muy baja (<70 mg/dL). Posible hipoglucemia. Verifica la medición.")
    elif glucose > 126:
        alertas.append("⚠️ Glucosa en ayunas elevada (>126 mg/dL). Puede indicar diabetes. Consulta con tu médico.")

    if maxhr is not None:
        maxhr_estimado = 220 - age
        if maxhr > maxhr_estimado + 20:
            alertas.append(
                f"⚠️ FC máxima ({maxhr} bpm) muy por encima de la estimada para tu edad "
                f"({maxhr_estimado} bpm). Confirma el dato."
            )
        elif maxhr < 80:
            alertas.append("⚠️ FC máxima muy baja (<80 bpm). Verifica que el dato es correcto.")

    bmi = weight / ((height / 100) ** 2)
    if bmi > 40:
        alertas.append(f"⚠️ IMC calculado muy elevado ({bmi:.1f}). Verifica peso y altura.")
    elif bmi < 15:
        alertas.append(f"⚠️ IMC calculado muy bajo ({bmi:.1f}). Verifica peso y altura.")

    if alertas:
        st.subheader("⚠️ Avisos sobre los datos introducidos")
        for alerta in alertas:
            st.warning(alerta)
        st.markdown(
            "La predicción se calculará igualmente. "
            "Te recomendamos revisar los valores marcados para mejorar la precisión."
        )

    # ── 3. Mensaje de campos imputados ──
    n_pac  = imputaciones["n_pacientes"]
    rango  = f"{age - delta_imputacion}–{age + delta_imputacion} años ({n_pac:,} pacientes)"
    origen = "media global (pocos datos en tu rango de edad)" \
             if imputaciones["fallback_global"] else f"media del grupo {rango}"

    campos_imputados = []
    if maxhr is None:
        campos_imputados.append(f"FC máxima (imputada con {origen}: {maxhr_final:.0f} bpm)")
    if RestingECG_opt == "No disponible":
        campos_imputados.append(f"ECG en reposo (imputado con {origen}: '{RestingECG_final}')")
    if STSlope_opt == "No disponible":
        campos_imputados.append(f"Pendiente ST (imputada con {origen}: '{_st_slope_mode}')")

    if campos_imputados:
        st.info(
            "📊 **Campos opcionales imputados con la media de la población seleccionada:**\n\n"
            + "\n".join(f"- {c}" for c in campos_imputados)
        )

    # ── 4. Mapeos ──
    MAP_SMOKING    = {"No": 0, "Sí": 1}
    MAP_FRECUENCIA = {"No (0 veces/semana)": 0, "Sí (>2 veces/semana)": 1}
    MAP_STSLOPE    = {
        "No disponible": _st_slope_mode,
        "↑": "Up", "---": "Flat", "↓": "Down"
    }

    smoking_model          = MAP_SMOKING[smoking]
    alcoholuse_model       = MAP_FRECUENCIA[alcoholuse]
    physicalactivity_model = MAP_FRECUENCIA[physicalactivity]
    STSlope_final          = MAP_STSLOPE[STSlope_opt]

    # ── 5. Construir DataFrame del paciente ──
    paciente_dict = {
        "age":               age,
        "resting_bp":        restingbp,
        "cholesterol":       cholesterol,
        "maxhr":             maxhr_final,       
        "weight":            weight,
        "height":            height,
        "glucose":           glucose,
        "RestingECG":        RestingECG_final,  
        "ST_Slope":          STSlope_final,     
        "alcohol_use":       alcoholuse_model,
        "physical_activity": physicalactivity_model,
        "smoking":           smoking_model,
        "sex":               sex,
    }

    df_paciente_raw = pd.DataFrame([paciente_dict])
    for col in CATEGORICAL_COLS:
        if col in df_paciente_raw.columns:
            df_paciente_raw[col] = df_paciente_raw[col].astype(str)
    columnas_modelo = joblib.load(BASE_DIR / "models" / "columnas_modelo.joblib")
    df_paciente_encoded = pd.get_dummies(df_paciente_raw, columns=CATEGORICAL_COLS)
    df_paciente = df_paciente_encoded.reindex(columns=columnas_modelo, fill_value=0)

    # ── 4. Predecir ──
    with st.spinner(f"Calculando predicción con {nombre_modelo}..."):
        modelo_result, preds, probas, metricas = entrenar_y_evaluar(
            nombre_modelo, X_train, X_test, y_train, y_test
        )
        modulo = importlib.import_module(MODELOS_DISPONIBLES[nombre_modelo])
        pred_pac, proba_pac = modulo.predecir(modelo_result, df_paciente)

    #  Guardar en session_state en vez de mostrar directamente
    st.session_state.resultado_prediccion = {
        "pred":             int(pred_pac[0]),
        "prob":             float(proba_pac[0]) * 100,
        "age":              age,           
        "maxhr_final":      maxhr_final,  
        "campos_imputados": campos_imputados,
        "valores_paciente": {
                        "age":         age,
                        "resting_bp":  restingbp,
                        "cholesterol": cholesterol,
                        "maxhr":       maxhr_final,
                        "weight":      weight,
                        "height":      height,
                        "glucose":     glucose,
                    },
    }


    



# Mostrar resultados desde session_state (persiste entre reruns)

if st.session_state.resultado_prediccion is not None:
    r = st.session_state.resultado_prediccion
    age_res         = r.get("age", 50)
    maxhr_final_res = r.get("maxhr_final", 150)
    prob_enfermedad  = r["prob"]
    pred_clase       = r["pred"]
    campos_imputados = r["campos_imputados"]
    valores_paciente = r["valores_paciente"]

    st.divider()
    st.subheader("📊 Resultado de la predicción")

    col_res, col_gauge = st.columns(2)

    # ── Determinar nivel de riesgo y colores ──
    if prob_enfermedad < 40:
        nivel_riesgo  = "BAJO"
        color_barra   = "#2ecc71"      
        color_mensaje = "success"
        icono         = "✅"
    elif prob_enfermedad < 70:
        nivel_riesgo  = "MODERADO"
        color_barra   = "#f39c12"      
        color_mensaje = "warning"
        icono         = "⚠️"
    else:
        nivel_riesgo  = "ALTO"
        color_barra   = "#e74c3c"      
        color_mensaje = "error"
        icono         = "🔴"

    with col_res:
        # ── Mensaje correlacionado con el porcentaje ──
        if color_mensaje == "success":
            st.success(f"{icono} **RIESGO {nivel_riesgo}** de enfermedad cardiovascular")
        elif color_mensaje == "warning":
            st.warning(f"{icono} **RIESGO {nivel_riesgo}** de enfermedad cardiovascular")
        else:
            st.error(f"{icono} **RIESGO {nivel_riesgo}** de enfermedad cardiovascular")
    
        # ── Métrica con icono de información ──
        st.metric(
            label="Probabilidad estimada de enfermedad CV",
            value=f"{prob_enfermedad:.1f}%",
            delta=f"{prob_enfermedad - 43.7:.1f}% vs media global (43.7%)",
            delta_color="inverse",
            help=(
                "Este riesgo refleja la probabilidad estimada de padecer alguna "
                "enfermedad cardiovascular (infarto, insuficiencia cardíaca, arritmias, etc.). "
                "Un valor elevado puede deberse a que el modelo contempla un amplio espectro "
                "de trastornos cardiovasculares.\n\n"
                "⚕️ Esta herramienta tiene fines académicos y NO sustituye el diagnóstico "
                "ni el criterio de un profesional médico. Consulta siempre con tu médico."
            )
        )

    if campos_imputados:
        st.caption(
            "ℹ️ Precisión reducida: algunos campos opcionales fueron estimados "
            "con la media de la población de tu rango de edad."
        )

    with col_gauge:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob_enfermedad,
                number={"suffix": "%", "valueformat": ".1f"},
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": f"Riesgo CV — Nivel {nivel_riesgo}", "font": {"size": 16}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1},
                    "bar": {"color": color_barra, "thickness": 0.3},  # ← color dinámico
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0,  40],  "color": "#a9dfbf"},  
                        {"range": [40, 70],  "color": "#fad7a0"},  
                        {"range": [70, 100], "color": "#f1948a"}, 
                    ],
                }
            ))
            fig_gauge.update_layout(
                height=300,
                margin=dict(t=60, b=60, l=30, r=30),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(
                fig_gauge,
                width='stretch',
                config={"locale": "es"},
                key=f"gauge_{prob_enfermedad:.1f}"
            )

    # Comparativa con media global y grupo de edad
    medias_global = df_global[NUMERIC_COLS].apply(pd.to_numeric, errors='coerce').mean()
    COLS_TABLA = [c for c in NUMERIC_COLS if c in valores_paciente]
    
    comparativa = pd.DataFrame({
        "Variable":     [TRADUCCION_COLUMNAS.get(c, c) for c in COLS_TABLA],  # ← traducidas
        "Paciente":     [valores_paciente[c] for c in COLS_TABLA],
        "Media global": medias_global[COLS_TABLA].values.round(1)
    })
    comparativa["Diferencia (%)"] = (
        (comparativa["Paciente"] - comparativa["Media global"])
        / comparativa["Media global"] * 100
    ).round(1)
    st.dataframe(comparativa.set_index("Variable"), width='stretch')
    
    fig_comp = px.bar(
        comparativa.melt(
            id_vars="Variable",
            value_vars=["Paciente", "Media global"],
            var_name="Grupo", value_name="Valor"
        ),
        x="Variable", y="Valor", color="Grupo",
        barmode="group",
        title="Perfil clínico del paciente vs. media global",
        labels={"Variable": "", "Valor": "Valor clínico"}  # ← etiquetas de ejes en español
    )
    st.plotly_chart(fig_comp, width='stretch', config={"locale": "es"})
    

    st.divider()
    _, _, confirmado = mostrar_selector_rango_edad(df_global, age_res)
    
    if confirmado:
            mostrar_comparativa_paciente(
                df_global,
                edad=age_res,
                valores_paciente=valores_paciente,   
                maxhr_final=maxhr_final_res,
                delta_inf=st.session_state.delta_confirmado_inf,
                delta_sup=st.session_state.delta_confirmado_sup
            )
    
    st.caption(
            "⚕️ **Aviso clínico**: Esta herramienta tiene fines académicos (TFG). "
            "No sustituye el diagnóstico ni el criterio de un profesional médico."
        )



# SECCIÓN 3: INFORMACIÓN DIVULGATIVA

def seccion_texto_imagen(texto, img_file, titulo_img, subtitulo_img, texto_derecha=False):
    img_path = IMAGES_DIR / img_file
    img_width = 600
    cols = st.columns(2)
    if texto_derecha:
        with cols[0]:
            st.image(img_path, caption=titulo_img, width=img_width)
            st.caption(subtitulo_img)
        with cols[1]:
            st.markdown(texto, unsafe_allow_html=True)
    else:
        with cols[0]:
            st.markdown(texto, unsafe_allow_html=True)
        with cols[1]:
            st.image(img_path, caption=titulo_img, width=img_width)
            st.caption(subtitulo_img)



st.divider()

st.info("""
💡 **¿Quieres saber más sobre las enfermedades cardiovasculares?**

Si te interesa entender qué las provoca, qué hábitos aumentan o reducen el riesgo 
y cómo cuidar tu corazón en el día a día, despliega la sección informativa aquí abajo.
""")

with st.expander("📚 Ver información sobre enfermedades cardiovasculares", expanded=False):

    st.subheader("Información básica sobre las enfermedades cardiovasculares")
    st.write("Las enfermedades cardiovasculares forman un grupo amplio de trastornos que afectan al corazón y a los vasos sanguíneos. Son una de las principales causas de enfermedad y mortalidad en el mundo, pero lo interesante es que muchos de sus factores de riesgo están ligados a hábitos modificables.")

    st.subheader("Qué las provoca")
    
    seccion_texto_imagen(
        """
        Hay varios mecanismos, pero el más común es la aterosclerosis, una acumulación de grasa, colesterol y otras sustancias en las paredes de las arterias. Con el tiempo, estas placas pueden:
            
        - <strong> Reducir el flujo sanguíneo: </strong> limita el oxígeno y nutrientes a los tejidos, provocando isquemia y daño cardiaco.
        
        - <strong> Inflamarse</strong>, ya que vuelve la pared arterial más vulnerable.
        
        - <strong> Romperse y formar coágulos que bloquean la circulación:</strong> generan bloqueos súbitos que pueden cortar el riesgo sanguíneo y provocar infartos.


        Otros desencadenantes incluyen:
        - <strong> Hipertensión mantenida:</strong> obliga al corazón a trabajar con más fuerza, dañando vasos y músculo cardiaco.
        
        - <strong> Alteraciones del ritmo cardíaco:</strong> reducen la eficacia del bombeo y comprometen el aporte de sangre.
        
        - <strong> Debilitamiento del músculo cardíaco:</strong> favorece a la insuficiencia cardíaca, porque el corazón no tiene tanta capacidad para bombear sangre.
        
        - <strong> Malformaciones congénitas:</strong> alteran la estructura y flujo normal del corazón, aumentando la carga de trabajo.
        """,
        "aterosclerosis_2.jpg","",""
        )
    st.subheader("Hábitos que influyen en su aparición")

    seccion_texto_imagen(
        """
        Aquí es donde la vida cotidiana pesa muchísimo. Algunos hábitos aumentan el riesgo, mientras que otros lo reducen de forma notable.

        <h5>Hábitos que aumentan el riesgo:</h5>

        - Tabaquismo: daña las arterias y acelera la aterosclerosis.
        
        - Dieta rica en grasas saturadas, azúcares y sal: favorece colesterol alto, hipertensión y obesidad.
        
        - Sedentarismo: reduce la capacidad cardiovascular y favorece el sobrepeso.
        
        - Consumo excesivo de alcohol: puede elevar la presión arterial y los triglicéridos.
        
        - Estrés crónico: contribuye a la inflamación y a la hipertensión.
        
        - Mal descanso: dormir poco o mal se asocia con mayor riesgo cardiovascular.
        """,
        "factores_riesgo.jpg", "", ""
    )

    st.write("")
    st.write("")

    seccion_texto_imagen(
        """
        <h5>Hábitos que protegen el corazón:</h5>

        - Actividad física regular: caminar, correr, nadar o cualquier ejercicio aeróbico mejora la salud vascular.
        
        - Alimentación equilibrada: patrones como la dieta mediterránea ayudan a controlar colesterol, glucosa y presión arterial.
        
        - No fumar: el beneficio empieza casi desde el primer día sin tabaco.
        
        - Control del estrés: técnicas como respiración, mindfulness o actividades placenteras.
        
        - Dormir entre 7 y 9 horas con buena calidad de sueño.
        
        - Revisiones médicas periódicas para detectar hipertensión, diabetes o colesterol elevado.
        """,
        "factores_salud.png", "", "",
        texto_derecha=True
    )
    
    
#%%
# ── Botón volver ──
left_spacer, center_col, right_spacer = st.columns([1, 0.3, 1])
with center_col:
    if st.button("Volver al inicio"):
        st.switch_page("pages/inicio.py")

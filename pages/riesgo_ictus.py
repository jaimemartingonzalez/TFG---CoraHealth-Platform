import streamlit as st
import sys
import warnings
import pandas as pd
import joblib
import importlib
import plotly.graph_objects as go
import plotly.express as px

warnings.filterwarnings("ignore")

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ictus_carga_datos    import cargar_datos_ictus
from ictus_preprocesado   import preprocesar_ictus
from ictus_modelos        import entrenar_y_evaluar_ictus
from ictus_visualizador   import (
    mostrar_resumen_ictus, mostrar_distribucion_numerica_ictus,
    mostrar_distribucion_categorica_ictus, mostrar_correlacion_ictus,
    mostrar_comparativa_paciente_ictus,
    mostrar_selector_rango_edad_ictus,
)
from ictus_utils import (
    NUMERIC_COLS, CATEGORICAL_COLS,
    MODELOS_DISPONIBLES_ICTUS, BASE_DIR)


st.markdown("""
    <style>
        .rosa-box { background-color: #FF6961; color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; text-align: center; }
        .texto-seccion { font-size: 1.1rem; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)


# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(page_title="Riesgo de Ictus", page_icon="🧠", layout="wide")

st.title("🧠 Predicción del Riesgo de Ictus")
st.write("Introduce tus datos clínicos, obtén tu predicción y compara tu perfil "
         "con la base de datos (~5.000 pacientes).")


st.warning("""
    ⚠️ **Limitaciones del modelo predictivo**

    Este modelo ha sido entrenado con un conjunto de datos de tamaño limitado (~5.000 pacientes), 
    condicionado por la escasez de datos clínicos públicos disponibles sobre ictus. 
    Esto puede reducir la precisión de las predicciones en ciertos perfiles de paciente, 
    especialmente en casos poco representados en la base de datos de entrenamiento.

    A pesar de ello, la herramienta está diseñada para actuar como un **apoyo diagnóstico complementario**: 
    puede ayudar a identificar perfiles de riesgo elevado y orientar hacia una atención médica más temprana.

    > ⚕️ **Esta herramienta tiene fines académicos (TFG) y no sustituye en ningún caso 
    > el diagnóstico ni el criterio clínico de un profesional médico. 
    > Ante cualquier duda o síntoma, consulta siempre con tu médico.**
    """)

# ── Función de imputación por edad ──
def calcular_imputaciones_por_edad_ictus(df: pd.DataFrame, edad: int,
                                          delta: int) -> dict:
    df_rango = df[df["age"].between(edad - delta, edad + delta)]
    if len(df_rango) < 10:
        df_rango = df
        fallback = True
    else:
        fallback = False

    glucose_imp = float(pd.to_numeric(
        df_rango["avg_glucose_level"], errors="coerce").median())

    return {
        "glucose_median":  glucose_imp,
        "n_pacientes":     len(df_rango),
        "fallback_global": fallback,
    }



# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS (cacheada)
# ══════════════════════════════════════════════════════════════════════════════

with st.spinner("Cargando base de datos de ictus..."):
    df_global = cargar_datos_ictus()
    X_train, X_test, y_train, y_test, X_clean = preprocesar_ictus(df_global)

ruta_columnas = BASE_DIR / "models" / "columnas_modelo_ictus.joblib"
if not ruta_columnas.exists():
    joblib.dump(list(X_clean.columns), ruta_columnas)

# ── Validar session_state ─────────────────────────────────────────────────────
CLAVES_ESPERADAS = {"pred", "prob", "campos_imputados",
                    "valores_paciente", "age"}
if (
    st.session_state.get("resultado_prediccion_ictus") is not None
    and not CLAVES_ESPERADAS.issubset(
        st.session_state.resultado_prediccion_ictus.keys())
):
    st.session_state.resultado_prediccion_ictus = None

if "resultado_prediccion_ictus" not in st.session_state:
    st.session_state.resultado_prediccion_ictus = None


# SECCIÓN 1: FORMULARIO DE DATOS

st.header("🩺 Introduce tus datos clínicos")
st.info("""
**📋 Sobre la precisión de la predicción**

Cuantos más campos rellenes y más precisos sean los valores,
más fiable será la estimación del modelo. Los campos opcionales
se estiman automáticamente con la media poblacional seleccionada.**
""")

nombre_modelo = st.selectbox(
    "🤖 Modelo de predicción:",
    list(MODELOS_DISPONIBLES_ICTUS.keys()),
    key="modelo_prediccion_ictus",
)

# ── Campos obligatorios ──
st.markdown("### Datos personales")
st.markdown("Los campos marcados con **\\*** son **obligatorios**.")

# ── Mapeos ES → EN (necesarios para que el OHE coincida con el entrenamiento) ──
MAP_GENDER    = {"Hombre": "Male", "Mujer": "Female", "Otro": "Other"}
MAP_WORK_TYPE = {
    "Privado/a":       "Private",
    "Autónomo/a":      "Self-employed",
    "Funcionario/a":   "Govt_job",
    "Menor de edad":   "children",
    "Sin empleo":      "Never_worked",
}
MAP_RESIDENCE = {"Urbana": "Urban", "Rural": "Rural"}
MAP_SMOKING = {
    "No fumador/a (nunca ha fumado)": 0,
    "Fumador/a activo o exfumador/a": 1,
}
MAP_MARRIED = {"Sí": 1, "No": 0}

c1, c2, c3 = st.columns(3)
age = c1.number_input(
    "Edad *", min_value=10, max_value=110, value=50, step=1,
    help="Edad en años completos (10–110)",
)
gender_es = c2.selectbox(
    "Sexo biológico *", list(MAP_GENDER.keys()),
    help="Sexo biológico del paciente",
)
ever_married_es = c3.selectbox(
    "¿Alguna vez casado/a? *", list(MAP_MARRIED.keys()),
    help="Estado civil (historial)",
)

st.markdown("##### 📏 Medidas corporales")
c_w, c_h = st.columns(2)
weight = c_w.number_input(
    "Peso (kg) *", min_value=20.0, max_value=250.0, value=75.0, step=0.5,
    help="Peso en kilogramos (20-250)",
)
height = c_h.number_input(
    "Altura (cm) *", min_value=50.0, max_value=230.0, value=170.0, step=0.5,
    help="Altura en centímetros (50-230)",
)
# Cálculo automático del IMC a partir de peso y altura
bmi_final = round(weight / ((height / 100) ** 2), 1)
st.info(f"📐 **IMC calculado automáticamente:** {bmi_final} kg/m²  "
        f"({'Bajo peso' if bmi_final < 18.5 else 'Normal' if bmi_final < 25 else 'Sobrepeso' if bmi_final < 30 else 'Obesidad'})")

st.markdown("##### 🏥 Antecedentes médicos")
c4, c5 = st.columns(2)
hypertension = c4.selectbox(
    "Hipertensión *", ["No", "Sí"],
    help="¿Tienes o has tenido hipertensión arterial diagnosticada?",
)
heart_disease = c5.selectbox(
    "Enfermedad cardíaca *", ["No", "Sí"],
    help="¿Tienes o has tenido alguna enfermedad cardíaca diagnosticada?",
)

st.markdown("##### 🚬 Tabaquismo")
smoking_es = st.selectbox(
    "Estado de tabaquismo *",
    list(MAP_SMOKING.keys()),
    help="Incluye tanto fumadores activos como exfumadores",
)

st.markdown("##### 💼 Situación laboral y residencia")
c6, c7 = st.columns(2)
work_type_es = c6.selectbox(
    "Tipo de trabajo *", list(MAP_WORK_TYPE.keys()),
    help="Categoría laboral actual",
)
Residence_type_es = c7.selectbox(
    "Tipo de residencia *", list(MAP_RESIDENCE.keys()),
    help="Zona de residencia actual",
)


# ── Campos opcionales ──
st.markdown("---")
with st.expander(
    "➕ Campo opcional — mejora la precisión si lo tienes disponible"
):
    st.markdown("""
    Si no conoces este valor, déjalo sin marcar y el modelo usará
    la mediana de pacientes de edad similar como estimación.
    """)
    glucose_option = st.checkbox(
        "Tengo el dato de glucosa media en sangre (analítica)",
        value=False, key="glucose_checkbox_ictus",
    )
    glucose_val = None
    if glucose_option:
        glucose_val = st.number_input(
            "Glucosa media en sangre (mg/dL)",
            min_value=50.0, max_value=300.0, value=100.0, step=0.5,
            help="Nivel medio de glucosa en sangre. Normal en ayunas: 70–100 mg/dL",
        )


# ── Rango de edad para imputación ──
st.markdown("##### 🎯 Rango de edad para imputar campos opcionales")
delta_imputacion = st.slider(
    "Abanico de edad (± años respecto a tu edad):",
    min_value=2, max_value=25, value=5, step=1,
    key="delta_imputacion_ictus",
    help="Pacientes dentro de este rango se usarán para imputar valores no disponibles.",
)

edad_min_imp = max(1, age - delta_imputacion)
edad_max_imp = min(110, age + delta_imputacion)

if delta_imputacion <= 7:
    st.success(f"✅ Abanico ajustado ({edad_min_imp}–{edad_max_imp} años): "
               "imputación precisa con pacientes de edad muy similar.")
elif delta_imputacion <= 13:
    st.warning(f"⚠️ Abanico moderado ({edad_min_imp}–{edad_max_imp} años): "
               "la imputación introduce algo de variabilidad.")
else:
    st.error(f"🔴 Abanico amplio ({edad_min_imp}–{edad_max_imp} años): "
             "alta variabilidad. Introduce los campos opcionales manualmente.")

imputaciones = calcular_imputaciones_por_edad_ictus(df_global, age,
                                                     delta=delta_imputacion)
n_pac = imputaciones["n_pacientes"]
if imputaciones["fallback_global"]:
    st.caption(f"ℹ️ Menos de 10 pacientes en el rango. Se usa la media global.")
else:
    st.caption(f"👥 Pacientes en el rango seleccionado: **{n_pac:,}**")

submitted = st.button(
    "🚀 Calcular riesgo de ictus",
    width='stretch', type="primary",
)


# SECCIÓN 2: VALIDACIONES + PREDICCIÓN

if submitted:
    st.session_state.delta_confirmado_inf_ictus = None
    st.session_state.delta_confirmado_sup_ictus = None

    imputaciones = calcular_imputaciones_por_edad_ictus(df_global, age,
                                                         delta=delta_imputacion)

    glucose_final = (glucose_val if glucose_val is not None
                    else imputaciones["glucose_median"])

   # ── Validaciones fisiológicas ──
    alertas = []
    if bmi_final > 50:
       alertas.append(f"⚠️ IMC calculado muy elevado ({bmi_final}). "
                      "Verifica que el peso y la altura son correctos.")
    elif bmi_final < 12:
       alertas.append(f"⚠️ IMC calculado muy bajo ({bmi_final}). "
                      "Verifica que el peso y la altura son correctos.")
    if glucose_val is not None:
       if glucose_val < 55:
           alertas.append("⚠️ Glucosa muy baja (<55 mg/dL). Posible hipoglucemia.")
       elif glucose_val > 250:
           alertas.append("⚠️ Glucosa muy elevada (>250 mg/dL). "
                          "Consulta con tu médico.")
    if alertas:
       st.subheader("⚠️ Avisos sobre los datos introducidos")
       for a in alertas:
           st.warning(a)

   # ── Mensaje de campos imputados (solo glucosa puede ser imputada) ──
    campos_imputados = []
    if glucose_val is None:
       n_pac = imputaciones["n_pacientes"]
       rango_str = (f"{age - delta_imputacion}–{age + delta_imputacion} "
                    f"años ({n_pac:,} pac.)")
       origen = ("media global" if imputaciones["fallback_global"]
                 else f"mediana del grupo {rango_str}")
       campos_imputados.append(
           f"Glucosa media (imputada con {origen}: "
           f"{glucose_final:.1f} mg/dL)")
    if campos_imputados:
       st.info(
           "📊 **Campo opcional imputado con la mediana de la "
           "población seleccionada:**\n\n"
           + "\n".join(f"- {c}" for c in campos_imputados)
       )

   # ── Mapeos ES → EN antes de construir el DataFrame del paciente ──
    MAP_BINARIO = {"No": 0, "Sí": 1}

    hypertension_val  = MAP_BINARIO[hypertension]
    heart_disease_val = MAP_BINARIO[heart_disease]
    ever_married_val  = MAP_MARRIED[ever_married_es]

   # ── Construir DataFrame del paciente (valores EN para OHE) ──
    paciente_dict = {
    "age":               age,
    "hypertension":      hypertension_val,
    "heart_disease":     heart_disease_val,
    "ever_married":      ever_married_val,
    "avg_glucose_level": glucose_final,
    "bmi":               bmi_final,
    "smoker":            MAP_SMOKING[smoking_es],   # ← AÑADIR
    "gender":            MAP_GENDER[gender_es],
    "work_type":         MAP_WORK_TYPE[work_type_es],
    "Residence_type":    MAP_RESIDENCE[Residence_type_es],
}


    df_paciente_raw = pd.DataFrame([paciente_dict])

    # Aplicar OHE exactamente igual que en el preprocesado
    for col in CATEGORICAL_COLS:
        if col in df_paciente_raw.columns:
            df_paciente_raw[col] = df_paciente_raw[col].astype(str)

    columnas_modelo = joblib.load(BASE_DIR / "models" / "columnas_modelo_ictus.joblib")
    df_paciente_enc = pd.get_dummies(df_paciente_raw, columns=CATEGORICAL_COLS)
    df_paciente     = df_paciente_enc.reindex(columns=columnas_modelo, fill_value=0)

    # ── Predecir ──
    with st.spinner(f"Calculando predicción con {nombre_modelo}..."):
        modelo_result, preds, probas, metricas = entrenar_y_evaluar_ictus(
            nombre_modelo, X_train, X_test, y_train, y_test
        )
        modulo = importlib.import_module(MODELOS_DISPONIBLES_ICTUS[nombre_modelo])
        pred_pac, proba_pac = modulo.predecir(modelo_result, df_paciente)

    st.session_state.resultado_prediccion_ictus = {
        "pred":             int(pred_pac[0]),
        "prob":             float(proba_pac[0]) * 100,
        "age":              age,
        "campos_imputados": campos_imputados,
        "valores_paciente": {
    # Numéricas
    "age":               age,
    "avg_glucose_level": glucose_final,
    "bmi":               bmi_final,
    # Binarias
    "hypertension":      hypertension_val,
    "heart_disease":     heart_disease_val,
    "ever_married":      ever_married_val,
    # Categóricas (valores EN para que coincidan con el dataset)
    "smoker":            MAP_SMOKING[smoking_es],
    "gender":            MAP_GENDER[gender_es],
    "work_type":         MAP_WORK_TYPE[work_type_es],
    "Residence_type":    MAP_RESIDENCE[Residence_type_es],
},
    }


# MOSTRAR RESULTADOS (desde session_state)

if st.session_state.resultado_prediccion_ictus is not None:
    r = st.session_state.resultado_prediccion_ictus
    prob_ictus  = r["prob"]
    pred_clase  = r["pred"]
    age_res     = r["age"]
    campos_imp  = r["campos_imputados"]
    vals_pac    = r["valores_paciente"]

    
    PREVALENCIA_MEDIA = 4.9 #aproximada

    st.divider()
    st.subheader("📊 Resultado de la predicción")

    if prob_ictus < 15:
        nivel_riesgo = "BAJO"
        msg_riesgo   = "✅ **RIESGO BAJO** de ictus"
        fn_riesgo    = st.success
    elif prob_ictus < 25:
        nivel_riesgo = "MODERADO"
        msg_riesgo   = "⚠️ **RIESGO MODERADO** de ictus"
        fn_riesgo    = st.warning
    else:
        nivel_riesgo = "ELEVADO"
        msg_riesgo   = "🚨 **RIESGO ELEVADO** de ictus"
        fn_riesgo    = st.error

    col_res, col_gauge = st.columns([1, 0.95])   

    with col_res:
        fn_riesgo(msg_riesgo)
        st.metric(
            label="Probabilidad estimada de ictus",
            value=f"{prob_ictus:.1f}%",
            delta=f"{prob_ictus - PREVALENCIA_MEDIA:.1f}% vs media dataset "
                  f"({PREVALENCIA_MEDIA}%)",
            delta_color="inverse",
        )
        if campos_imp:
            st.caption("ℹ️ Precisión reducida: algunos campos fueron estimados "
                       "con la media poblacional.")
    
    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob_ictus,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"Riesgo de sufrir un Ictus<br><span style='font-size:0.8em;color:gray'>Nivel: {nivel_riesgo}</span>"},
            number={"suffix": "%", "font": {"size": 28}},
            gauge={
                "axis": {
                    "range": [0, 50],
                    "tickvals": [0, 15, 25, 50],
                    "ticktext": ["0%", "15%", "25%", "50%"],
                },
                "bar": {
                    "color": (
                        "green"  if prob_ictus < 15 else
                        "orange" if prob_ictus < 25 else
                        "crimson"
                    )
                },
                "steps": [
                    {"range": [0, 15],  "color": "#d4edda"},
                    {"range": [15, 25], "color": "#fff3cd"},
                    {"range": [25, 50], "color": "#f8d7da"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.75,
                    "value": prob_ictus,
                },
            },
        ))
        fig_gauge.update_layout(
            height=240,                                    
            margin=dict(t=60, b=30, l=15, r=15),         
        )
        st.plotly_chart(fig_gauge, width='stretch',
                        config={"locale": "es"},
                        key=f"gauge_ictus_{prob_ictus:.1f}")

    # Comparativa con media global
    TRADUCCION_VARS = {
    "age":               "Edad (años)",
    "avg_glucose_level": "Glucosa media (mg/dL)",
    "bmi":               "IMC (kg/m²)",
}

    medias_global = df_global[NUMERIC_COLS].apply(
        pd.to_numeric, errors="coerce").mean()
    COLS_TABLA = [c for c in NUMERIC_COLS if c in vals_pac]
    
    comparativa = pd.DataFrame({
        "Variable":     [TRADUCCION_VARS.get(c, c) for c in COLS_TABLA],
        "Paciente":     [vals_pac[c] for c in COLS_TABLA],
        "Media global": medias_global[COLS_TABLA].values.round(1),
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
        x="Variable", y="Valor", color="Grupo", barmode="group",
        color_discrete_map={"Paciente": "#e74c3c", "Media global": "#3498db"},
        title="Perfil clínico del paciente vs. media global",
        labels={"Valor": "Valor clínico", "Variable": ""},
    )
    st.plotly_chart(fig_comp, width='stretch',
                    config={"locale": "es"})

    # Comparativa con grupo de edad
    st.divider()
    _, _, confirmado = mostrar_selector_rango_edad_ictus(df_global, age_res)

    if confirmado:
        mostrar_comparativa_paciente_ictus(
            df_global,
            edad=age_res,
            valores_paciente=vals_pac,
            delta_inf=st.session_state.delta_confirmado_inf_ictus,
            delta_sup=st.session_state.delta_confirmado_sup_ictus,
        )

    st.caption(
        "⚕️ **Aviso clínico**: Esta herramienta tiene fines académicos (TFG). "
        "No sustituye el diagnóstico ni el criterio de un profesional médico."
    )


# SECCIÓN 3: EXPLORACIÓN DEL DATASET

st.divider()
with st.expander("📊 Ver análisis exploratorio del dataset de ictus", expanded=False):
    st.write("En esta pestaña se puede analizar la base de datos utilizada en este sistema de predicción.")
    st.write("Como se indica más arriba, esta funcionalidad se encuentra en fase BETA y de desarrollo debido a que la base de datos no es tan amplia y se encuentra desbalanceada, por lo que la predicción puede no ser tan precisa.")
    st.write("Siempre consultar los resultados y cualquier decisión clínica con un profesional, esto sólo es una herramienta de apoyo diagnóstico.")
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Resumen", "Numéricas", "Categóricas", "Correlación"])
    with tab1:
        mostrar_resumen_ictus(df_global)
    with tab2:
        mostrar_distribucion_numerica_ictus(df_global)
    with tab3:
        mostrar_distribucion_categorica_ictus(df_global)
    with tab4:
        mostrar_correlacion_ictus(df_global)











with st.expander("📚 ¿Quieres saber más sobre cómo se producen los ictus o qué los causa? Pincha aquí"):

    st.markdown('<div class="rosa-box"><h2>🧠 Ictus: Definición y factores de riesgo </h2>', unsafe_allow_html=True)

    st.write("El ictus o accidente cerebrovascular (ACV) es la interrupción repentina del flujo sanguíneo al cerebro, causando la muerte de neuronas en minutos."
             "Existen dos tipos principales: isquémico (85%, obstrucción por coágulo) e hemorrágico (15%, rotura de vaso). Es la segunda causa de muerte mundial (7,25M muertes/año) y primera de discapacidad.")

    # Fila 1: Títulos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### **🔴 Factores de Riesgo**")
    with col2:
        st.markdown("### **🟢 Factores Protectores**")

    # Fila 2: No modificables vs Estilo de vida
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**No modificables:**")
        st.markdown("- Edad (>55 años)")
        st.markdown("- Sexo masculino")
        st.markdown("- Historia familiar")
        st.markdown("- ACV previo")
    with col2:
        st.markdown("**Estilo de vida:**")
        st.markdown("- Dieta mediterránea")
        st.markdown("- Ejercicio (150 min/sem)")
        st.markdown("- Control peso (IMC <25)")
        st.markdown("- No fumar")

    # Fila 3: Modificables vs Médicos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Modificables:**")
        st.markdown("- Hipertensión (50% casos)")
        st.markdown("- Fibrilación auricular")
        st.markdown("- Diabetes tipo 2")
        st.markdown("- Tabaquismo")
        st.markdown("- Obesidad")
        st.markdown("- Colesterol alto")
    with col2:
        st.markdown("**Médicos:**")
        st.markdown("- Tensión <130/80 mmHg")
        st.markdown("- Anticoagulantes")
        st.markdown("- Estatinas")
        st.markdown("- Antiagregantes")







left_spacer, center_col, right_spacer = st.columns([1, 0.3, 1])

with center_col:
    if st.button("Volver al inicio"): 
        st.switch_page("pages/inicio.py")


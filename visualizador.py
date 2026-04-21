# visualizador.py — Distribuciones de la BD original (NO resultados de modelos)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import NUMERIC_COLS, CATEGORICAL_COLS, TARGET_COL

# Añadir al inicio de visualizador.py, tras los imports
plotly_config = {"locale": "es"}

TRADUCCION_COLUMNAS = {
    "age":               "Edad (años)",
    "resting_bp":        "Tensión arterial (mmHg)",
    "cholesterol":       "Colesterol (mg/dL)",
    "maxhr":             "FC máxima (bpm)",
    "weight":            "Peso (kg)",
    "height":            "Altura (cm)",
    "glucose":           "Glucosa (mg/dL)",
}


def mostrar_resumen(df: pd.DataFrame):
    st.subheader("📋 Resumen del dataset")
    col1, col2, col3 = st.columns(3)
    col1.metric("Pacientes totales", f"{df.shape[0]:,}")
    col2.metric("Variables", df.shape[1])
    dist = df[TARGET_COL].value_counts(normalize=True)
    col3.metric("% Enfermedad CV", f"{dist.get(1, 0)*100:.1f}%")
    st.dataframe(df.describe().round(2), width='stretch')

def mostrar_distribucion_numerica(df: pd.DataFrame):
    st.subheader("📊 Distribución de variables numéricas")
    col_seleccionada = st.selectbox("Variable numérica:", NUMERIC_COLS)
    fig = px.histogram(df, x=col_seleccionada, color=TARGET_COL,
                       marginal="box", nbins=40,
                       labels={TARGET_COL: "Enfermedad CV"},
                       title=f"Distribución de {col_seleccionada}")
    st.plotly_chart(fig, width='stretch', config=plotly_config)

def mostrar_distribucion_categorica(df: pd.DataFrame):
    st.subheader("📊 Distribución de variables categóricas")
    col_seleccionada = st.selectbox("Variable categórica:", CATEGORICAL_COLS)
    fig = px.histogram(df, x=col_seleccionada, color=TARGET_COL,
                       barmode="group",
                       title=f"Distribución de {col_seleccionada}")
    st.plotly_chart(fig, width='stretch', config=plotly_config)

def mostrar_correlacion(df: pd.DataFrame):
    st.subheader("🔗 Mapa de correlación (variables numéricas)")
    corr = df[NUMERIC_COLS].corr()
    fig = px.imshow(corr, text_auto=".2f",
                    title="Correlación entre variables clínicas numéricas")
    st.plotly_chart(fig, width='stretch', config=plotly_config)

def mostrar_valores_nulos(df: pd.DataFrame):
    st.subheader("🕳️ Valores faltantes por columna")
    nulos = df.isnull().sum().reset_index()
    nulos.columns = ["Variable", "Valores nulos"]
    nulos = nulos[nulos["Valores nulos"] > 0].sort_values("Valores nulos", ascending=False)
    fig = px.bar(nulos, x="Variable", y="Valores nulos",
                 title="Missing values antes del preprocesado")
    st.plotly_chart(fig, width='stretch', config=plotly_config)
    
def get_pacientes_por_rango_edad(df: pd.DataFrame, edad: int,
                                  delta_inf: int = 1, delta_sup: int = 1) -> pd.DataFrame:
    """Devuelve todos los pacientes con edad en [edad-delta_inf, edad+delta_sup]."""
    df_rango = df[df["age"].between(edad - delta_inf, edad + delta_sup)].reset_index(drop=True)

    if df_rango.empty:
        raise ValueError(
            f"No hay pacientes en el rango de edad "
            f"[{edad - delta_inf}, {edad + delta_sup}] años. "
            f"Amplía el rango en el selector."
        )

    return df_rango


def mostrar_selector_rango_edad(df_global: pd.DataFrame, edad_paciente: int) -> tuple:
    if "delta_confirmado_inf" not in st.session_state:
        st.session_state.delta_confirmado_inf = None
    if "delta_confirmado_sup" not in st.session_state:
        st.session_state.delta_confirmado_sup = None

    st.subheader("📐 Selecciona el rango de edad para la comparativa")
    st.markdown(
        "Arrastra los extremos del slider para definir el rango de edades "
        "con el que quieres compararte."
    )

    edad_min_bd = int(df_global["age"].min())
    edad_max_bd = int(df_global["age"].max())

    #  Slider sobre edades absolutas
    rango = st.slider(
        "Rango de edad (años):",
        min_value=edad_min_bd,
        max_value=edad_max_bd,
        value=(max(edad_min_bd, edad_paciente - 1),
               min(edad_max_bd, edad_paciente + 1)),
        step=1,
        key="slider_rango_edad"
    )

    edad_min_sel = rango[0]
    edad_max_sel = rango[1]

    # Recalcular deltas desde la edad del paciente
    delta_inf = edad_paciente - edad_min_sel
    delta_sup = edad_max_sel - edad_paciente
    
    delta_inf = edad_paciente - edad_min_sel
    delta_sup = edad_max_sel - edad_paciente
    
    # Validación
    if delta_inf < 0 or delta_sup < 0:
        st.error("⚠️ El rango seleccionado debe incluir tu edad.")
        return delta_inf, delta_sup, False  # No confirmar rango inválido


    n_rango = int(df_global["age"].between(edad_min_sel, edad_max_sel).sum())

    # ── Gráfico de distribución con región seleccionada ──
    age_counts = df_global["age"].value_counts().sort_index()

    fig = go.Figure()
    fig.add_bar(
        x=age_counts.index,
        y=age_counts.values,
        marker_color="#3498db",
        opacity=0.35,
        name="Distribución BD"
    )
    fig.add_vrect(
        x0=edad_min_sel - 0.5, x1=edad_max_sel + 0.5,
        fillcolor="#f39c12", opacity=0.20,
        line_width=2, line_color="#e67e22",
        annotation_text=f" {edad_min_sel}–{edad_max_sel} años ({n_rango:,} pac.)",
        annotation_position="top left",
        annotation_font_size=12
    )
    fig.add_vline(
        x=edad_paciente,
        line_color="red", line_dash="dash", line_width=2,
        annotation_text=f"  Tu edad: {edad_paciente}",
        annotation_position="top right",
        annotation_font_color="red"
    )
    fig.update_layout(
        xaxis_title="Edad (años)",
        yaxis_title="Nº de pacientes",
        showlegend=False,
        height=280,
        margin=dict(t=40, b=20, l=40, r=20),
        plot_bgcolor="white"
    )
    st.plotly_chart(fig, width='stretch', config=plotly_config)

    c1, c2, c3 = st.columns(3)
    c1.metric("Edad mínima seleccionada", f"{edad_min_sel} años")
    c2.metric("Edad máxima seleccionada", f"{edad_max_sel} años")
    c3.metric("Pacientes en el rango", f"{n_rango:,}")

    if st.button("✅ Confirmar rango y generar comparativa",
                 width='stretch', key="btn_confirmar_rango"):
        st.session_state.delta_confirmado_inf = delta_inf
        st.session_state.delta_confirmado_sup = delta_sup

    confirmado = st.session_state.delta_confirmado_inf is not None
    return delta_inf, delta_sup, confirmado



def mostrar_comparativa_paciente(
    df_global: pd.DataFrame,
    edad: int,
    valores_paciente: dict,  
    maxhr_final: float,
    delta_inf: int = 1,
    delta_sup: int = 1
):
    """
    Muestra tabla + barras triple de comparativa del paciente vs grupo de edad vs global.
    Llamar desde riesgo_cv.py tras la predicción.
    valores_paciente: dict {nombre_columna: valor} para evitar errores posicionales.
    """
    try:
        df_cercanos = get_pacientes_por_rango_edad(df_global, edad, delta_inf, delta_sup)
    except ValueError as e:
        st.warning(f"⚠️ {e}")
        return

    n_real         = len(df_cercanos)
    edad_min_grupo = int(df_cercanos["age"].min())
    edad_max_grupo = int(df_cercanos["age"].max())

    st.subheader("📈 Comparativa del paciente")
    st.caption(
        f"👥 Grupo de referencia: **{n_real:,} pacientes** con edades "
        f"**{edad_min_grupo}–{edad_max_grupo} años** "
        f"(tu edad ±{delta_inf}/{delta_sup} años)."
    )

    # Excluir 'age' (el grupo ya está filtrado por edad)
    # Solo incluir columnas que existan en ambos DataFrames
    COLS_COMPARATIVA = [
        c for c in NUMERIC_COLS
        if c != "age"
        and c in df_global.columns
        and c in df_cercanos.columns
        and c in valores_paciente  
    ]

    valores_sin_edad = [valores_paciente[c] for c in COLS_COMPARATIVA]

    medias_global   = df_global[COLS_COMPARATIVA].apply(pd.to_numeric, errors="coerce").mean()
    medias_cercanos = df_cercanos[COLS_COMPARATIVA].mean()

    col_global = f"Media global (~{len(df_global):,} pac.)"
    col_grupo  = f"Media grupo edad ({edad_min_grupo}–{edad_max_grupo} años, n={n_real})"

    comparativa = pd.DataFrame({
        "Variable":  [TRADUCCION_COLUMNAS.get(c, c) for c in COLS_COMPARATIVA],  # columnas traducidas
        "Paciente":  valores_sin_edad,
        col_global:  medias_global.values.round(1),
        col_grupo:   medias_cercanos.values.round(1),
    })
    comparativa["Dif. vs global (%)"]    = ((comparativa["Paciente"] - comparativa[col_global])  / comparativa[col_global]  * 100).round(1)
    comparativa["Dif. vs grupo edad (%)"] = ((comparativa["Paciente"] - comparativa[col_grupo]) / comparativa[col_grupo] * 100).round(1)
    st.dataframe(comparativa.set_index("Variable"), width='stretch')
    
    df_plot = pd.DataFrame({
        "Variable": [TRADUCCION_COLUMNAS.get(c, c) for c in COLS_COMPARATIVA] * 3,  # columnas traducidas
        "Valor": (
            valores_sin_edad
            + medias_global.values.round(1).tolist()
            + medias_cercanos.values.round(1).tolist()
        ),
        "Grupo": (
            ["Paciente"] * len(COLS_COMPARATIVA)
            + [col_global] * len(COLS_COMPARATIVA)
            + [col_grupo] * len(COLS_COMPARATIVA)
        )
    })
    fig_comp = px.bar(
        df_plot, x="Variable", y="Valor", color="Grupo", barmode="group",
        color_discrete_map={"Paciente": "#e74c3c", col_global: "#3498db", col_grupo: "#2ecc71"},
        title=f"Paciente vs. media global vs. grupo edad ({edad_min_grupo}–{edad_max_grupo} años)",
        labels={"Variable": "", "Valor": "Valor clínico"}  # ejes en español
    )
    fig_comp.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_comp, width='stretch', config=plotly_config)

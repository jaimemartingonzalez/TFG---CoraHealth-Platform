import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from ictus_utils import NUMERIC_COLS, CATEGORICAL_COLS, TARGET_COL

plotly_config = {"locale": "es"}


def mostrar_resumen_ictus(df: pd.DataFrame):
    st.subheader("📋 Resumen del dataset de ictus")
    col1, col2, col3 = st.columns(3)
    col1.metric("Pacientes totales", f"{df.shape[0]:,}")
    col2.metric("Variables", df.shape[1])
    dist = df[TARGET_COL].value_counts(normalize=True)
    col3.metric("% Ictus positivo", f"{dist.get(1, 0) * 100:.1f}%")
    st.dataframe(df.describe().round(2), width='stretch')


def mostrar_distribucion_numerica_ictus(df: pd.DataFrame):
    st.subheader("📊 Distribución de variables numéricas")
    col_sel = st.selectbox("Variable numérica:", NUMERIC_COLS, key="num_ictus")
    fig = px.histogram(
        df, x=col_sel, color=TARGET_COL,
        marginal="box", nbins=40,
        labels={TARGET_COL: "Ictus"},
        title=f"Distribución de {col_sel}",
    )
    st.plotly_chart(fig, width='stretch', config=plotly_config)


def mostrar_distribucion_categorica_ictus(df: pd.DataFrame):
    st.subheader("📊 Distribución de variables categóricas")
    col_sel = st.selectbox("Variable categórica:", CATEGORICAL_COLS, key="cat_ictus")
    fig = px.histogram(
        df, x=col_sel, color=TARGET_COL,
        barmode="group",
        title=f"Distribución de {col_sel}",
    )
    st.plotly_chart(fig, width='stretch', config=plotly_config)


def mostrar_correlacion_ictus(df: pd.DataFrame):
    st.subheader("🔗 Mapa de correlación (variables numéricas)")
    cols_num = [c for c in NUMERIC_COLS if c in df.columns]
    corr = df[cols_num].corr()
    fig = px.imshow(corr, text_auto=".2f",
                    title="Correlación entre variables clínicas numéricas")
    st.plotly_chart(fig, width='stretch', config=plotly_config)


def mostrar_valores_nulos_ictus(df: pd.DataFrame):
    st.subheader("🕳️ Valores faltantes por columna")
    nulos = df.isnull().sum().reset_index()
    nulos.columns = ["Variable", "Valores nulos"]
    nulos = nulos[nulos["Valores nulos"] > 0].sort_values("Valores nulos", ascending=False)
    if nulos.empty:
        st.success("✅ No hay valores nulos en el dataset.")
        return
    fig = px.bar(nulos, x="Variable", y="Valores nulos",
                 title="Missing values antes del preprocesado")
    st.plotly_chart(fig, width='stretch', config=plotly_config)


def get_pacientes_por_rango_edad_ictus(df: pd.DataFrame, edad: int,
                                        delta_inf: int = 1,
                                        delta_sup: int = 1) -> pd.DataFrame:
    """Devuelve pacientes con edad en [edad - delta_inf, edad + delta_sup]."""
    df_rango = df[df["age"].between(edad - delta_inf, edad + delta_sup)].reset_index(drop=True)
    if df_rango.empty:
        raise ValueError(
            f"No hay pacientes en el rango de edad "
            f"[{edad - delta_inf}, {edad + delta_sup}] años. "
            f"Amplía el rango en el selector."
        )
    return df_rango


def mostrar_selector_rango_edad_ictus(df_global: pd.DataFrame,
                                       edad_paciente: int) -> tuple:
    if "delta_confirmado_inf_ictus" not in st.session_state:
        st.session_state.delta_confirmado_inf_ictus = None
    if "delta_confirmado_sup_ictus" not in st.session_state:
        st.session_state.delta_confirmado_sup_ictus = None

    st.subheader("📐 Selecciona el rango de edad para la comparativa")
    st.markdown("Arrastra los extremos del slider para definir el rango de edades "
                "con el que quieres compararte.")

    edad_min_bd = int(df_global["age"].min())
    edad_max_bd = int(df_global["age"].max())

    rango = st.slider(
        "Rango de edad (años):",
        min_value=edad_min_bd, max_value=edad_max_bd,
        value=(max(edad_min_bd, edad_paciente - 2),
               min(edad_max_bd, edad_paciente + 2)),
        step=1, key="slider_rango_edad_ictus",
    )

    edad_min_sel, edad_max_sel = rango
    delta_inf = edad_paciente - edad_min_sel
    delta_sup = edad_max_sel - edad_paciente

    if delta_inf < 0 or delta_sup < 0:
        st.error("⚠️ El rango seleccionado debe incluir tu edad.")
        return delta_inf, delta_sup, False

    n_rango = int(df_global["age"].between(edad_min_sel, edad_max_sel).sum())
    age_counts = df_global["age"].value_counts().sort_index()

    fig = go.Figure()
    fig.add_bar(x=age_counts.index, y=age_counts.values,
                marker_color="#3498db", opacity=0.35, name="Distribución BD")
    fig.add_vrect(
        x0=edad_min_sel - 0.5, x1=edad_max_sel + 0.5,
        fillcolor="#f39c12", opacity=0.20,
        line_width=2, line_color="#e67e22",
        annotation_text=f" {edad_min_sel}–{edad_max_sel} años ({n_rango:,} pac.)",
        annotation_position="top left", annotation_font_size=12,
    )
    fig.add_vline(
        x=edad_paciente, line_color="red", line_dash="dash", line_width=2,
        annotation_text=f" Tu edad: {edad_paciente}",
        annotation_position="top right", annotation_font_color="red",
    )
    fig.update_layout(xaxis_title="Edad (años)", yaxis_title="Nº de pacientes",
                      showlegend=False, height=280,
                      margin=dict(t=40, b=20, l=40, r=20), plot_bgcolor="white")
    st.plotly_chart(fig, width='stretch', config=plotly_config)

    c1, c2, c3 = st.columns(3)
    c1.metric("Edad mínima seleccionada", f"{edad_min_sel} años")
    c2.metric("Edad máxima seleccionada", f"{edad_max_sel} años")
    c3.metric("Pacientes en el rango", f"{n_rango:,}")

    if st.button("✅ Confirmar rango y generar comparativa",
                 width='stretch', key="btn_confirmar_rango_ictus"):
        st.session_state.delta_confirmado_inf_ictus = delta_inf
        st.session_state.delta_confirmado_sup_ictus = delta_sup

    confirmado = st.session_state.delta_confirmado_inf_ictus is not None
    return delta_inf, delta_sup, confirmado


# Diccionarios para mostrar etiquetas en español en los gráficos
_LABEL_BIN = {
    "hypertension":  "Hipertensión",
    "heart_disease": "Enf. cardíaca",
    "ever_married":  "Casado/a",
}
_LABEL_CAT = {
    "gender":         "Sexo",
    "work_type":      "Tipo de trabajo",
    "Residence_type": "Residencia",
}
_LABEL_NUM = {
    "avg_glucose_level": "Glucosa media (mg/dL)",
    "bmi":               "IMC (kg/m²)",
}


def mostrar_comparativa_paciente_ictus(df_global: pd.DataFrame, edad: int,
                                        valores_paciente: dict,
                                        delta_inf: int = 2,
                                        delta_sup: int = 2):
    try:
        df_cercanos = get_pacientes_por_rango_edad_ictus(
            df_global, edad, delta_inf, delta_sup)
    except ValueError as e:
        st.warning(f"⚠️ {e}")
        return

    n_real     = len(df_cercanos)
    edad_min_g = int(df_cercanos["age"].min())
    edad_max_g = int(df_cercanos["age"].max())
    label_grupo = f"Grupo edad {edad_min_g}–{edad_max_g} a. (n={n_real})"
    label_global = f"Media global (~{len(df_global):,} pac.)"

    st.subheader("📈 Comparativa del paciente")
    st.caption(
        f"👥 Grupo de referencia: **{n_real:,} pacientes** con edades "
        f"**{edad_min_g}–{edad_max_g} años** (tu edad ±{delta_inf}/{delta_sup} años)."
    )

    COLS_NUM = [c for c in NUMERIC_COLS
                if c != "age"
                and c in df_global.columns
                and c in df_cercanos.columns
                and c in valores_paciente]

    if COLS_NUM:
        st.markdown("#### 🔢 Variables numéricas")
        medias_global   = df_global[COLS_NUM].apply(
            pd.to_numeric, errors="coerce").mean()
        medias_cercanos = df_cercanos[COLS_NUM].mean()

        comp_num = pd.DataFrame({
            "Variable":    [_LABEL_NUM.get(c, c) for c in COLS_NUM],
            "Paciente":    [valores_paciente[c] for c in COLS_NUM],
            label_global:  medias_global.values.round(1),
            label_grupo:   medias_cercanos.values.round(1),
        })
        comp_num["Dif. vs global (%)"] = (
            (comp_num["Paciente"] - comp_num[label_global])
            / comp_num[label_global] * 100
        ).round(1)
        comp_num["Dif. vs grupo edad (%)"] = (
            (comp_num["Paciente"] - comp_num[label_grupo])
            / comp_num[label_grupo] * 100
        ).round(1)
        st.dataframe(comp_num.set_index("Variable"), width='stretch')

        df_plot_num = pd.DataFrame({
            "Variable": [_LABEL_NUM.get(c, c) for c in COLS_NUM] * 3,
            "Valor": (
                [valores_paciente[c] for c in COLS_NUM]
                + medias_global.values.round(1).tolist()
                + medias_cercanos.values.round(1).tolist()
            ),
            "Grupo": (
                ["Paciente"]    * len(COLS_NUM)
                + [label_global] * len(COLS_NUM)
                + [label_grupo]  * len(COLS_NUM)
            ),
        })
        fig_num = px.bar(
            df_plot_num, x="Variable", y="Valor",
            color="Grupo", barmode="group",
            color_discrete_map={
                "Paciente":   "#e74c3c",
                label_global: "#3498db",
                label_grupo:  "#2ecc71",
            },
            title="Variables numéricas: paciente vs. medias poblacionales",
        )
        fig_num.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_num, width='stretch',
                        config=plotly_config)


    # 2. VARIABLES BINARIAS (hypertension, heart_disease, ever_married)
    
    COLS_BIN = [c for c in ["hypertension", "heart_disease", "ever_married"]
                if c in df_global.columns
                and c in df_cercanos.columns
                and c in valores_paciente]

    if COLS_BIN:
        st.markdown("#### ✅ Variables binarias (% de casos positivos en la población)")
        rows_bin = []
        for col in COLS_BIN:
            val_pac   = int(valores_paciente[col])
            pct_glob  = df_global[col].apply(
                pd.to_numeric, errors="coerce").mean() * 100
            pct_grupo = df_cercanos[col].apply(
                pd.to_numeric, errors="coerce").mean() * 100
            rows_bin.append({
                "Variable":           _LABEL_BIN.get(col, col),
                "Paciente":           "Sí" if val_pac == 1 else "No",
                "% global con Sí":    round(pct_glob, 1),
                "% grupo edad con Sí":round(pct_grupo, 1),
            })
        df_bin = pd.DataFrame(rows_bin).set_index("Variable")
        st.dataframe(df_bin, width='stretch')

        # Gráfico: % Sí del paciente (0 o 100) vs medias
        df_plot_bin = pd.DataFrame({
            "Variable": [_LABEL_BIN.get(c, c) for c in COLS_BIN] * 3,
            "% con Sí": (
                [int(valores_paciente[c]) * 100 for c in COLS_BIN]
                + [round(df_global[c].apply(pd.to_numeric,
                   errors="coerce").mean() * 100, 1) for c in COLS_BIN]
                + [round(df_cercanos[c].apply(pd.to_numeric,
                   errors="coerce").mean() * 100, 1) for c in COLS_BIN]
            ),
            "Grupo": (
                ["Paciente (Sí=100 / No=0)"] * len(COLS_BIN)
                + [label_global]              * len(COLS_BIN)
                + [label_grupo]               * len(COLS_BIN)
            ),
        })
        fig_bin = px.bar(
            df_plot_bin, x="Variable", y="% con Sí",
            color="Grupo", barmode="group",
            color_discrete_map={
                "Paciente (Sí=100 / No=0)": "#e74c3c",
                label_global:               "#3498db",
                label_grupo:                "#2ecc71",
            },
            title="Variables binarias: paciente vs. % positivos en población",
            labels={"% con Sí": "% casos positivos"},
        )
        fig_bin.update_layout(
            yaxis_range=[0, 100],
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_bin, width='stretch',
                        config=plotly_config)


    # 3. VARIABLES CATEGÓRICAS (gender, work_type, Residence_type)
    
    COLS_CAT_VIS = [c for c in ["gender", "work_type", "Residence_type"]
                    if c in df_global.columns
                    and c in df_cercanos.columns
                    and c in valores_paciente]

    if COLS_CAT_VIS:
        st.markdown("#### 🏷️ Variables categóricas")
        st.caption(
            "Se muestra la distribución completa de cada variable en la "
            "población. La barra del paciente (roja) indica su categoría."
        )
        for col in COLS_CAT_VIS:
            val_pac = valores_paciente[col]
            label_col = _LABEL_CAT.get(col, col)

            # Distribuciones globales y del grupo (%)
            dist_global = (df_global[col].value_counts(normalize=True) * 100).round(1)
            dist_grupo  = (df_cercanos[col].value_counts(normalize=True) * 100).round(1)

            categorias = sorted(
                set(dist_global.index.tolist() + dist_grupo.index.tolist()))

            df_cat_plot = pd.DataFrame({
                "Categoría": categorias * 2,
                "Porcentaje": (
                    [dist_global.get(cat, 0.0) for cat in categorias]
                    + [dist_grupo.get(cat, 0.0)  for cat in categorias]
                ),
                "Grupo": (
                    [label_global] * len(categorias)
                    + [label_grupo]  * len(categorias)
                ),
            })

            fig_cat = px.bar(
                df_cat_plot, x="Categoría", y="Porcentaje",
                color="Grupo", barmode="group",
                color_discrete_map={
                    label_global: "#3498db",
                    label_grupo:  "#2ecc71",
                },
                title=f"{label_col}: distribución en la población",
                labels={"Porcentaje": "% pacientes"},
            )
            # Resaltar la categoría del paciente con una línea vertical
            if val_pac in categorias:
                max_y = max(
        dist_global.get(val_pac, 0.0),
        dist_grupo.get(val_pac, 0.0),
    )
        
        fig_cat.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_cat, width='stretch',
                            config=plotly_config)

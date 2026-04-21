from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent
IMAGES_DIR  = BASE_DIR / "images"
MODELS_DIR  = BASE_DIR / "models"
DATA_PATH   = BASE_DIR / "data" / "stroke_data.csv"

APP_TITLE = "Riesgo de Ictus - TFG"
APP_ICON  = "🧠"

# Columnas numéricas continuas del dataset
NUMERIC_COLS = ["age", "avg_glucose_level", "bmi"]

# Columnas categóricas que recibirán One-Hot Encoding
CATEGORICAL_COLS = ["gender", "work_type", "Residence_type"]

# Columnas binarias (ya 0/1 tras la carga)
BINARY_COLS = ["hypertension", "heart_disease", "ever_married", "smoker"]

TARGET_COL = "stroke"

# Preprocesado
RANDOM_STATE      = 42
TEST_SIZE         = 0.2
KNN_NEIGHBORS     = 5
SMOTE_K_NEIGHBORS = 5
CAT_IMPUTER_FILL  = "Unknown"

# Pesos óptimos 
BEST_WEIGHT_RF     = {0: 1, 1: 10}
BEST_SCALE_POS_XGB = 10

# Modelos disponibles en la app
MODELOS_DISPONIBLES_ICTUS = {
    "Random Forest: Equilibrado (detecta bien tanto enfermos como sanos)":
        "models.ictus_modelo_rf",
    "XGBoost: Conservador (solo alerta cuando está muy seguro)":
        "models.ictus_modelo_xgb",
    "Regresión Logística: Preventivo (prefiere avisarte antes que perderse un caso)":
        "models.ictus_modelo_lr",
    "SVM: Versátil (aprende patrones complejos entre variables)":
        "models.ictus_modelo_svm",
}


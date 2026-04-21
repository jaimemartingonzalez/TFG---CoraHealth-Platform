#  Constantes globales del módulo cardiovascular

from pathlib import Path

# Raíz del proyecto (donde está utils.py, siempre en la raíz)
BASE_DIR   = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"
MODELS_DIR  = BASE_DIR / "models" 
DATA_PATH  = BASE_DIR / "data" / "heart_all_merged_final_v2.csv"


APP_TITLE = "Riesgo Cardiovascular - TFG"
APP_ICON = "❤️"

# Columnas del dataset real
NUMERIC_COLS = ["age", "resting_bp", "cholesterol", "maxhr", "weight", "height", "glucose", "smoking", "alcohol_use", "physical_activity"]
CATEGORICAL_COLS = ["RestingECG", "ST_Slope", "sex"]
TARGET_COL = "heart_disease"

# Preprocesado
RANDOM_STATE = 42
TEST_SIZE = 0.2
KNN_NEIGHBORS = 5
SMOTE_K_NEIGHBORS = 5
CAT_IMPUTER_FILL = "Unknown"

# Pesos óptimos por modelo (hallados en los notebooks de optimización)
BEST_WEIGHT_RF = {0: 1, 1: 3}      
BEST_SCALE_POS_XGB = 2             

# Modelos disponibles para el usuario
MODELOS_DISPONIBLES = {
    "Random Forest: Equilibrado (detecta bien tanto enfermos como sanos)": "models.modelo_rf",
    "XGBoost: Conservador (solo alerta cuando está muy seguro)": "models.modelo_xgb",
    "Regresión Logística: Preventivo (prefiere avisarte antes que perderse un caso)": "models.modelo_lr",
    "MLP (Red Neuronal): Versátil (aprende patrones complejos entre variables)": "models.modelo_mlp",
}



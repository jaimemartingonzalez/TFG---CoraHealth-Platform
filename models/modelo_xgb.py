import streamlit as st
import xgboost as xgb
from utils import RANDOM_STATE, BEST_SCALE_POS_XGB

@st.cache_resource(show_spinner="⚡ Entrenando XGBoost...")
def entrenar(_X_train, _y_train):
    modelo = xgb.XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        scale_pos_weight=BEST_SCALE_POS_XGB,  
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        use_label_encoder=False
    )
    modelo.fit(_X_train, _y_train, verbose=False)
    return {                                      
        "modelo":   modelo,
        "scaler":   None,                         
        "features": list(_X_train.columns)
    }

def predecir(resultado: dict, X):                 
    return (
        resultado["modelo"].predict(X),
        resultado["modelo"].predict_proba(X)[:, 1]
    )
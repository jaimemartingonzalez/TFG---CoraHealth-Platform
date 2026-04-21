from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from ictus_utils import RANDOM_STATE, BEST_SCALE_POS_XGB


def entrenar(X_train, y_train) -> dict:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    modelo = XGBClassifier(
        n_estimators=300,
        scale_pos_weight=BEST_SCALE_POS_XGB,
        learning_rate=0.05,
        max_depth=6,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    modelo.fit(X_scaled, y_train)
    return {"modelo": modelo, "scaler": scaler, "features": list(X_train.columns)}


def predecir(resultado: dict, X_test) -> tuple:
    X_scaled = resultado["scaler"].transform(X_test)
    preds  = resultado["modelo"].predict(X_scaled)
    probas = resultado["modelo"].predict_proba(X_scaled)[:, 1]
    return preds, probas

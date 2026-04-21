from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from ictus_utils import RANDOM_STATE, BEST_WEIGHT_RF


def entrenar(X_train, y_train) -> dict:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    modelo = RandomForestClassifier(
        n_estimators=200,
        class_weight=BEST_WEIGHT_RF,
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

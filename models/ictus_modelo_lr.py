from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from ictus_utils import RANDOM_STATE


def entrenar(X_train, y_train) -> dict:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    modelo = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=RANDOM_STATE,
        solver="lbfgs",
    )
    modelo.fit(X_scaled, y_train)
    return {"modelo": modelo, "scaler": scaler, "features": list(X_train.columns)}


def predecir(resultado: dict, X_test) -> tuple:
    X_scaled = resultado["scaler"].transform(X_test)
    preds  = resultado["modelo"].predict(X_scaled)
    probas = resultado["modelo"].predict_proba(X_scaled)[:, 1]
    return preds, probas

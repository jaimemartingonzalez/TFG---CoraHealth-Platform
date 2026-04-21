from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from ictus_utils import RANDOM_STATE


def entrenar(X_train, y_train) -> dict:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    modelo = SVC(
        kernel="rbf",
        C=1.0,
        gamma="scale",
        class_weight="balanced",   # compensa el desbalanceo ~95/5
        probability=True,          # necesario para predict_proba
        random_state=RANDOM_STATE,
    )
    modelo.fit(X_scaled, y_train)
    return {"modelo": modelo, "scaler": scaler, "features": list(X_train.columns)}


def predecir(resultado: dict, X_test) -> tuple:
    X_scaled = resultado["scaler"].transform(X_test)
    preds  = resultado["modelo"].predict(X_scaled)
    probas = resultado["modelo"].predict_proba(X_scaled)[:, 1]
    return preds, probas
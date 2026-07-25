import os
import joblib
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/features.csv")

##. Select Features
FEATURES = [

    "hour_of_day",

    "day_of_week",

    "is_weekend",

    "session_duration",

    "time_since_last_login",

    "login_frequency",

    "avg_session_duration",

    "session_ratio",

    "new_device",

    "new_location",

    "failed_login",

    "failed_login_ratio",

    "auth_changed",

    "new_resource",

    "resource_count",

    "command_length"

]

X = df[FEATURES]
X = X.fillna(0)
scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

## Train Isolation Forest
model = IsolationForest(

    n_estimators=200,

    contamination=0.03,

    random_state=42

)

model.fit(X_scaled)

pred = model.predict(X_scaled)
df["prediction"] = pred

df["prediction"] = df["prediction"].map({

    1: "normal",

    -1: "anomaly"

})

df["anomaly_score"] = -model.decision_function(X_scaled)

score = df["anomaly_score"]

df["risk_score"] = (

    (score - score.min()) /

    (score.max() - score.min())

) * 100

# ----------------------------------------
# Analyst Alert Budget Evaluation
# ----------------------------------------

df_sorted = df.sort_values(
    "risk_score",
    ascending=False
)

top_k = max(1, int(len(df_sorted) * 0.01))

top_alerts = df_sorted.head(top_k)

precision_top1 = (
    top_alerts["label"] == "anomaly"
).mean()

print(f"\nTop 1% Alert Budget")
print(f"Alerts Reviewed : {top_k}")
print(f"True Anomalies  : {(top_alerts['label']=='anomaly').sum()}")
print(f"Precision       : {precision_top1:.4f}")

top_alerts.to_csv(
    "data/models/top_1_percent_alerts.csv",
    index=False
)

## Evaluate
print(

classification_report(

    df["label"],

    df["prediction"]

))

cm = confusion_matrix(
    df["label"],
    df["prediction"],
    labels=["normal", "anomaly"]
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["normal", "anomaly"]
)

disp.plot(cmap="Blues")

plt.tight_layout()

plt.savefig("data/models/detection_confusion_matrix.png")

plt.close()

os.makedirs("data/models", exist_ok=True)

joblib.dump(

    model,

    "data/models/detector.pkl"

)

joblib.dump(

    scaler,

    "data/models/scaler.pkl"

)

df.to_csv(

    "data/models/detector_results.csv",

    index=False

)

print("Detector trained successfully.")
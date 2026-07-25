import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt

df = pd.read_csv("data/models/detector_results.csv")

df = df[df["label"] == "anomaly"].copy()

df = df[df["attack_type"] != "None"]
df = df.dropna(subset=["attack_type"])

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
    "command_length",
]

X = df[FEATURES].fillna(0)

y = df["attack_type"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

clf = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced"
)

clf.fit(X_train, y_train)

pred = clf.predict(X_test)

results = X_test.copy()

results["Actual"] = y_test.values

results["Predicted"] = pred

results.to_csv(
    "data/models/classifier_predictions.csv",
    index=False
)

print(classification_report(y_test, pred))

print(confusion_matrix(y_test, pred))

cm = confusion_matrix(y_test, pred)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=clf.classes_
)

disp.plot(
    cmap="Blues",
    xticks_rotation=45
)

plt.tight_layout()

plt.savefig(
    "data/models/classification_confusion_matrix.png"
)

importance = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": clf.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print(importance)

importance.to_csv(
    "data/models/feature_importance.csv",
    index=False
)

os.makedirs("data/models", exist_ok=True)

joblib.dump(
    clf,
    "data/models/classifier.pkl"
)

print("Classifier saved.")
# models/risk_score.py

def calculate_risk_score(anomaly_score, class_probability):

    anomaly_score = abs(anomaly_score)

    risk = anomaly_score * 40 + class_probability * 60

    return min(round(risk), 100)


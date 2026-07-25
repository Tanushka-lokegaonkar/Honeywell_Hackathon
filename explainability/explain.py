import pandas as pd

def explain_event(row):
    reasons = []

    # Feature-based reasons
    if row["new_device"] == 1:
        reasons.append("New Device Detected")

    if row["new_location"] == 1:
        reasons.append("Login From New Location")

    if row["failed_login_ratio"] > 0.5:
        reasons.append("High Failed Login Ratio")

    if row["session_ratio"] > 2:
        reasons.append("Abnormally Long Session")

    if row["new_resource"] == 1:
        reasons.append("Previously Unseen Resource")

    if row["auth_changed"] == 1:
        reasons.append("Authentication Method Changed")

    if row["hour_of_day"] < 6 or row["hour_of_day"] > 22:
        reasons.append("Login Outside Normal Working Hours")

    # Attack-specific reasons
    attack = row["attack_type"]

    if attack == "Brute Force":
        reasons.append("Rapid Consecutive Login Attempts")

    elif attack == "Impossible Travel":
        reasons.append("Impossible Geo-Location Change")

    elif attack == "Credential Stuffing":
        reasons.append("Repeated Login Attempts Using Stolen Credentials")

    elif attack == "Device Spoofing":
        reasons.append("Device Fingerprint Mismatch")

    elif attack == "Lateral Movement":
        reasons.append("Unusual Internal Resource Access")

    elif attack == "Low and Slow":
        reasons.append("Gradual Suspicious Behaviour")

    # Remove duplicates
    reasons = list(dict.fromkeys(reasons))

    return ", ".join(reasons)

df = pd.read_csv(
    "data/models/detector_results.csv"
)

df["reasons"] = df.apply(
    explain_event,
    axis=1
)

df.to_csv(
    "data/models/explained_results.csv",
    index=False
)
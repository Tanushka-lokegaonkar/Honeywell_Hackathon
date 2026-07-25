def explain_event(event, profile):

    reasons = []

    if event["login_hour"] < profile["login_start"] or \
       event["login_hour"] > profile["login_end"]:
        reasons.append("Outside normal working hours")

    if event["resource"] not in profile["resources"]:
        reasons.append("New resource accessed")

    if event["device_fingerprint"] != profile["device_fingerprint"]:
        reasons.append("Unknown device")

    return reasons
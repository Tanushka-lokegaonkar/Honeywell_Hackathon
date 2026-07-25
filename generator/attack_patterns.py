import random
from copy import deepcopy
from datetime import timedelta

# ---------------------------------------
# Helper Data
# ---------------------------------------

LOCATIONS = [
    ("London", "212.58.244.1"),
    ("New York", "104.18.1.1"),
    ("Tokyo", "103.5.140.1"),
    ("Sydney", "1.120.0.1"),
    ("Dubai", "5.32.0.1")
]

RESOURCES = [
    "Firewall",
    "Router",
    "VPN",
    "Database",
    "SCADA",
    "PLC",
    "Admin Panel"
]

COMMANDS = [
    "login>database>logout",
    "login>firewall>router>logout",
    "login>vpn>database>logout",
    "login>scada>plc>router>logout",
    "login>admin>database>router>logout"
]

OS_LIST = [
    "Windows",
    "Linux",
    "Ubuntu",
    "Android",
    "macOS"
]


def random_fingerprint():
    return f"{random.choice(OS_LIST)}-{random.randint(1000,9999)}"


# ======================================================
# 1 Brute Force
# ======================================================

def inject_brute_force(events, num_attacks=100):

    attacks = []

    victims = random.sample(events, num_attacks)

    for event in victims:

        base = deepcopy(event)

        # 5 failed logins
        for i in range(5):

            failed = deepcopy(base)

            failed["timestamp"] += timedelta(seconds=i * 20)

            failed["login_status"] = "Failed"

            failed["label"] = "anomaly"

            failed["attack_type"] = "Brute Force"

            attacks.append(failed)

        # Successful login

        success = deepcopy(base)

        success["timestamp"] += timedelta(minutes=2)

        success["login_status"] = "Success"

        success["label"] = "anomaly"

        success["attack_type"] = "Brute Force"

        attacks.append(success)

    return attacks


# ======================================================
# 2 Impossible Travel
# ======================================================

def inject_impossible_travel(events, num_attacks=100):

    attacks = []

    victims = random.sample(events, num_attacks)

    for event in victims:

        new = deepcopy(event)

        city, ip = random.choice(LOCATIONS)

        new["geo_location"] = city

        new["source_ip"] = ip

        new["timestamp"] += timedelta(minutes=random.randint(15,45))

        new["label"] = "anomaly"

        new["attack_type"] = "Impossible Travel"

        attacks.append(new)

    return attacks


# ======================================================
# 3 Credential Stuffing
# ======================================================

def inject_credential_stuffing(events, groups=20):

    attacks = []

    attacker_ip = "185.220.101.10"

    for _ in range(groups):

        victims = random.sample(events,5)

        for i,event in enumerate(victims):

            new = deepcopy(event)

            new["source_ip"] = attacker_ip

            if i == 4:
                new["login_status"]="Success"
            else:
                new["login_status"]="Failed"

            new["label"]="anomaly"

            new["attack_type"]="Credential Stuffing"

            attacks.append(new)

    return attacks


# ======================================================
# 4 Lateral Movement
# ======================================================

def inject_lateral_movement(events,num_attacks=100):

    attacks=[]

    victims=random.sample(events,num_attacks)

    for event in victims:

        new=deepcopy(event)

        new["resource"]=random.choice(["Database","SCADA","PLC","Admin Panel"])

        new["command_sequence"]=random.choice(COMMANDS)

        new["session_duration"]*=random.randint(2,5)

        new["label"]="anomaly"

        new["attack_type"]="Lateral Movement"

        attacks.append(new)

    return attacks


# ======================================================
# 5 Device Spoofing
# ======================================================

def inject_device_spoofing(events,num_attacks=100):

    attacks=[]

    victims=random.sample(events,num_attacks)

    for event in victims:

        new=deepcopy(event)

        new["device_fingerprint"]=random_fingerprint()

        new["auth_method"]="Password"

        new["label"]="anomaly"

        new["attack_type"]="Device Spoofing"

        attacks.append(new)

    return attacks


# ======================================================
# 6 Low And Slow
# ======================================================

def inject_low_and_slow(events,num_attacks=50):

    attacks=[]

    victims=random.sample(events,num_attacks)

    for event in victims:

        base=deepcopy(event)

        duration=base["session_duration"]

        for day in range(5):

            new=deepcopy(base)

            new["timestamp"]+=timedelta(days=day)

            new["session_duration"]=duration+(day+1)*300

            new["resource"]=RESOURCES[min(day,len(RESOURCES)-1)]

            new["command_sequence"]=COMMANDS[min(day,len(COMMANDS)-1)]

            new["label"]="anomaly"

            new["attack_type"]="Low and Slow"

            attacks.append(new)

    return attacks


# ======================================================
# MASTER FUNCTION
# ======================================================

def inject_all_attacks(events):

    attack_events=[]

    attack_events.extend(inject_brute_force(events,100))

    attack_events.extend(inject_impossible_travel(events,100))

    attack_events.extend(inject_credential_stuffing(events,20))

    attack_events.extend(inject_lateral_movement(events,100))

    attack_events.extend(inject_device_spoofing(events,100))

    attack_events.extend(inject_low_and_slow(events,50))

    random.shuffle(attack_events)

    return attack_events



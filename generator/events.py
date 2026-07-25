import random
from datetime import datetime, timedelta
import pandas as pd
import os

from generator.profiles import UserProfile, DeviceProfile

CITY_SUBNET = {
    "Bangalore": "10.10",
    "Mumbai": "10.20",
    "Hyderabad": "10.30",
    "Chennai": "10.40",
    "Pune": "10.50"
}

def generate_ip(city):

    subnet = CITY_SUBNET[city]

    return f"{subnet}.{random.randint(0,255)}.{random.randint(1,254)}"

def generate_timestamp(user, current_date):

    hour = random.randint(
        user.login_start,
        user.login_end
    )

    minute = random.randint(0,59)

    second = random.randint(0,59)

    return current_date.replace(
        hour=hour,
        minute=minute,
        second=second
    )

def choose_resource(user):

    weights = [70]

    while len(weights) < len(user.resources):
        weights.append(10)

    return random.choices(
        user.resources,
        weights=weights,
        k=1
    )[0]

def session_duration(user):

    duration = int(

        random.gauss(

            user.avg_session,

            120

        )

    )

    return max(duration,60)

COMMANDS = {

    "Finance":[
        ["login","open_payroll","read","logout"],
        ["login","finance_api","update","logout"]
    ],

    "HR":[
        ["login","attendance","read","logout"],
        ["login","employee_db","update","logout"]
    ],

    "IT":[
        ["login","vpn","server","logout"],
        ["login","firewall","router","logout"]
    ],

    "Operations":[
        ["login","plc","scada","logout"],
        ["login","sensor","read","logout"]
    ],

    "Sales":[
        ["login","crm","customer_db","logout"],
        ["login","reports","download","logout"]
    ]
}

def generate_commands(user):

    return ">".join(

        random.choice(

            COMMANDS[user.department]

        )

    )

def create_event(

    event_id,

    user,

    device,

    current_date

):
    event = {

        "event_id":event_id,

        "entity_id":user.user_id,

        "entity_type":"user",

        "timestamp":generate_timestamp(

        user,

        current_date

        ),

        "source_ip":generate_ip(

        user.city

        ),

        "geo_location":user.city,

        "resource":choose_resource(

        user

        ),

        "auth_method":user.auth_method,

        "session_duration":session_duration(

        user

        ),

        "command_sequence":generate_commands(

        user

        ),

        "device_fingerprint":

        f"{device.operating_system}-{device.mac_address}",

        "login_status":"Success",

        "label":"normal",

        "attack_type":"None"

    }

    return event

def generate_normal_events(users, devices, num_days=30):

    events = []

    start_date = datetime(2026, 7, 1)

    event_counter = 1

    for day in range(num_days):

        current_date = start_date + timedelta(days=day)

        for user in users.values():

            daily_sessions = random.randint(2, 5)

            for _ in range(daily_sessions):

                device = devices[user.device_id]

                event = create_event(
                    event_id=f"EVT{event_counter:06d}",
                    user=user,
                    device=device,
                    current_date=current_date
                )

                events.append(event)

                event_counter += 1

    return events

from generator.profiles import (
    create_device_profiles,
    create_user_profiles
)

import os

os.makedirs("data/raw", exist_ok=True)

devices = create_device_profiles()

users = create_user_profiles(devices=devices)

events = generate_normal_events(users, devices)

df = pd.DataFrame(events)

df.to_csv(
    "data/raw/access_logs.csv",
    index=False
)

print(f"Generated {len(events)} events.")
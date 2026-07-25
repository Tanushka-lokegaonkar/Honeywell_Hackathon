import os
import random
import pandas as pd

from generator.profiles import (
    create_device_profiles,
    create_user_profiles
)

from generator.events import generate_normal_events
from generator.attack_patterns import inject_all_attacks

# -------------------------------------------------
# Create folders
# -------------------------------------------------

os.makedirs("data/raw", exist_ok=True)

# -------------------------------------------------
# Generate normal data
# -------------------------------------------------

devices = create_device_profiles()

users = create_user_profiles(devices=devices)

events = generate_normal_events(users, devices)

print(f"Generated {len(events)} normal events.")

# -------------------------------------------------
# Inject attacks
# -------------------------------------------------

attack_events = inject_all_attacks(events)

print(f"Generated {len(attack_events)} attack events.")

# -------------------------------------------------
# Merge
# -------------------------------------------------

events.extend(attack_events)

# Shuffle so attacks are mixed with normal events
random.shuffle(events)

# -------------------------------------------------
# Save
# -------------------------------------------------

df = pd.DataFrame(events)

df.to_csv(
    "data/raw/access_logs.csv",
    index=False
)

print("\nDataset saved successfully.")
print(f"Total Events : {len(df)}")

print("\nAttack Distribution:")
print(df["attack_type"].value_counts(dropna=False))

print("\nLabel Distribution:")
print(df["label"].value_counts())
import pandas as pd

df = pd.read_csv("data/raw/access_logs.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values(["entity_id", "timestamp"])

## define features
df["hour_of_day"] = df["timestamp"].dt.hour

df["day_of_week"] = df["timestamp"].dt.dayofweek

df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)

df["login_date"] = df["timestamp"].dt.date

## Time Since Last Login
df["time_since_last_login"] = (
    df.groupby("entity_id")["timestamp"]
      .diff()
      .dt.total_seconds()
)

df["time_since_last_login"] = (
    df["time_since_last_login"]
      .fillna(0)
)

## Login Frequency
df["login_frequency"] = (
    df.groupby(
        ["entity_id", "login_date"]
    )["event_id"]
    .transform("count")
)

### Failed Login Count
df["failed_login"] = (
    df["login_status"] == "Failed"
).astype(int)

df["failed_login_ratio"] = (
    df.groupby("entity_id")["failed_login"]
      .transform(
          lambda x: x.rolling(
              10,
              min_periods=1
          ).mean()
      )
)


## Average Session
df["avg_session_duration"] = (
    df.groupby("entity_id")["session_duration"]
      .transform("mean")
)

df["session_ratio"] = (
    df["session_duration"] /
    df["avg_session_duration"]
)

### New Device
seen = {}

new_device = []

for _, row in df.iterrows():

    user = row["entity_id"]

    fp = row["device_fingerprint"]

    if user not in seen:
        seen[user] = set()

    if fp in seen[user]:
        new_device.append(0)
    else:
        new_device.append(1)
        seen[user].add(fp)

df["new_device"] = new_device


## New Location
seen = {}

flags = []

for _, row in df.iterrows():

    user = row["entity_id"]

    city = row["geo_location"]

    if user not in seen:
        seen[user] = set()

    if city in seen[user]:
        flags.append(0)
    else:
        flags.append(1)
        seen[user].add(city)

df["new_location"] = flags

### Authentication Changed
previous = (
    df.groupby("entity_id")["auth_method"]
      .shift()
)

df["auth_changed"] = (
    previous != df["auth_method"]
).fillna(False).astype(int)

### New Resource
seen = {}

flags = []

for _, row in df.iterrows():

    user = row["entity_id"]

    resource = row["resource"]

    if user not in seen:
        seen[user] = set()

    if resource in seen[user]:
        flags.append(0)
    else:
        flags.append(1)
        seen[user].add(resource)

df["new_resource"] = flags

### Resource Count
df["resource_count"] = (
    df.groupby("entity_id")["resource"]
      .transform("nunique")
)

### Command Length
df["command_length"] = (
    df["command_sequence"]
      .str.split(">")
      .str.len()
)


import os

os.makedirs("data/processed", exist_ok=True)

df.to_csv(
    "data/processed/features.csv",
    index=False
)

print("Features saved successfully!")
print(f"Dataset shape: {df.shape}")
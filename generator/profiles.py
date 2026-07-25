from dataclasses import dataclass
from faker import Faker
import random

from generator.constants import (
    DEPARTMENTS,
    CITIES,
    AUTH_METHODS,
    OPERATING_SYSTEMS,
    PROTOCOLS,
    RESOURCES
)

fake = Faker()


@dataclass
class UserProfile:
    user_id: str
    department: str
    city: str
    login_start: int
    login_end: int
    resources: list
    auth_method: str
    device_id: str
    avg_session: int

@dataclass
class DeviceProfile:
    device_id: str
    operating_system: str
    firmware: str
    mac_address: str
    protocol: str

def create_device_profiles(num_devices=200):
    devices = {}

    for i in range(1, num_devices + 1):

        device_id = f"DEVICE{i:03d}"

        devices[device_id] = DeviceProfile(
            device_id=device_id,
            operating_system=random.choice(OPERATING_SYSTEMS),
            firmware=f"v{random.randint(1,5)}.{random.randint(0,9)}",
            mac_address=fake.mac_address(),
            protocol=random.choice(PROTOCOLS)
        )

    return devices

def create_user_profiles(num_users=500, devices=None):

    users = {}

    device_ids = list(devices.keys())

    for i in range(1, num_users + 1):

        department = random.choices(
            DEPARTMENTS,
            weights=[25, 15, 30, 20, 10],
            k=1
        )[0]

        login_start = random.randint(7,10)

        login_end = login_start + random.randint(8,10)

        user_id = f"USER{i:03d}"

        users[user_id] = UserProfile(

            user_id=user_id,

            department=department,

            city=random.choice(CITIES),

            login_start=login_start,

            login_end=login_end,

            resources=RESOURCES[department],

            auth_method=random.choice(AUTH_METHODS),

            device_id=random.choice(device_ids),

            avg_session=random.randint(300,1200)

        )

    return users

if __name__ == "__main__":

    devices = create_device_profiles()

    users = create_user_profiles(devices=devices)

    print(users["USER001"])
    print(devices["DEVICE001"])
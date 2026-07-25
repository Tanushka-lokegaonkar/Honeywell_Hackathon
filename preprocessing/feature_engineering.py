import numpy as np
import pandas as pd

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates geodesic distance in kilometers between two points."""
    R = 6371.0  # Earth radius in km
    dlat, dlon = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineers spatial, temporal, and sequence-based features per entity."""
    df = df.sort_values(by=['entity_id', 'timestamp']).reset_index(drop=True)
    
    # Temporal Δt
    df['prev_time'] = df.groupby('entity_id')['timestamp'].shift(1)
    df['time_delta_sec'] = (df['timestamp'] - df['prev_time']).dt.total_seconds().fillna(3600)
    
    # Geodesic Distance & Velocity
    df['prev_lat'] = df.groupby('entity_id')['geo_lat'].shift(1).fillna(df['geo_lat'])
    df['prev_lon'] = df.groupby('entity_id')['geo_lon'].shift(1).fillna(df['geo_lon'])
    
    df['distance_km'] = calculate_haversine_distance(
        df['prev_lat'], df['prev_lon'], df['geo_lat'], df['geo_lon']
    )
    df['velocity_kmh'] = df['distance_km'] / (df['time_delta_sec'] / 3600.0 + 1e-5)
    
    # Cyclic Time Features
    df['hour_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.hour / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.hour / 24.0)
    
    return df
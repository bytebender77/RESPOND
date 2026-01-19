#!/usr/bin/env python3
"""
Real-time disaster simulation script for RESPOND.

Continuously generates and ingests simulated disaster incidents
through the API for testing and demonstration.

Usage:
    python scripts/simulate_disaster.py

Press CTRL+C to stop.
"""

import random
import time
from datetime import datetime

import requests

API_URL = "http://127.0.0.1:8000/ingest/incident"

# Incident types with realistic text templates
INCIDENT_TYPES = {
    "fire": [
        "Fire spotted near residential block, heavy smoke visible",
        "Major fire outbreak in commercial area, flames spreading",
        "Fire reported in warehouse district, smoke visible from distance",
        "Building fire in downtown area, evacuation underway",
        "Fire alarm triggered in apartment complex, smoke detected",
    ],
    "flood": [
        "Flash flood warning, water rising rapidly in metro area",
        "Flooding reported in low-lying areas, roads submerged",
        "River overflow causing flooding in residential zones",
        "Heavy rainfall causing urban flooding, drainage overwhelmed",
        "Emergency flood alert, water entering basement levels",
    ],
    "building_collapse": [
        "Building collapse near school, people trapped",
        "Partial building collapse in old town area, rescue needed",
        "Construction site collapse, workers trapped under debris",
        "Multi-story building collapse reported, emergency response needed",
        "Wall collapse in residential area, people feared trapped",
    ],
    "bridge_collapse": [
        "Bridge collapsed near hospital zone, vehicles stuck",
        "Pedestrian bridge collapse, multiple injuries reported",
        "Old bridge structure collapsed, traffic disrupted",
        "Bridge deck collapse near river crossing, rescue underway",
        "Railway bridge collapse reported, trains halted",
    ],
    "earthquake_aftershock": [
        "Aftershock felt in downtown area, buildings shaking",
        "Earthquake aftershock reported, minor damage to structures",
        "Tremors felt across multiple zones, panic among residents",
        "Seismic activity detected, aftershock warning issued",
        "Ground shaking reported, possible aftershock event",
    ],
}

# Source types
SOURCE_TYPES = ["social", "sensor", "call", "report"]

# Urgency with weights
URGENCY_OPTIONS = [
    ("critical", 0.40),
    ("high", 0.30),
    ("medium", 0.20),
    ("low", 0.10),
]

# Zone IDs
ZONES = ["zone-1", "zone-2", "zone-3", "zone-4"]


def weighted_choice(options: list[tuple[str, float]]) -> str:
    """Select option based on weights."""
    choices, weights = zip(*options)
    return random.choices(choices, weights=weights, k=1)[0]


def generate_location() -> dict:
    """Generate realistic Delhi region coordinates."""
    lat = round(random.uniform(28.55, 28.75), 4)
    lon = round(random.uniform(77.05, 77.35), 4)
    return {"lat": lat, "lon": lon}


def generate_incident() -> tuple[str, dict]:
    """Generate a random incident.
    
    Returns:
        Tuple of (incident_type, incident_data).
    """
    # Select incident type
    incident_type = random.choice(list(INCIDENT_TYPES.keys()))
    text = random.choice(INCIDENT_TYPES[incident_type])
    
    # Generate metadata
    incident = {
        "text": text,
        "source_type": random.choice(SOURCE_TYPES),
        "urgency": weighted_choice(URGENCY_OPTIONS),
        "status": "pending",
        "zone_id": random.choice(ZONES),
        "location": generate_location(),
    }
    
    return incident_type, incident


def send_incident(incident: dict, max_retries: int = 5) -> str | None:
    """Send incident to API with exponential backoff.
    
    Args:
        incident: Incident data.
        max_retries: Maximum retry attempts.
    
    Returns:
        Incident ID or None if failed.
    """
    backoff = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json=incident, timeout=10)
            response.raise_for_status()
            return response.json().get("incident_id")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"  ⚠ API error, retrying in {backoff}s: {e}")
                time.sleep(backoff)
                backoff = min(30, backoff * 2)
            else:
                print(f"  ✗ Failed after {max_retries} attempts: {e}")
                return None


def main():
    """Run disaster simulation loop."""
    print("=" * 60)
    print("RESPOND Disaster Simulation")
    print("=" * 60)
    print(f"API endpoint: {API_URL}")
    print("Press CTRL+C to stop")
    print("-" * 60)
    
    count = 0
    
    try:
        while True:
            # Generate incident
            incident_type, incident = generate_incident()
            
            # Send to API
            incident_id = send_incident(incident)
            
            if incident_id:
                count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(
                    f"[{timestamp}] #{count} | "
                    f"{incident_type:20} | "
                    f"{incident['urgency']:8} | "
                    f"{incident['zone_id']:7} | "
                    f"ID: {incident_id[:8]}..."
                )
            
            # Wait before next incident
            time.sleep(3)
    
    except KeyboardInterrupt:
        print("\n" + "-" * 60)
        print(f"Simulation stopped. Total incidents ingested: {count}")
        print("=" * 60)


if __name__ == "__main__":
    main()

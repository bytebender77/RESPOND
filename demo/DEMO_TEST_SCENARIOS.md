# 🧪 RESPOND - Ultimate Demo Guide

This guide provides a structured walkthrough for demonstrating the full capabilities of the RESPOND system. It includes a library of **15+ test incidents** and detailed scenarios.

---

## ⚡ Quick Start

1.  **Reset Database** (Optional but recommended):
    ```bash
    curl -X DELETE http://127.0.0.1:8000/reset
    curl http://127.0.0.1:8000/setup
    ```
2.  **Open Dashboard**: [http://127.0.0.1:5500](http://127.0.0.1:5500)

---

## 📚 Incident Library (Copy-Paste Ready)

Use these varied incidents to populate your database. Mix and match urgencies and zones.

### 🔥 Fire & Explosion (Critical)
1.  **Residential Fire**:
    `Fire reported at 34 Oak Street apartment complex, heavy smoke visible from 3rd floor, residents evacuating.`
2.  **Industrial Explosion**:
    `Loud explosion heard at chemical plant in Zone 4, possible gas leak, multiple workers unaccounted for.`
3.  **Wildfire**:
    `Brush fire spreading rapidly near highway exit 12, threatening nearby homes due to high winds.`

### 🚑 Medical & Rescue (High)
4.  **Mass Casualty**:
    `Metro train derailment at Central Station, multiple injuries reported, passengers trapped in lead car.`
5.  **Traffic Accident**:
    `Multi-vehicle collision on Main Bridge, bus overturned, traffic completely blocked.`
6.  **Structural Collapse**:
    `Old warehouse roof collapsed during renovation, construction crew trapped inside debris.`

### 🌊 Natural Disasters (High/Critical)
7.  **Flash Flood**:
    `River overflowing banks in low-lying residential area, water entering ground floor homes.`
8.  **Landslide**:
    `Mudslide blocking mountain pass road, vehicles stranded, power lines down.`
9.  **Earthquake Damage**:
    `Significant structural cracks appearing in city hospital foundation after tremors.`

### 🛡️ Public Safety (Medium)
10. **Suspicious Package**:
    `Unattended black bag left near stadium entrance, canine unit requested for inspection.`
11. **Crowd Control**:
    `Large protest gathering at City Hall turning aggressive, barriers breached.`
12. **Chemical Spill**:
    `Tanker truck leaking unidentified liquid on interstate, strong chemical odor reported.`

### 🔧 Infrastructure (Low/Medium)
13. **Power Outage**:
    `Grid failure affecting 3 neighborhood blocks, traffic lights out at major intersections.`
14. **Water Main Break**:
    `Main pipe burst flooding downtown street, road surface buckling.`
15. **Telecom Failure**:
    `Cellular tower down in Zone 2, emergency calls failing to connect.`

---

## 🎬 Master Scenario: "The Bridge Collapse"

Follow this script to demonstrate **every key feature** in 5 minutes.

### Phase 1: Ingestion & Deduplication
1.  **Ingest Incident A**:
    *   **Text**: "Bridge reported collapsing near reaction park" (Note: "reaction" is a typo for "recreation")
    *   **Source**: Call
    *   **Urgency**: Critical
    *   **Status**: Pending
    *   *Result*: **✓ NEW** (Copy this Incident ID)
2.  **Ingest Incident B (Duplicate)**:
    *   **Text**: "Big bridge collapse near recreation park, cars in water"
    *   **Source**: Social
    *   *Result*: **🔄 DEDUPLICATED** (Same ID as A, Evidence Check increases)

### Phase 2: Multi-Modal Evidence
1.  Click **🖼️ Use for Media** on the success card.
2.  **Upload Image**:
    *   Select a photo of a bridge/structure collapse.
    *   Click **Upload**.
3.  **Upload Audio**:
    *   Select audio file (e.g., call recording).
    *   Click **Transcribe & Reinforce**.
    *   *Result*: **Confusion Check** (Similarity score shown, Transcript displayed).

### Phase 3: Search & Context
1.  Go to **Incidents Tab**.
2.  Search Query: `bridge infrastructure failure`
3.  **Verify**:
    *   Incident shows **✓ Multi-source Confirmed** (because of Text + Image + Audio).
    *   Confidence Score should be high (>85%).
4.  Expand **📋 Evidence Chain** to show all 3 pieces of data linked together.

### Phase 4: AI Recommendations
1.  With the search results visible, click **🎯 Recommend Actions**.
2.  **Verify**:
    *   AI suggests `DISPATCH_HEAVY_RESCUE` or `CLOSE_ROADS`.
    *   Priority is **5/5**.

### Phase 5: Response (Deployment)
1.  Click **🚒 Use for Deployment**.
2.  **Create Deployment**:
    *   **Action**: Dispatch Rescue Team
    *   **Unit**: Heavy Rescue 1
    *   **Status**: En Route
3.  **Update Deployment**:
    *   Change status to `On Site`.
    *   Add Note: "Team arrived, beginning extraction."

---

## 🔍 Testing "Contextual Image Search"

This tests the new feature where images show specific text descriptions.

1.  **Upload Images** for two *different* incidents:
    *   Incident 1 (Fire): Upload fire image. description: "Fire at building"
    *   Incident 2 (Flood): Upload flood image. description: "Flood in street"
2.  Go to **Media Tab** -> **Search Images**.
3.  Query: `disaster`
4.  **Result**:
    *   You see both images.
    *   **Crucially**: Under the fire image, it says "Fire at building...". Under the flood image, it says "Flood in street...".
    *   **Success**: You can identify which is which without clicking!

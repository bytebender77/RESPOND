# 🧪 RESPOND - Fresh Demo Scenarios (Batch 2)

**Status:** ✨ NEW (Unused)  
**Focus:** Complex, multi-stage events for advanced testing.

---

## ⚡ Quick Reset
Before starting, clear your database to avoid confusion with old data.
```bash
curl -X DELETE http://127.0.0.1:8000/reset
curl http://127.0.0.1:8000/setup
```

---

## 📚 Incident Library (Fresh Batch)

### ☣️ Scenario A: "The Subway Bio-Hazard" (Medical/Panic)
*Good for testing: Sensor data, Crowd panic, Urgent response.*

1.  **Gas Leak**:
    `Strange almond-like smell reported at Metro Central Station platform, passengers coughing.`
2.  **Sensor Alert**:
    `Chemical sensor HX-99 detected dangerous levels of Sarin gas particles in Zone-4 subway tunnel.`
3.  **Panic/Stampede**:
    `Stampede reported at Metro exit gates, multiple people crushed, crowd moving towards downtown.`
4.  **Medical Emergency**:
    `Three people unconscious near ticket counter, foaming at mouth, requesting immediate HAZMAT.`

### � Scenario B: "The Smart City Blackout" (Cyber/Infrastructure)
*Good for testing: Cascading failures, Deduplication.*

5.  **Substation Explosion**:
    `Loud bang heard at North Grid Substation, black smoke rising, entire neighborhood lost power.`
6.  **Traffic Chaos**:
    `All traffic lights out at Main & 4th intersection, 5-car pileup reported.`
7.  **Looting**:
    `Store windows smashed at Electronics Store during blackout, looting in progress.`
8.  **Hospital Power Failure**:
    `City Hospital backup generator failed to start, ICU on battery power, requesting emergency generators.`

### 🌀 Scenario C: "The Typhoon Surge" (Natural Disaster)
*Good for testing: Image search ("flood", "water"), Wide-area response.*

9.  **Levee Breach**:
    `Sea wall breached at Harbor Point, ocean water entering financial district streets.`
10. **Stranded Vehicles**:
    `School bus trapped in rising floodwaters at underpass near Zone-2, children detailed inside.`
11. **Roof Collapse**:
    `High winds tore roof off Sports Arena, debris falling onto highway.`
12. **Floating Debris**:
    `Large shipping containers floating down Main Street, impacting buildings.`

---

## 🎬 Master Script: "Operation Bio-Shield"

**Theme:** Coordinating a response to a chemical attack in the subway.

### Phase 1: Detection (The "Sensor" vs "Human")
1.  **Ingest Human Report**:
    *   *Text:* `People passing out on the subway platform, weird smell.`
    *   *Source:* Social
    *   *Result:* **✓ NEW**
2.  **Ingest Sensor Report (Deduplication Test)**:
    *   *Text:* `Environmental sensor detected toxic gas irregularity at subway platform.`
    *   *Source:* Sensor
    *   *Result:* **🔄 DEDUPLICATED** (or NEW depending on threshold). *Key learning: Even if it doesn't dedup, it's fine. If it does, great.*

### Phase 2: Verification (The Audio Evidence)
1.  Go to **Media Tab** (Select the human report).
2.  **Upload Audio** (Prevert recording of a siren or coughing):
    *   *Action:* Transcribe & Reinforce.
    *   *Story:* "We received a voice note from a passenger."
    *   *Expectation:* **✅ Reinforcement Accepted** (Use audio containing words like "cant breathe", "gas", "help").

### Phase 3: Investigation (Context Search)
1.  Go to **Incidents Tab**.
2.  Search: `chemical attack victims`
3.  **Verify**: The "People passing out" incident appears top of list.

### Phase 4: Response (The HAZMAT Team)
1.  Click **Recommend Actions**
    *   Look for `DISPATCH_HAZMAT` or `EVACUATE` suggestions.
2.  **Create Deployment**:
    *   *Action:* Dispatch HAZMAT Unit 1
    *   *Apparatus:* Bio-Defense Truck
    *   *Zone:* Zone-4
3.  **Update Status**:
    *   Set to: `En Route` -> `On Site`

### Phase 5: Resolution
1.  Update Incident Status to **Resolved**.
2.  Update Deployment to **Completed**.

---

## 📸 Image Search Test Set
*Use these prompts if you upload relevant images:*

*   **For Blackout:** Search `dark street` or `traffic jam`.
*   **For Bio-Hazard:** Search `crowd panic` or `subway`.
*   **For Typhoon:** Search `flood water` or `floating debris`.

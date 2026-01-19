# RESPOND — Demo Guide

**Sample Queries, Test Data & Interaction Logs for Frontend Testing**

---

## 🧪 Sample Incidents to Ingest

Copy-paste these into the **Ingest Incident** form on the dashboard:

---

### 1. Fire Emergency (Critical)

| Field | Value |
|-------|-------|
| **Text** | Major fire outbreak in commercial district near Central Mall. Heavy smoke visible, multiple floors affected. Immediate evacuation required. |
| **Source** | social |
| **Urgency** | critical |
| **Status** | pending |
| **Zone ID** | zone-1 |
| **Latitude** | 28.6129 |
| **Longitude** | 77.2295 |

---

### 2. Flood Warning (Critical)

| Field | Value |
|-------|-------|
| **Text** | Flash flood warning in residential colony. Water level rising rapidly, roads submerged. Multiple families stranded on rooftops. |
| **Source** | sensor |
| **Urgency** | critical |
| **Status** | pending |
| **Zone ID** | zone-3 |
| **Latitude** | 28.5845 |
| **Longitude** | 77.0512 |

---

### 3. Building Collapse (Critical)

| Field | Value |
|-------|-------|
| **Text** | Multi-story building collapsed near metro station. Approximately 15-20 people believed trapped under debris. Rescue teams needed urgently. |
| **Source** | call |
| **Urgency** | critical |
| **Status** | pending |
| **Zone ID** | zone-4 |
| **Latitude** | 28.6358 |
| **Longitude** | 77.2245 |

---

### 4. Earthquake Aftershock (High)

| Field | Value |
|-------|-------|
| **Text** | Strong earthquake aftershock felt across multiple zones. Minor structural cracks reported in old buildings. Residents advised to stay outdoors. |
| **Source** | report |
| **Urgency** | high |
| **Status** | pending |
| **Zone ID** | zone-2 |
| **Latitude** | 28.7041 |
| **Longitude** | 77.1025 |

---

### 5. Gas Leak (Critical)

| Field | Value |
|-------|-------|
| **Text** | Gas pipeline leak detected in industrial area. Strong smell of gas reported. Evacuation of nearby residential blocks recommended. |
| **Source** | sensor |
| **Urgency** | critical |
| **Status** | pending |
| **Zone ID** | zone-2 |
| **Latitude** | 28.6892 |
| **Longitude** | 77.1534 |

---

## 🔍 Sample Search Queries

After ingesting incidents, try these searches:

| Query | Expected Results |
|-------|------------------|
| `fire smoke evacuation` | Fire incidents at top |
| `flood water trapped rooftops` | Flood incident |
| `collapse trapped rescue` | Building collapse |
| `earthquake tremor cracks` | Earthquake aftershock |
| `gas leak evacuation` | Gas pipeline incident |
| `critical emergency` | All critical incidents |
| `zone-4` | Incidents in zone-4 |

---

## 🎛️ Filter Combinations

| Urgency | Status | Last Hours | Expected |
|---------|--------|------------|----------|
| critical | pending | 24 | Critical pending incidents |
| high | - | 1 | High urgency in last hour |
| - | acknowledged | - | Acknowledged incidents |

---

## 📋 Expected Search Response

```json
{
  "query": "fire smoke emergency",
  "count": 3,
  "results": [
    {
      "id": "52bea223-9d79-420b-8470-1d12614f60c0",
      "score": 0.8442,
      "payload": {
        "text": "Major fire outbreak in commercial district...",
        "urgency": "critical",
        "status": "pending",
        "zone_id": "zone-1"
      },
      "final_score": 0.8442,
      "decay_factor": 1.0,
      "age_seconds": 45,
      "evidence": {
        "confidence_score": 0.58,
        "is_multi_source_confirmed": true,
        "evidence_count": 1
      }
    }
  ]
}
```

---

## 🔄 Status Update Test

1. Search for any incident
2. Note the incident ID
3. Use the dropdown to change status: `pending → acknowledged`
4. Click **Update**
5. Search again — status badge should change

---

## 📊 Reinforcement Test

To test confidence increase:

1. Ingest the Fire incident (above)
2. Search for "fire" — note confidence is 50%
3. Run this curl command:

```bash
curl -X POST "http://127.0.0.1:8000/memory/incident/<INCIDENT_ID>/reinforce" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "call",
    "text": "Emergency call confirms major fire at Central Mall, heavy smoke, evacuation underway"
  }'
```

4. Search again — confidence should increase to ~58%
5. "Multi-source ✓" badge should appear

---

## 🎯 Recommendation Test

1. Search for "collapse trapped rescue"
2. Click **🎯 Recommend Actions**
3. Expected actions:
   - `DISPATCH_SEARCH_AND_RESCUE` (Priority 5)
   - `PRIORITIZE_HEAVY_EQUIPMENT` (Priority 5)

---

## 📋 Interaction Log Example

### Session Flow:

```
1. [INGEST] Fire at Central Mall
   → Response: {"incident_id": "52bea223...", "message": "Incident ingested"}

2. [INGEST] Flood in residential area
   → Response: {"incident_id": "346c268f...", "message": "Incident ingested"}

3. [SEARCH] Query: "fire emergency"
   → Found 1 result, score: 0.84, confidence: 50%

4. [REINFORCE] Fire incident with call
   → Similarity: 0.84, accepted: true, new_confidence: 0.58

5. [SEARCH] Query: "fire emergency" (again)
   → Same result, confidence now 58%, multi-source: ✓

6. [UPDATE] Fire status: pending → acknowledged
   → Response: {"old_status": "pending", "new_status": "acknowledged"}

7. [RECOMMEND] Query: "building collapse"
   → Actions: DISPATCH_SEARCH_AND_RESCUE, PRIORITIZE_HEAVY_EQUIPMENT
```

---

## 🧹 Reset Database

To clear all data and start fresh:

```bash
curl -X DELETE http://127.0.0.1:8000/reset
```

Then re-run setup:

```bash
curl http://127.0.0.1:8000/setup
```

---

## 🎬 Demo Flow for Judges

1. **Ingest 3 incidents** (fire, flood, collapse)
2. **Search** with "fire emergency" → show semantic ranking
3. **Reinforce** fire with call → show confidence increase
4. **Update status** → show memory evolution
5. **Recommend actions** → show evidence-grounded output
6. **Start simulator** → show real-time ingestion

---

*Use this guide to test all RESPOND features!*

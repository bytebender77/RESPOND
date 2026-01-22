# RESPOND — Demo & Testing Script

**Multimodal Disaster Response Coordination System using Qdrant as Evolving Situational Memory**

*Convolve 4.0 | Qdrant MAS Track | Presentation Guide*

---

## 📋 Table of Contents

1. [Introduction (Elevator Pitch)](#1-introduction-elevator-pitch)
2. [System Concepts Explained](#2-system-concepts-explained)
3. [Tech Stack Overview](#3-tech-stack-overview)
4. [Manual Testing Script (Frontend)](#4-manual-testing-script-frontend)
5. [Expected Output Examples](#5-expected-output-examples)
6. [Closing & Summary](#6-closing--summary)

---

## 1. Introduction (Elevator Pitch)

> **Read this aloud to judges (30 seconds)**

---

*"When disaster strikes—an earthquake, a flood, a fire—emergency responders are flooded with thousands of reports from social media, sensors, and phone calls. The problem? Information overload. They can't tell what's urgent, what's already handled, or what's outdated.*

*RESPOND solves this by using Qdrant as an evolving situational memory. We ingest incident reports, embed them semantically, and enable hybrid search that combines meaning with filters like urgency, location, and time. But here's the key innovation: our memory evolves. Incidents update their status, gain confidence through multi-source reinforcement, and decay in priority as they age—all without re-indexing vectors.*

*The result? Responders get prioritized, actionable intelligence in seconds—not hours. In the golden 72 hours after a disaster, every minute saved means lives saved."*

---

## 2. System Concepts Explained

> **Use this section to explain concepts to judges in simple terms.**

---

### 2.1 What is an Incident?

An **incident** is a single disaster-related report. It could come from:
- A social media post: *"Fire at Central Mall, smoke visible"*
- A sensor alert: *"Water level critical at River Bridge"*
- A phone call: *"People trapped in collapsed building"*

Each incident has:
- **Text** — the report content
- **Source type** — social, sensor, call, or report
- **Urgency** — critical, high, medium, low
- **Location** — latitude/longitude coordinates
- **Zone ID** — geographic region identifier

---

### 2.2 What is a Qdrant Vector Point?

When we ingest an incident, we convert it into a **vector point** stored in Qdrant:

| Component | Description |
|-----------|-------------|
| **ID** | Unique identifier (UUID) |
| **Vector** | 384 floating-point numbers representing the text's meaning |
| **Payload** | Structured metadata (urgency, status, location, timestamp, confidence, evidence_chain) |

**Why vectors?** Vectors let us search by *meaning*, not just keywords. "Building collapse with people trapped" will match "structural failure with victims" even though they share no exact words.

---

### 2.3 What are Text Embeddings?

An **embedding** is a mathematical representation of text as a list of numbers.

```
"Fire at Central Mall" → [0.023, -0.045, 0.112, ..., 0.087] (384 numbers)
```

We use the model `sentence-transformers/all-MiniLM-L6-v2`:
- **Size:** 384 dimensions
- **Speed:** ~50ms per embedding
- **Distance:** Cosine similarity (higher = more similar)

---

### 2.4 Why Semantic Search?

Traditional keyword search fails in disasters:
- Query "fire" won't find "smoke visible" or "burning building"
- Query "trapped" won't find "people stuck under debris"

**Semantic search** finds results by *meaning*:
- Query "fire emergency" finds "smoke visible", "flames spotted", "burning structure"
- Query "people trapped" finds "victims under rubble", "stuck in building"

---

### 2.5 What is Hybrid Search?

RESPOND combines two types of search:

| Type | How It Works |
|------|--------------|
| **Semantic** | Find incidents similar in meaning to the query |
| **Filters** | Narrow results by urgency, status, time range, geo radius |

**Example query:**
> "Find critical incidents about fire in Zone-4 from the last 6 hours within 5km of the hospital"

This is impossible with keyword search alone.

---

### 2.6 Why is Memory Important?

Traditional search treats every query as independent. RESPOND treats incidents as **evolving entities**:

| Memory Feature | What It Does |
|----------------|--------------|
| **Status Evolution** | pending → acknowledged → resolved |
| **Confidence Boosting** | Multi-source reports increase confidence |
| **Evidence Chain** | Every confirmation is logged with source + timestamp |
| **Time Decay** | Old incidents rank lower automatically |

**Key insight:** All updates happen via Qdrant payload operations—**no re-embedding needed**.

---

### 2.7 What is Reinforcement / Evidence Chain?

When multiple sources report the same incident, we **reinforce** it:

1. A social media post reports a fire (confidence: 0.5)
2. A phone call confirms the same fire (similarity: 0.78)
3. Confidence boosts to 0.578
4. `evidence_chain` now contains both reports

**Multi-source confirmation** = higher priority + more reliable

---

### 2.8 What is Decay Reranking?

Fresh information is more valuable than old information:

| Incident Age | Decay Factor | Effect |
|--------------|--------------|--------|
| ≤ 1 hour | 1.0 | Full score |
| ≤ 6 hours | 0.8 | Slightly reduced |
| ≤ 24 hours | 0.5 | Half score |
| > 24 hours | 0.2 | Low priority |

**Final Score = Semantic Score × Decay Factor**

A highly relevant but old incident will rank lower than a moderately relevant fresh incident.

---

### 2.9 What is Action Recommendation?

RESPOND suggests actions based on incident keywords and status:

| Trigger | Action |
|---------|--------|
| "fire", "smoke" | DISPATCH_FIRE_BRIGADE |
| "flood", "water" | ISSUE_EVACUATION_ALERT |
| "collapse", "trapped" | PRIORITIZE_HEAVY_EQUIPMENT |
| Critical + Pending | DISPATCH_SEARCH_AND_RESCUE |
| Multi-source confirmed | Priority boost (+1) |

**Important:** Actions are rule-based, not LLM-generated. No hallucination risk.

---

## 3. Tech Stack Overview

> **Explain why each technology was chosen.**

---

| Component | Technology | Why We Chose It |
|-----------|------------|-----------------|
| **Backend** | FastAPI + Pydantic | Async, fast, automatic validation and OpenAPI docs |
| **Vector DB** | Qdrant Cloud | Hybrid search, payload indexing, geo queries, in-place updates |
| **Embeddings** | all-MiniLM-L6-v2 | Fast (50ms), accurate, small (384 dims), proven |
| **Frontend** | HTML + CSS + JS | Simple, no framework overhead, judge-friendly |
| **Simulation** | simulate_disaster.py | Auto-generates realistic incidents for demo |

### Why Qdrant?

| Qdrant Feature | RESPOND Usage |
|----------------|---------------|
| **Hybrid Filtering** | Semantic + urgency + status + zone filters |
| **Geo-Radius Search** | Find incidents within N km of any point |
| **In-Place Updates** | Status + confidence updates without re-embedding |
| **Payload Indexing** | Fast filtering on timestamp, urgency, status, zone |
| **Scalability** | Sub-100ms at millions of vectors |

---

## 4. Manual Testing Script (Frontend)

> **Follow these steps exactly during the demo.**
> 
> **Prerequisites:**
> - Backend running at `http://127.0.0.1:8000`
> - Frontend running at `http://127.0.0.1:5500`
> - Collections initialized via `/setup`

---

### Step 0: Verify System is Running

1. Open browser → Navigate to `http://127.0.0.1:8000/health`
2. You should see:
   ```json
   {"status": "healthy", "qdrant": "connected"}
   ```
3. If not connected, check your `.env` file for `QDRANT_URL` and `QDRANT_API_KEY`

---

### A. Ingest Incidents (Frontend Form)

> **Goal:** Add test incidents to the system

---

#### A1. Fire Incident

1. Open frontend: `http://127.0.0.1:5500`
2. Find the **"Ingest Incident"** form
3. Fill in:
   | Field | Value |
   |-------|-------|
   | Text | `Fire spotted at Central Mall, heavy smoke visible from 3rd floor` |
   | Source Type | `social` |
   | Urgency | `critical` |
   | Zone ID | `zone-1` |
   | Latitude | `28.6139` |
   | Longitude | `77.2090` |

4. Click **Submit**
5. **Expected Response:**
   ```json
   {
     "incident_id": "a1b2c3d4-...",
     "message": "Incident ingested"
   }
   ```
6. **Copy the incident_id** — you'll need it for reinforcement testing

---

#### A2. Flood Incident

1. Fill in:
   | Field | Value |
   |-------|-------|
   | Text | `Water level rising rapidly at River Bridge, evacuation needed` |
   | Source Type | `sensor` |
   | Urgency | `high` |
   | Zone ID | `zone-2` |
   | Latitude | `28.5500` |
   | Longitude | `77.2500` |

2. Click **Submit**
3. **Expected:** incident_id returned

---

#### A3. Building Collapse Incident

1. Fill in:
   | Field | Value |
   |-------|-------|
   | Text | `Building collapsed near Government School, multiple people trapped under debris` |
   | Source Type | `call` |
   | Urgency | `critical` |
   | Zone ID | `zone-4` |
   | Latitude | `28.6200` |
   | Longitude | `77.2150` |

2. Click **Submit**
3. **Expected:** incident_id returned
4. **Save this incident_id** — you'll use it for reinforcement

---

### B. Search Incidents (Frontend Search Panel)

> **Goal:** Demonstrate hybrid semantic search with filters

---

#### B1. Fire Search

1. Find the **"Search Incidents"** panel
2. Enter:
   | Field | Value |
   |-------|-------|
   | Query | `fire smoke residential` |
   | Limit | `5` |
   | Urgency | `critical` (or leave blank for all) |
   | Last Hours | `24` |

3. Click **Search**
4. **Expected Results:**
   - Fire incident ranks highest
   - Flood incident may appear (low score)
   - Collapse incident should not appear

---

#### B2. Collapse Search

1. Enter:
   | Field | Value |
   |-------|-------|
   | Query | `people trapped collapse` |
   | Limit | `5` |

2. Click **Search**
3. **Expected Results:**
   - Collapse incident ranks highest
   - Other incidents may appear with lower scores

---

#### B3. Flood Search

1. Enter:
   | Field | Value |
   |-------|-------|
   | Query | `flood evacuation water rising` |
   | Limit | `5` |

2. Click **Search**
3. **Expected Results:**
   - Flood incident ranks highest

---

#### Understanding Search Results

| Field | Meaning |
|-------|---------|
| `score` | Raw semantic similarity (0.0 to 1.0) |
| `decay_factor` | Time-based penalty (1.0 = fresh, 0.2 = old) |
| `final_score` | score × decay_factor |
| `confidence_score` | How reliable is this incident (0.5 = base, increases with reinforcement) |
| `is_multi_source_confirmed` | True if 2+ sources confirmed this incident |
| `evidence_count` | Number of reinforcing reports |

---

### C. Status Update Testing

> **Goal:** Demonstrate memory evolution

---

#### C1. Update Status: pending → acknowledged

1. From search results, **copy an incident ID**
2. Find the **"Update Status"** section (or use curl):
   ```bash
   curl -X PATCH "http://127.0.0.1:8000/memory/incident/{incident_id}/status" \
     -H "Content-Type: application/json" \
     -d '{"new_status": "acknowledged"}'
   ```
3. **Expected Response:**
   ```json
   {
     "incident_id": "...",
     "old_status": "pending",
     "new_status": "acknowledged"
   }
   ```

---

#### C2. Update Status: acknowledged → resolved

1. Same incident, run:
   ```bash
   curl -X PATCH "http://127.0.0.1:8000/memory/incident/{incident_id}/status" \
     -H "Content-Type: application/json" \
     -d '{"new_status": "resolved"}'
   ```
2. **Expected Response:**
   ```json
   {
     "incident_id": "...",
     "old_status": "acknowledged",
     "new_status": "resolved"
   }
   ```

---

#### What Changed in Qdrant?

| Before | After |
|--------|-------|
| `payload.status = "pending"` | `payload.status = "resolved"` |

**Key point:** The vector was NOT re-embedded. Only the payload was updated in-place.

---

### D. Reinforcement Testing

> **Goal:** Demonstrate multi-source confirmation and evidence chains

---

#### D1. Reinforce an Incident

1. Use the **collapse incident ID** from Step A3
2. Send reinforcement:
   ```bash
   curl -X POST "http://127.0.0.1:8000/memory/incident/{incident_id}/reinforce" \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "call",
       "text": "Emergency call confirms building collapse, multiple victims trapped"
     }'
   ```
3. **Expected Response:**
   ```json
   {
     "incident_id": "...",
     "similarity": 0.7856,
     "accepted": true,
     "old_confidence": 0.5,
     "new_confidence": 0.578,
     "reinforced_count": 1
   }
   ```

---

#### D2. Add Second Reinforcement

1. Same incident, different source:
   ```bash
   curl -X POST "http://127.0.0.1:8000/memory/incident/{incident_id}/reinforce" \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "report",
       "text": "Field team on site: structural collapse confirmed, rescue operation starting"
     }'
   ```
2. **Expected Response:**
   ```json
   {
     "incident_id": "...",
     "similarity": 0.6523,
     "accepted": true,
     "old_confidence": 0.578,
     "new_confidence": 0.643,
     "reinforced_count": 2
   }
   ```

---

#### What Changed in Qdrant?

| Field | Before | After |
|-------|--------|-------|
| `confidence_score` | 0.5 | 0.643 |
| `evidence_chain` | `[]` | `[{...}, {...}]` |
| `is_multi_source_confirmed` | `false` | `true` |

**Key point:** Higher confidence = higher priority in search results.

---

### E. Recommendations Testing

> **Goal:** Demonstrate evidence-grounded action generation

---

#### E1. Get Recommendations

1. Run:
   ```bash
   curl -X POST "http://127.0.0.1:8000/recommend/actions" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "school collapse trapped rescue urgent",
       "limit": 5
     }'
   ```

2. **Expected Response:**
   ```json
   {
     "query": "school collapse trapped rescue urgent",
     "actions": [
       {
         "action_type": "DISPATCH_SEARCH_AND_RESCUE",
         "priority": 5,
         "reason": "Detected 'trapped' in incident; urgency is critical; multi-source confirmed",
         "incident_ids": ["a1b2c3d4-..."]
       },
       {
         "action_type": "PRIORITIZE_HEAVY_EQUIPMENT",
         "priority": 4,
         "reason": "Detected 'collapse' in incident",
         "incident_ids": ["a1b2c3d4-..."]
       }
     ]
   }
   ```

---

#### Understanding Recommendations

| Field | Meaning |
|-------|---------|
| `action_type` | What action should be taken |
| `priority` | 1 (low) to 5 (critical) |
| `reason` | Why this action was generated |
| `incident_ids` | Which incidents triggered this action |

**Key point:** Every recommendation is traceable to specific incidents. No hallucination.

---

## 5. Expected Output Examples

> **Use these as reference during the demo.**

---

### 5.1 Search Results Example

```json
{
  "count": 3,
  "query": "building collapse trapped",
  "results": [
    {
      "id": "91b1f4f1-2a9b-4002-8298-47b55b0cccab",
      "text": "Building collapsed near Government School, multiple people trapped under debris",
      "source_type": "call",
      "urgency": "critical",
      "status": "acknowledged",
      "zone_id": "zone-4",
      "score": 0.9234,
      "decay_factor": 1.0,
      "final_score": 0.9234,
      "evidence": {
        "is_multi_source_confirmed": true,
        "confidence_score": 0.643,
        "evidence_count": 2
      }
    },
    {
      "id": "b10fb3b2-5c4e-4f1a-9876-def123456789",
      "text": "Structural damage reported at old apartment complex",
      "source_type": "social",
      "urgency": "high",
      "status": "pending",
      "zone_id": "zone-3",
      "score": 0.6123,
      "decay_factor": 0.8,
      "final_score": 0.4898,
      "evidence": {
        "is_multi_source_confirmed": false,
        "confidence_score": 0.5,
        "evidence_count": 0
      }
    }
  ]
}
```

---

### 5.2 Evidence Chain Example

After reinforcement, the incident payload contains:

```json
{
  "evidence_chain": [
    {
      "source_type": "call",
      "text": "Emergency call confirms building collapse, multiple victims trapped",
      "similarity": 0.7856,
      "timestamp": "2026-01-20T12:30:45Z"
    },
    {
      "source_type": "report",
      "text": "Field team on site: structural collapse confirmed, rescue operation starting",
      "similarity": 0.6523,
      "timestamp": "2026-01-20T12:45:22Z"
    }
  ]
}
```

---

### 5.3 Recommendations Example

```json
{
  "query": "fire emergency smoke",
  "actions": [
    {
      "action_type": "DISPATCH_FIRE_BRIGADE",
      "priority": 5,
      "reason": "Detected 'fire' and 'smoke' in incident; urgency is critical",
      "incident_ids": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]
    },
    {
      "action_type": "ISSUE_EVACUATION_ALERT",
      "priority": 4,
      "reason": "Detected 'fire' in residential zone",
      "incident_ids": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]
    }
  ]
}
```

---

## 6. Closing & Summary

> **Use this to wrap up your presentation.**

---

### Why Qdrant is Central

RESPOND is **not possible without Qdrant**:

| Feature | How RESPOND Uses It |
|---------|---------------------|
| **Hybrid Search** | Semantic meaning + operational filters |
| **Payload Updates** | Status evolution + confidence boosting in-place |
| **Geo Queries** | Find incidents within radius of hospitals/schools |
| **Indexing** | Fast filtering on urgency, status, time |

**Key innovation:** Qdrant is used as **evolving situational memory**, not just a retrieval store.

---

### What Makes RESPOND Unique

| Innovation | Why It Matters |
|------------|----------------|
| **Memory Evolution** | Incidents update status without re-embedding |
| **Multi-Source Reinforcement** | Confidence grows with independent confirmations |
| **Evidence Chains** | Every decision is traceable |
| **Time Decay** | Fresh information automatically prioritized |
| **Rule-Based Actions** | No LLM hallucination risk |

---

### Roadmap (Phase 2)

| Feature | Description |
|---------|-------------|
| **Image Embeddings** | CLIP-based satellite/drone imagery analysis |
| **Audio Embeddings** | Whisper transcription + embedding |
| **Auto-Clustering** | HDBSCAN for incident grouping |
| **Real-Time Dashboard** | WebSocket-based live updates |
| **Multi-Region** | Distributed Qdrant for scale |

---

### Thank You

> *"RESPOND transforms chaotic disaster reports into prioritized, actionable intelligence. By using Qdrant as evolving situational memory, we enable faster triage, better coordination, and ultimately—more lives saved.*
>
> *Thank you for your time. We're happy to answer any questions."*

---

*Built with ❤️ for Convolve 4.0 | Qdrant MAS Track*

**Repository:** [GitHub Link]

**Team:** [Your Team Name]

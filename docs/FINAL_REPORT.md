# RESPOND — Final Submission Report

**Multimodal Disaster Response Coordination System using Qdrant as Evolving Situational Memory**

*Convolve 4.0 | Qdrant MAS Track | Round 2 Submission (Jan 2026)*

---

## 1. Problem Statement

### What Societal Issue Are We Addressing?

When disaster strikes—an earthquake, a flood, a fire—emergency responders face **information overload**. Within minutes, they receive thousands of reports from social media posts, IoT sensors, phone calls, and field teams. The challenge is not lack of information, but too much of it:

| Challenge | Impact |
|-----------|--------|
| **Volume** | Thousands of reports per hour from multiple channels |
| **Ambiguity** | Natural language reports lack structure |
| **Duplication** | Same incident reported multiple times by different sources |
| **Decay** | A 6-hour-old report may no longer be relevant |
| **Coordination Gap** | Responders need to know *what to do*, not just *what happened* |

Traditional keyword search fails here. Searching for "fire" won't find "smoke visible" or "burning building." Filtering by time alone doesn't account for meaning.

### Why Does It Matter?

The first 72 hours after a disaster are called the **"golden hours"**—every minute of delay increases casualties. In disaster response, faster triage and verification directly improves rescue outcomes.

**RESPOND reduces decision latency by transforming chaotic, multi-source reports into prioritized, actionable intelligence.** Responders can find relevant incidents in seconds, trust high-confidence reports, and receive recommended actions—all powered by Qdrant's hybrid search and in-place memory updates.

---

## 2. System Design

### Architecture Overview

RESPOND follows a modular pipeline architecture:

<div style="page-break-inside: avoid;">

```
Sources (Social/Sensor/Call/Report) → Ingestion (Validate/Embed/Index) → Qdrant Cloud
     ↓
Hybrid Search (Semantic + Geo + Time + Filter) → Memory Layer (Evolution/Reinforcement/Decay)
     ↓
Recommendation Engine → Action Dashboard
```

</div>

**Data Flow:**

1. **Ingestion:** Incident reports arrive from multiple sources (social media, sensors, calls). Each report is validated, embedded into a 384-dimensional vector, and stored in Qdrant with structured metadata.

2. **Search:** Responders query using natural language. RESPOND combines semantic similarity with operational filters (urgency, status, zone, time window, geo-radius).

3. **Memory Evolution:** Incidents update their status, gain confidence through multi-source reinforcement, and decay in priority as they age. All updates happen via Qdrant payload operations—no re-embedding required.

4. **Recommendations:** Based on search results, the system generates rule-based action recommendations (e.g., "dispatch fire brigade") with full traceability to source incidents.

### Why Qdrant Is Critical

Qdrant is not just a storage layer—it is the **core intelligence engine** of RESPOND:

| Qdrant Feature | How RESPOND Uses It |
|----------------|---------------------|
| **Hybrid Filtering** | Combine semantic search with urgency, status, zone, and time filters in a single query |
| **Geo-Radius Search** | Find incidents within N km of a hospital, school, or command center |
| **In-Place Payload Updates** | Update incident status and confidence score without re-embedding vectors |
| **Payload Indexing** | Fast filtering on `timestamp_unix`, `urgency`, `status`, `zone_id` |
| **Scalability** | Sub-100ms queries even at millions of vectors |

**Key Insight:** RESPOND uses Qdrant as **evolving situational memory**. Incidents are not static documents—they update, reinforce, and decay. Qdrant's payload update capability makes this possible without costly re-indexing.

---

## 3. Multimodal Strategy

### What Data Types Are Used

| Modality | Source Examples | Status |
|----------|-----------------|--------|
| **Text** | Social media posts, call transcripts, field reports | ✅ Implemented |
| **Sensor Data** | IoT alerts, water level readings, seismic sensors | ✅ Implemented (as structured text) |
| **Image** | Satellite imagery, drone footage | 🔜 Roadmap (CLIP integration) |
| **Audio** | Emergency calls, radio communications | 🔜 Roadmap (Whisper transcription) |

Currently, RESPOND processes text-based incidents from four source types: `social`, `sensor`, `call`, and `report`. Sensor data is ingested as structured text alerts. The system is designed for future extension to images and audio via a modular `BaseEmbedder` interface.

### How Embeddings Are Created

**Model:** `sentence-transformers/all-MiniLM-L6-v2`  
**Dimensions:** 384  
**Distance Metric:** Cosine similarity  
**Speed:** ~50ms per embedding

When an incident is ingested, the text is converted into a vector:

```
"Fire spotted at Central Mall, heavy smoke visible"
    ↓
[0.023, -0.045, 0.112, ..., 0.087]  (384 floats)
```

This vector captures the **semantic meaning** of the text—allowing similarity-based retrieval.

### How Embeddings Are Queried

1. **Embed the query text** → 384-dimensional vector
2. **Build operational filters** → urgency, status, time window, geo-radius
3. **Execute hybrid search** in Qdrant → semantic + filtered
4. **Apply time decay** → fresh incidents rank higher
5. **Extract evidence metadata** → confidence score, evidence chain, multi-source flag
6. **Return ranked results**

**Example Ingestion Payload:**

```json
{
  "text": "Building collapsed near Government School, people trapped",
  "source_type": "call",
  "urgency": "critical",
  "zone_id": "zone-4",
  "location": {"lat": 28.6139, "lon": 77.2090}
}
```

This becomes a Qdrant point with vector + payload including `timestamp_unix`, `status: pending`, `confidence_score: 0.5`, and `evidence_chain: []`.

---

## 4. Search / Memory / Recommendation Logic

### 4.1 How Retrieval Works

RESPOND implements **hybrid search**—combining semantic similarity with structured filters:

| Component | Function |
|-----------|----------|
| **Semantic Similarity** | Query embedding vs. stored incident embeddings |
| **Status Filter** | pending / acknowledged / resolved |
| **Urgency Filter** | critical / high / medium / low |
| **Time Filter** | Last N hours (via `timestamp_unix`) |
| **Geo Filter** | Within N km of a coordinate |

**Search Flow:**
```
Query → Embed → Qdrant Hybrid Search → Decay Rerank → Evidence Extract → Return
```

### 4.2 How Memory Is Stored

Each incident is stored as a **Qdrant point**:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Unique identifier |
| `vector` | float[384] | Semantic representation |
| `text` | string | Original incident text |
| `source_type` | keyword | social / sensor / call / report |
| `urgency` | keyword | critical / high / medium / low |
| `status` | keyword | pending / acknowledged / resolved |
| `timestamp_unix` | integer | Ingestion time (for decay + filtering) |
| `confidence_score` | float | Reliability (0.5 to 1.0) |
| `evidence_chain` | array | List of confirming reports |
| `location` | geo | lat/lon for geo queries |
| `zone_id` | keyword | Geographic zone |

### 4.3 How Memory Is Updated

**Status Evolution** (payload-only, no re-embedding):
```
pending → acknowledged → resolved
```

Responders update status as incidents are handled. This is a simple payload update in Qdrant—the vector stays unchanged.

**Confidence Reinforcement:**

When a new report matches an existing incident:
1. Compute cosine similarity between original and new text
2. If similarity ≥ 0.65, accept as corroborating evidence
3. Boost confidence: `new_conf = min(1.0, old_conf + min(0.15, similarity × 0.1))`
4. Append to `evidence_chain` with source, text, similarity, and timestamp

**Example:** An incident with base confidence 0.5 receives a confirming phone call (similarity 0.78). Confidence increases to 0.578, and `evidence_chain` now contains the call details.

### 4.4 How Memory Is Reused (Decay Reranking)

Fresh information is more valuable than old information. RESPOND applies **time decay** during search:

| Incident Age | Decay Factor |
|--------------|--------------|
| ≤ 1 hour | 1.0 |
| ≤ 6 hours | 0.8 |
| ≤ 24 hours | 0.5 |
| > 24 hours | 0.2 |

**Final Score = Semantic Score × Decay Factor**

A highly relevant but old incident will rank lower than a moderately relevant fresh incident.

**Example Search Output:**

```json
{
  "id": "91b1f4f1-...",
  "text": "Building collapsed near school, people trapped",
  "score": 0.92,
  "decay_factor": 1.0,
  "final_score": 0.92,
  "evidence": {
    "confidence_score": 0.643,
    "is_multi_source_confirmed": true,
    "evidence_count": 2
  }
}
```

### 4.5 How Recommendations Are Generated

RESPOND's recommendation engine is **rule-based and evidence-grounded**—no LLM generation, no hallucination risk.

| Detected Keywords | Action Generated |
|-------------------|------------------|
| "fire", "smoke" | DISPATCH_FIRE_BRIGADE |
| "flood", "water" | ISSUE_EVACUATION_ALERT |
| "collapse", "trapped" | PRIORITIZE_HEAVY_EQUIPMENT |
| Critical + Pending | DISPATCH_SEARCH_AND_RESCUE |
| Multi-source confirmed | Priority boost (+1) |

Every recommendation includes the `incident_ids` that triggered it—full traceability.

**Example Recommendation Output:**

```json
{
  "action_type": "DISPATCH_SEARCH_AND_RESCUE",
  "priority": 5,
  "reason": "Detected 'trapped' in incident; urgency is critical; multi-source confirmed",
  "incident_ids": ["91b1f4f1-...", "b10fb3b2-..."]
}
```

---

## 5. Limitations & Ethics

### 5.1 Known Failure Modes

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Text + sensor only** | Cannot process images or audio directly | Modular `BaseEmbedder` designed for CLIP/Whisper extensions |
| **Rule-based recommendations** | Limited reasoning compared to LLMs | Trade-off: no hallucination, full traceability |
| **Single-region demo** | Not distributed | Qdrant Cloud supports multi-region; ready for scaling |
| **No authentication** | Demo-only security | Add OAuth/JWT for production deployment |
| **Embedding model limitations** | MiniLM may miss domain-specific language | Fine-tuning or domain-specific models possible |

### 5.2 Bias, Privacy, and Safety Considerations

**Privacy:**
- No personally identifiable information (PII) is stored
- Locations are stored at zone-level, not exact addresses
- Retention policy recommended for production (auto-expire old records)

**Bias & Fairness:**
- All sources are weighted equally (social, sensor, call, report)
- No geographic zone receives inherently lower priority
- Confidence is based on corroboration, not source type preference

**Safety & Human Oversight:**
- RESPOND is **decision support**, not automation—humans make final decisions
- Status transitions require explicit action (no auto-resolution)
- Every confidence change is logged with evidence
- Recommendations are rule-based—no LLM "creativity" or hidden reasoning

---

## Appendix: Quick Reference

### Qdrant Collection

**Primary:** `respond_situation_reports`

**Indexes:**
| Field | Type |
|-------|------|
| `timestamp_unix` | Integer |
| `urgency` | Keyword |
| `status` | Keyword |
| `zone_id` | Keyword |
| `location` | Geo |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ingest/incident` | Ingest new incident |
| `POST` | `/search/incidents` | Hybrid semantic search |
| `PATCH` | `/memory/incident/{id}/status` | Update status |
| `POST` | `/memory/incident/{id}/reinforce` | Add evidence |
| `POST` | `/recommend/actions` | Get recommendations |

### Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Pydantic |
| Vector DB | Qdrant Cloud |
| Embeddings | all-MiniLM-L6-v2 (384 dims) |
| Frontend | HTML + CSS + JavaScript |
| Simulation | scripts/simulate_disaster.py |

---

*Built with ❤️ for Convolve 4.0 | Qdrant MAS Track*

**Repository:** https://github.com/bytebender77/RESPOND

**Team:** Palak Soni , Kunal Kumar Gupta  

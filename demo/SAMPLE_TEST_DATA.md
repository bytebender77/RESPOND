# Sample Test Data for RESPOND Demo

This file contains realistic test data you can use to quickly populate the system for demos.

---

## 🔥 Quick Copy-Paste Incidents

### Critical Emergencies

**Fire Incident 1:**
```
Description: Building fire at residential tower, multiple floors affected, heavy smoke, residents trapped on floors 8-12
Source: Call
Urgency: Critical
Status: Pending
Zone: zone-1
Lat: 28.6139
Lon: 77.2090
```

**Fire Incident 2 (Dedup Test):**
```
Description: Large fire reported at residential building, thick smoke visible, people need rescue from upper floors
Source: Social
Urgency: Critical
Status: Pending
Zone: zone-1
Lat: 28.6145
Lon: 77.2095
```

**Collapse Incident:**
```
Description: Bridge collapse on highway near metro station, multiple vehicles trapped underneath, heavy casualties reported
Source: Sensor
Urgency: Critical
Status: Pending
Zone: zone-4
Lat: 28.5355
Lon: 77.3910
```

**Flood Emergency:**
```
Description: Severe flooding in residential area, water level rising rapidly, 50+ families stranded, rescue boats needed immediately
Source: Call
Urgency: Critical
Status: Pending
Zone: zone-5
Lat: 28.7041
Lon: 77.1025
```

### High Priority

**Gas Leak:**
```
Description: Major gas pipeline leak near shopping mall, strong odor reported, area being evacuated, explosion risk
Source: Report
Urgency: High
Status: Pending
Zone: zone-2
Lat: 28.4595
Lon: 77.0266
```

**Mass Casualty:**
```
Description: Metro train derailment at central station, multiple injuries reported, emergency medical teams required
Source: Call
Urgency: High
Status: Pending
Zone: zone-3
Lat: 28.6358
Lon: 77.2245
```

**Earthquake:**
```
Description: Earthquake magnitude 6.5 detected, buildings evacuated, structural damage visible, aftershocks expected
Source: Sensor
Urgency: High
Status: Pending
Zone: zone-all
Lat: 28.6139
Lon: 77.2090
```

### Medium Priority

**Power Outage:**
```
Description: Widespread power outage affecting 3 neighborhoods, traffic signals down, backup generators needed
Source: Report
Urgency: Medium
Status: Pending
Zone: zone-6
Lat: 28.5244
Lon: 77.2066
```

**Hazmat Spill:**
```
Description: Chemical tanker overturned on expressway, hazardous material spill, containment teams required
Source: Call
Urgency: Medium
Status: Pending
Zone: zone-7
Lat: 28.4089
Lon: 77.3178
```

### Low Priority

**Minor Fire:**
```
Description: Small electrical fire in office building basement, already extinguished by building security, no injuries
Source: Social
Urgency: Low
Status: Acknowledged
Zone: zone-2
Lat: 28.6304
Lon: 77.2177
```

**Medical Assist:**
```
Description: Elderly person fell at home, conscious and alert, requires non-emergency medical transport
Source: Call
Urgency: Low
Status: Pending
Zone: zone-1
Lat: 28.6431
Lon: 77.2197
```

---

## 🔄 Evidence Reinforcement Examples

Use these via API to test multi-source confirmation.

### For Fire Incident:
```bash
# Evidence 1 - Sensor
curl -X POST "http://127.0.0.1:8000/memory/incident/{INCIDENT_ID}/reinforce" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "sensor",
    "text": "Thermal imaging confirms active fire on floors 9 through 11, temperature exceeding 800°C"
  }'

# Evidence 2 - Social
curl -X POST "http://127.0.0.1:8000/memory/incident/{INCIDENT_ID}/reinforce" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "social",
    "text": "Witnesses report massive fire at apartment building, flames visible from blocks away"
  }'

# Evidence 3 - Report
curl -X POST "http://127.0.0.1:8000/memory/incident/{INCIDENT_ID}/reinforce" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "report",
    "text": "Fire department on scene, confirming residential tower fire with trapped occupants"
  }'
```

---

## 🔍 Search Query Examples

### High-Relevance Queries

```
Query: "fire emergency building rescue"
Expected: Fire incidents with rescue needs

Query: "collapse trapped casualties"
Expected: Structural collapse incidents

Query: "flood water rising evacuation"
Expected: Flooding incidents requiring evacuation

Query: "medical emergency ambulance needed"
Expected: Medical incidents

Query: "gas leak explosion risk"
Expected: Hazmat/gas incidents

Query: "earthquake structural damage"
Expected: Seismic incidents
```

### Filter Combinations

```
Query: "emergency"
Urgency: Critical
Status: Pending
→ All critical pending emergencies

Query: "fire"
Last Hours: 6
Zone: zone-1
→ Recent fires in zone-1

Query: "rescue"
Urgency: High, Critical
→ High priority rescue operations
```

---

## 🖼️ Image Search Queries

Test these after uploading disaster images:

```
"fire with heavy smoke and flames"
"flooded street with submerged vehicles"
"collapsed building with debris"
"rescue workers at emergency scene"
"damaged infrastructure after earthquake"
"evacuation of people from danger zone"
"emergency vehicles with flashing lights"
"disaster area with casualties"
```

---

## 🎯 Action Recommendation Queries

These should trigger specific action types:

```
Query: "building fire trapped residents"
Expected Actions: DISPATCH_FIRE_UNIT, DISPATCH_AMBULANCE, EVACUATE_ZONE

Query: "medical emergency casualties"
Expected Actions: DISPATCH_AMBULANCE, MEDICAL_TEAM

Query: "chemical spill hazardous"
Expected Actions: HAZMAT_TEAM, EVACUATE_ZONE

Query: "violence crime scene"
Expected Actions: DISPATCH_POLICE

Query: "earthquake structural damage"
Expected Actions: EVACUATE_ZONE, DISPATCH_FIRE_UNIT, MEDICAL_TEAM
```

---

## 🚒 Deployment Examples

### Multi-Incident Response

```
Action Type: Dispatch Fire Unit
Incident IDs: {fire_id_1}, {fire_id_2}, {fire_id_3}
Assigned Unit: Fire Rescue Unit 5
Zone: zone-1
Notes: Multiple fire incidents in same zone, coordinated response required
```

### Evacuation Operation

```
Action Type: Evacuate Zone
Incident IDs: {gas_leak_id}, {explosion_risk_id}
Assigned Unit: Evacuation Team Alpha
Zone: zone-2
Notes: High risk area, evacuate 1km radius, establish perimeter
```

### Medical Response

```
Action Type: Dispatch Ambulance
Incident IDs: {collapse_id}
Assigned Unit: Ambulance Team 3, Trauma Unit 7
Zone: zone-4
Notes: Mass casualty incident, multiple ambulances dispatched, trauma centers alerted
```

---

## 📊 Deduplication Test Sets

### Set 1: Same Incident, Different Wording

Submit these within 5 minutes of each other:

1. "Major fire at Central Plaza apartment building, floors 8-12 burning"
2. "Fire reported at Central Plaza apartments, upper floors affected"
3. "Blaze at Central Plaza residential tower, multiple floors on fire"

**Expected:** All should return same incident ID (deduplicated)

### Set 2: Similar but Different Incidents

1. "Fire at North Street residential building"
2. "Fire at South Street commercial building"

**Expected:** Two separate incident IDs (different locations)

### Set 3: Temporal Boundary Test

1. Submit: "Fire at Main Street building" → get ID
2. Wait 30 minutes
3. Submit: "Fire at Main Street building" → should get NEW ID (outside dedup window)

---

## 🧪 Status Lifecycle Test

Create one incident and update through all states:

```
1. [Ingest] → Status: Pending
2. [Quick Acknowledge] → Status: Acknowledged
3. [Update] → Status: Resolved
```

Track confidence changes at each step.

---

## 📈 Zone Distribution

For geographical testing, distribute incidents:

- **zone-1:** 3 fires, 1 medical
- **zone-2:** 2 floods, 1 gas leak
- **zone-3:** 1 earthquake, 1 collapse
- **zone-4:** 2 traffic, 1 hazmat
- **zone-5:** 1 flood, 1 evacuation

Search by zone to verify filtering.

---

## 🎬 Demo Script Data

**Perfect 10-minute demo sequence:**

### Phase 1: Initial Report (0:00)
```
Incident: "Residential building fire on 5th Avenue, people trapped, heavy smoke"
Source: Call
Urgency: Critical
```

### Phase 2: Confirmation (0:30)
```
Incident: "Fire at 5th Avenue building confirmed, multiple floors burning"
Source: Social
Urgency: Critical
→ Should deduplicate!
```

### Phase 3: Evidence Upload (1:00)
- Upload fire image
- Upload emergency call audio

### Phase 4: Search & Analysis (2:00)
```
Search: "fire rescue trapped"
→ View evidence chain
→ Multi-source confirmed badge
```

### Phase 5: Recommendations (3:00)
```
Click "Recommend Actions"
→ See AI suggestions
```

### Phase 6: Deployment (4:00)
```
Create: DISPATCH_FIRE_UNIT
Unit: Fire Rescue 5
→ Update: En Route
→ Update: On Site
```

### Phase 7: Resolution (5:00)
```
Update Incident: Acknowledged → Resolved
Update Deployment: Completed
```

---

## 🔗 Quick API Commands

### Reset Database (Start Fresh)
```bash
curl -X DELETE http://127.0.0.1:8000/reset
```

### Initialize Collections
```bash
curl http://127.0.0.1:8000/setup
```

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Ingest via API
```bash
curl -X POST "http://127.0.0.1:8000/ingest/incident" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Building fire emergency",
    "source_type": "call",
    "urgency": "critical",
    "zone_id": "zone-1",
    "location": {"lat": 28.6139, "lon": 77.2090}
  }'
```

### Search via API
```bash
curl -X POST "http://127.0.0.1:8000/search/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fire emergency",
    "limit": 10,
    "last_hours": 24
  }'
```

---

## 💡 Pro Tips

1. **Copy incident IDs immediately** - You'll need them for media uploads and deployments
2. **Test deduplication within 5 minutes** - The time window matters
3. **Use realistic descriptions** - Better semantic search results
4. **Upload actual images/audio** - Shows real CLIP/Whisper capability
5. **Create 5-10 incidents first** - Makes search/sort more interesting
6. **Try zone filtering via API** - Not available in UI yet

---

**Quick Start:** Copy the first 5 critical incidents above, ingest them, then test search and deployments!

*Last updated: January 22, 2026*

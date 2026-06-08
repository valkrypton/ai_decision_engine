# AI Decision Engine — Technical Specifications

## 1. Overview

Unified AI system converting Voice/Text input into ranked, actionable recommendations. Built on LangGraph. Serves multiple domains via shared pipeline.

**Domains:**
- CardDeals — restaurant + discount discovery
- HireStream — job/candidate matching
- Lead Finder — company scoring
- Travel Planner — itinerary recommendations

---

## 2. System Architecture

```
Voice/Text Input
      │
      ▼
  STT (if Voice)
      │
      ▼
  Normalization
      │
      ▼
  LangGraph Pipeline
  ┌─────────────────────────────────────────┐
  │  1. Input Understanding                 │
  │  2. Candidate Fetch                     │
  │  3. Enrichment                          │
  │  4. Ranking                             │
  │  5. Response Generation                 │
  └─────────────────────────────────────────┘
      │
      ▼
  Structured Output
```

---

## 3. LangGraph Pipeline Nodes

### 3.1 Input Understanding
- **Input:** raw text or transcribed speech
- **Output:** `intent`, `entities`
- **Responsibilities:** intent classification, entity extraction (location, budget, role, etc.)

### 3.2 Candidate Fetch
- **Input:** `intent`, `entities`
- **Output:** `candidates[]`
- **Responsibilities:** domain-specific data retrieval (DB, API, vector store)

### 3.3 Enrichment
- **Input:** `candidates[]`
- **Output:** `enriched[]`
- **Responsibilities:** augment candidates with external data (reviews, scores, metadata)

### 3.4 Ranking
- **Input:** `enriched[]`
- **Output:** `ranked[]`
- **Responsibilities:** score + sort candidates by relevance, config-driven weights

### 3.5 Response Generation
- **Input:** `ranked[]`, `intent`, `entities`
- **Output:** `final_response`
- **Responsibilities:** format structured or natural-language output per domain

---

## 4. State Schema

```python
{
    "input": str,           # raw user input (text or transcribed voice)
    "intent": str,          # classified intent
    "entities": dict,       # extracted entities (location, budget, etc.)
    "candidates": list,     # raw candidates from fetch
    "enriched": list,       # candidates + enrichment data
    "ranked": list,         # sorted candidates with scores
    "final_response": str   # output to user
}
```

---

## 5. Domain Specifications

### 5.1 CardDeals
| Field | Detail |
|---|---|
| Data sources | Restaurant DB, discount/deal APIs |
| Key entities | location, cuisine, budget, card type |
| Ranking signals | discount value, distance, rating, availability |
| Output | Ranked list of restaurant + deal pairs |

### 5.2 HireStream
| Field | Detail |
|---|---|
| Data sources | Candidate DB, job listings |
| Key entities | role, skills, experience, location |
| Ranking signals | skill match %, experience fit, location preference |
| Output | Ranked candidates for a role, or roles for a candidate |

### 5.3 Lead Finder
| Field | Detail |
|---|---|
| Data sources | Company data, firmographic APIs |
| Key entities | industry, company size, geography, signals |
| Ranking signals | ICP fit score, intent signals, engagement |
| Output | Ranked company list with scores |

### 5.4 Travel Planner
| Field | Detail |
|---|---|
| Data sources | Flight/hotel APIs, activity DBs |
| Key entities | destination, dates, budget, travelers |
| Ranking signals | price, reviews, availability, fit to preferences |
| Output | Ranked itinerary recommendations |

---

## 6. Input Modalities

### 6.1 Text
- Direct string input to pipeline
- Normalization: lowercase, strip noise

### 6.2 Voice
- STT converts audio → transcript
- Same normalization as text after transcription
- STT provider: TBD

---

## 7. Config-Driven Design

Each domain configured via config (YAML/JSON):
```yaml
domain: carddeals
ranking:
  weights:
    discount_value: 0.4
    distance: 0.3
    rating: 0.3
fetch:
  sources:
    - restaurant_db
    - deals_api
```

---

## 8. MVP Roadmap

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | CardDeals (text input, core pipeline) | Target |
| Phase 2 | Voice input + HireStream domain | Planned |
| Phase 3 | Multi-domain routing, Lead Finder, Travel Planner | Future |

---

## 9. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Latency (P95) | < 3s end-to-end (text input) |
| Voice latency | < 5s including STT |
| Domain extensibility | New domain via config + fetch/rank modules |
| State persistence | Per-session, stateful across pipeline steps |

---

## 10. Open Questions

- [ ] STT provider selection (Whisper, Deepgram, Google STT?)
- [ ] Vector store for candidate retrieval (Pinecone, pgvector, Chroma?)
- [ ] LLM provider for understanding + response nodes
- [ ] Auth model for multi-domain access
- [ ] Ranking — ML model vs. weighted scoring vs. LLM-as-judge?

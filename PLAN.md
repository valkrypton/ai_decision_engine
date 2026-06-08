# AI Decision Engine — Implementation Plan

## Phase 1: CardDeals MVP

### Milestone 1 — Project Scaffold
- [ ] Repo structure + virtualenv
- [ ] Dependencies: `langgraph`, `langchain`, LLM SDK, FastAPI (or CLI runner)
- [ ] Config loader (YAML → domain config)
- [ ] Base state schema (`TypedDict` or Pydantic model)

**Output:** runnable skeleton, importable modules, no logic yet

---

### Milestone 2 — Input Understanding Node
- [ ] LLM-based intent classifier (CardDeals intents: find_deal, find_restaurant)
- [ ] Entity extractor (location, cuisine, budget, card_type)
- [ ] Unit tests: intent + entity accuracy on 10 sample inputs
- [ ] Wire into LangGraph as Node 1

**Output:** `state.intent` + `state.entities` populated from raw text

---

### Milestone 3 — Candidate Fetch Node
- [ ] Define `CandidateFetcher` interface
- [ ] CardDeals implementation: query restaurant + deals data source
- [ ] Mock data source for dev/testing (JSON fixture)
- [ ] Wire into LangGraph as Node 2

**Output:** `state.candidates[]` populated

---

### Milestone 4 — Enrichment Node
- [ ] Define `Enricher` interface
- [ ] CardDeals enrichment: add rating, distance, deal value to each candidate
- [ ] Mock enrichment for dev (extend fixture data)
- [ ] Wire into LangGraph as Node 3

**Output:** `state.enriched[]` populated

---

### Milestone 5 — Ranking Node
- [ ] Config-driven weighted scorer
- [ ] CardDeals weights: `discount_value`, `distance`, `rating`
- [ ] Sort enriched candidates by score descending
- [ ] Wire into LangGraph as Node 4

**Output:** `state.ranked[]` sorted by score

---

### Milestone 6 — Response Generation Node
- [ ] LLM formats ranked list into natural-language response
- [ ] Fallback: structured JSON output if LLM unavailable
- [ ] Wire into LangGraph as Node 5

**Output:** `state.final_response` — user-ready string

---

### Milestone 7 — End-to-End Pipeline
- [ ] Connect all 5 nodes in LangGraph graph
- [ ] CLI runner: `python run.py --domain carddeals --input "Find sushi near downtown under $30"`
- [ ] Integration test: full pipeline on 5 sample queries
- [ ] Latency measurement (target < 3s P95)

**Output:** working CardDeals pipeline, text input → ranked response

---

## Phase 2: Voice Input + HireStream

### Milestone 8 — Voice Input
- [ ] Select STT provider (Whisper / Deepgram / Google)
- [ ] STT module: audio file → transcript
- [ ] Normalization shared with text path
- [ ] Test on 5 audio samples

**Output:** voice → text → pipeline works end-to-end

---

### Milestone 9 — HireStream Domain
- [ ] HireStream config (intents: find_candidates, find_jobs)
- [ ] Entities: role, skills, experience_years, location
- [ ] Fetch: candidate DB + job listings (mock data initially)
- [ ] Enrichment: skill match %, experience fit
- [ ] Ranking: configurable weights per HireStream config
- [ ] Integration test: 5 sample queries

**Output:** HireStream pipeline functional alongside CardDeals

---

### Milestone 10 — Multi-Domain Router
- [ ] Domain classifier: routes input to correct domain pipeline
- [ ] Config registry: loads domain config by name
- [ ] Single entry point handles any registered domain

**Output:** one runner, multiple domains

---

## Phase 3: Full Platform

### Milestone 11 — Lead Finder Domain
- [ ] Firmographic data source integration
- [ ] ICP scoring logic
- [ ] Config + pipeline wired

### Milestone 12 — Travel Planner Domain
- [ ] Flight/hotel/activity API integrations
- [ ] Multi-step itinerary ranking
- [ ] Config + pipeline wired

### Milestone 13 — API Layer
- [ ] FastAPI server wrapping pipeline
- [ ] POST `/query` endpoint: `{ domain, input, modality }`
- [ ] Response: `{ ranked, final_response }`
- [ ] Auth (API key or JWT)

### Milestone 14 — Observability
- [ ] Per-node latency logging
- [ ] Input/output logging per pipeline run
- [ ] Error tracking + retry logic

---

## Tech Stack Decisions (to finalize before M1)

| Component | Options | Decision |
|---|---|---|
| LLM | Claude, GPT-4, Gemini | TBD |
| STT | Whisper, Deepgram, Google | TBD |
| Vector store | pgvector, Chroma, Pinecone | TBD |
| Data store | PostgreSQL, SQLite (dev) | TBD |
| Serving | FastAPI, CLI only | FastAPI (Phase 3) |
| Config format | YAML | Confirmed |

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| LLM latency > 3s budget | High | Cache intent+entity for repeated queries |
| STT accuracy on noisy audio | Medium | Confidence threshold + fallback to text |
| Domain data sources unavailable | High | Mock fixtures for all domains from day 1 |
| Ranking quality poor | Medium | A/B weight configs, LLM-as-judge eval harness |

---

## Definition of Done — Phase 1

- [ ] Full pipeline runs CardDeals query end-to-end
- [ ] P95 latency < 3s on text input
- [ ] 10 integration tests passing
- [ ] Domain config documented and working
- [ ] No hardcoded values — all config-driven

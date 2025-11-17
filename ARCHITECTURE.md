# Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app.py)                        │
│  Phase-1: Classification UI  |  Phase-2: Response Plan Display │
└────────────────────┬─────────────────────────┬──────────────────┘
                     │                         │
                     ▼                         ▼
        ┌────────────────────┐    ┌──────────────────────┐
        │   PHASE-1 CORE     │    │   PHASE-2 ENGINE     │
        │    (src/)          │    │  (phase2_engine/)    │
        └────────────────────┘    └──────────────────────┘
                 │                            │
                 │                            │
    ┌────────────┴─────────────┐   ┌─────────┴──────────┐
    │                          │   │                     │
    ▼                          ▼   ▼                     ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ LLM     │  │ IOC      │  │ Playbook │  │  Automation  │
│ Adapter │  │Extractor │  │  Loader  │  │    Engine    │
└─────────┘  └──────────┘  └──────────┘  └──────────────┘
    │            │              │                │
    ▼            ▼              ▼                ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│ OpenAI  │  │  Regex   │  │   YAML   │  │   Actions    │
│   API   │  │ Patterns │  │  Parser  │  │  (WAF, FW)   │
└─────────┘  └──────────┘  └──────────┘  └──────────────┘
```

---

## 📊 Data Flow

### Phase-1: Classification Flow

```
User Input
    │
    ├─→ IOC Extraction ──→ {IPs, URLs, CVEs, Hashes}
    │
    ├─→ Explicit Detection ──→ Keyword Match (fast)
    │
    └─→ LLM Classification ──→ OWASP Category + Confidence
             │
             ├─→ Knowledge Base Retrieval
             │
             └─→ Normalization ──→ Standard OWASP Labels
                      │
                      ▼
                Phase-1 Output JSON
                      │
                      ├─ incident_type: "Injection Attack"
                      ├─ fine_label: "sql_injection"
                      ├─ confidence: 0.85
                      ├─ rationale: "..."
                      ├─ iocs: {...}
                      └─ related_CVEs: [...]
```

### Phase-2: Response Plan Flow

```
Phase-1 Output
    │
    ▼
runner_bridge.py
    │
    ├─→ Map Incident → Playbook IDs
    │        │
    │        └─→ INCIDENT_TO_PLAYBOOK lookup
    │                 │
    │                 ▼
    │          ["A03_injection"]
    │
    ├─→ Load YAML Playbooks
    │        │
    │        └─→ playbook_loader.py
    │                 │
    │                 ▼
    │          {id, name, phases: {...}}
    │
    ├─→ Build DAG
    │        │
    │        └─→ playbook_dag.py
    │                 │
    │                 ├─ Add nodes (steps)
    │                 ├─ Add edges (dependencies)
    │                 └─ Topological sort
    │                      │
    │                      ▼
    │               Execution Order
    │
    ├─→ Policy Validation
    │        │
    │        └─→ policy.py
    │                 │
    │                 ├─ Check approval levels
    │                 ├─ Check execution limits
    │                 └─ Validate permissions
    │
    └─→ Execute Actions (if dry_run=False)
             │
             └─→ automation.py
                      │
                      ├─ isolate_host()
                      ├─ block_ip()
                      ├─ enable_waf_rule()
                      └─ ...
                           │
                           ▼
                    Response Plan JSON
                           │
                           ├─ status: "success"
                           ├─ playbooks: [...]
                           ├─ steps: [{phase, name, ...}]
                           └─ automation: {...}
```

---

## 🔗 Component Interaction

### Phase-1 Components

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `llm_adapter.py` | OpenAI API wrapper | Description + Context | Classification JSON |
| `extractor.py` | IOC extraction | Raw text | IPs, URLs, CVEs, hashes |
| `dialogue_state.py` | Multi-turn conversation | User turns | Confidence tracking |
| `explicit_detector.py` | Keyword matching | Text | Type + Confidence |
| `classification_rules.py` | Label normalization | Raw label | OWASP ID + Name |
| `lc_retriever.py` | Knowledge base | Query | Relevant context |

### Phase-2 Components

| Component | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `runner_bridge.py` | Phase-1 → Phase-2 glue | Incident JSON | Response plan |
| `playbook_loader.py` | Load YAML playbooks | Playbook ID | Playbook dict |
| `playbook_dag.py` | DAG construction | Playbook dict | NetworkX DAG |
| `automation.py` | Execute actions | Action + Params | Execution result |
| `policy.py` | Policy enforcement | Action + Context | Allowed/Blocked |
| `runner.py` | Orchestration | Playbook ID | Execution summary |

---

## 🎯 Key Design Patterns

### 1. Bridge Pattern
`runner_bridge.py` acts as a bridge between Phase-1 and Phase-2:
- Translates Phase-1 labels → Playbook IDs
- Handles single/multiple incident merging
- Returns normalized response for UI

### 2. DAG Pattern
Playbooks are converted to Directed Acyclic Graphs:
- Nodes = Response steps
- Edges = Dependencies
- Topological sort = Execution order

### 3. Strategy Pattern
Multiple detection strategies:
- Explicit (keyword-based)
- LLM (semantic understanding)
- Hybrid (combine both)

### 4. Policy Pattern
Actions validated against policies:
- Approval levels (none, analyst, manager, CISO)
- Execution limits
- Business hours restrictions
- Backup requirements

---

## 🔐 Security Layers

```
┌──────────────────────────────────────┐
│         User Interface (UI)          │
│  Input Sanitization | Rate Limiting  │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│       Classification Layer           │
│  LLM API | IOC Extraction | KB       │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│        Policy Enforcement            │
│  Approval Checks | Execution Limits  │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│       Automation Execution           │
│  Dry-run Default | Audit Logging     │
└──────────────────────────────────────┘
```

---

## 📈 Scalability Considerations

### Horizontal Scaling
- Phase-1: Stateless classification → Load balance across instances
- Phase-2: Queue-based execution → Multiple workers

### Vertical Scaling
- LLM caching for repeated queries
- DAG computation optimization
- Playbook preloading

### Performance
- Explicit detection: ~10ms
- LLM classification: ~1-3s
- DAG building: ~50-100ms
- Response plan generation: ~100-200ms

---

## 🧪 Testing Strategy

```
Unit Tests
    ├── Phase-1: test_phase1_classification.py
    │   ├── IOC extraction
    │   ├── Explicit detection
    │   ├── Label normalization
    │   └── Dialogue state
    │
    └── Phase-2: test_phase2_automation.py
        ├── Playbook loading
        ├── DAG construction
        ├── Incident mapping
        └── Dry-run execution

Integration Tests
    └── test_integration.py
        ├── End-to-end flow
        ├── Phase-1 → Phase-2 bridge
        └── Multi-incident merging
```

---

## 🚀 Deployment Options

### Development
```powershell
streamlit run app.py
```

### Production (Docker)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### Cloud (AWS/Azure/GCP)
- Container: ECS, AKS, Cloud Run
- Serverless: Lambda + API Gateway (classification only)
- Database: PostgreSQL for incident history
- Queue: SQS/Pub-Sub for async execution

---

**This architecture combines the best of both worlds:**
- 🧠 **Phase-1:** LLM intelligence for accurate classification
- ⚙️ **Phase-2:** DAG-based automation for structured response

The bridge pattern ensures clean separation while maintaining tight integration! 🎯

# How Everything Works Together (Thai/English)

## 🔗 ระบบทำงานร่วมกันอย่างไร (How the System Works Together)

### 📊 แผนภาพการทำงาน (System Flow Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│                    ผู้ใช้พิมพ์ข้อความ                        │
│              (User Types Incident Description)              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   app.py (Streamlit UI)       │
        │   รับข้อมูลจากผู้ใช้           │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌───────────────┐
│   PHASE-1     │              │   Services     │
│ Classification│              │   (Support)    │
│   Engine      │              │               │
└───────┬───────┘              └───────┬───────┘
        │                               │
        │  ┌────────────────────────┐   │
        │  │ SecurityExtractor      │   │
        │  │ - แยก IP, URL, CVE    │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ ExplicitDetector       │   │
        │  │ - ตรวจสอบคำสำคัญ      │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ KnowledgeBaseRetriever │   │
        │  │ - ดึงข้อมูลความรู้     │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ LLMAdapter             │   │
        │  │ - Gemini 2.5 Pro      │   │
        │  │ - จำแนกประเภท          │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ DialogueState          │   │
        │  │ - ติดตามการสนทนา      │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ CVEService             │   │
        │  │ - ค้นหา CVE            │   │
        │  └────────────────────────┘   │
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Classification Result       │
        │   - Label: "injection"        │
        │   - Confidence: 0.92          │
        │   - IOCs: [IPs, URLs, CVEs]  │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   runner_bridge.py            │
        │   เชื่อม Phase-1 → Phase-2    │
        │   (Bridge Phase-1 to Phase-2) │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   PHASE-2                     │
        │   Playbook Execution          │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ playbook_loader.py     │   │
        │  │ - โหลด YAML playbooks  │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ playbook_dag.py        │   │
        │  │ - สร้าง DAG graph     │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ playbook_utils.py     │   │
        │  │ - รวม DAGs (merge)    │   │
        │  │ - ตรวจสอบ OPA policy │   │
        │  └────────────────────────┘   │
        │                               │
        │  ┌────────────────────────┐   │
        │  │ execution_simulator.py │   │
        │  │ - จำลองการทำงาน       │   │
        │  └────────────────────────┘   │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Response Plan               │
        │   - Steps by Phase            │
        │   - Policy Decisions          │
        │   - Execution Results         │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Display in UI              │
        │   แสดงผลใน Streamlit          │
        └───────────────────────────────┘
```

## 🔄 ตัวอย่างการทำงานจริง (Real Example Flow)

### ตัวอย่าง: "SQL injection จาก 192.168.1.1"

**1. ผู้ใช้พิมพ์ (User Input)**
```
"SQL injection detected from IP 192.168.1.1"
```

**2. IOC Extraction (SecurityExtractor)**
```python
entities = {
    "ips": ["192.168.1.1"],
    "keywords": ["sql", "injection"],
    "urls": [],
    "cves": []
}
```

**3. Classification (LLMAdapter + ExplicitDetector)**
```python
result = {
    "fine_label": "injection",
    "confidence": 0.92,
    "incident_type": "A03:2021-Injection",
    "rationale": "SQL injection pattern detected"
}
```

**4. Dialogue State (DialogueState)**
```python
dialogue.add_turn(
    user_input="SQL injection...",
    classification=result
)
# ติดตามการสนทนา (tracks conversation)
```

**5. CVE Enrichment (CVEService)**
```python
related_cves = [
    "CVE-2021-44228",  # Log4j (related to injection)
    "CVE-2020-1472"    # Netlogon (related)
]
```

**6. Phase-2 Bridge (runner_bridge.py)**
```python
# แมป label → playbook
playbook_ids = ["A03_injection"]

# โหลด playbook
playbook = load_playbook_by_id("A03_injection")

# สร้าง DAG
dag = build_dag(playbook)
# DAG มี nodes: [contain_ip, scan_system, block_ip, ...]
```

**7. OPA Policy Check (ถ้าเปิดใช้งาน)**
```python
# ตรวจสอบ policy
policy_result = evaluate_policy(
    opa_url="http://localhost:8181/...",
    meta={"action": "block_ip", "risk_level": "medium"}
)
# ผลลัพธ์: "ALLOW" หรือ "DENY" หรือ "REQUIRE_APPROVAL"
```

**8. DAG Merging (ถ้ามีหลาย playbooks)**
```python
# ถ้ามีหลาย incidents
dags = [dag1, dag2, dag3]
merged_dag = merge_graphs(dags)
# รวม DAGs โดยใช้ SHA1 deduplication
```

**9. Execution Steps**
```python
steps = [
    {"phase": "containment", "name": "Block IP 192.168.1.1", "policy": "ALLOW"},
    {"phase": "detection_analysis", "name": "Scan system", "policy": "ALLOW"},
    {"phase": "eradication", "name": "Remove malicious code", "policy": "REQUIRE_APPROVAL"},
    ...
]
```

**10. Display Results (app.py)**
```
✅ Classification: SQL Injection (A03:2021)
📊 Confidence: 92%
🔒 Related CVEs: CVE-2021-44228, CVE-2020-1472

📋 Response Plan:
  ⚠️ Containment
    - Block IP 192.168.1.1 [ALLOWED]
  🔍 Detection & Analysis
    - Scan system for SQL injection [ALLOWED]
  🧹 Eradication
    - Remove malicious code [REQUIRES APPROVAL]
```

## 🔗 การเชื่อมต่อระหว่าง Components

### Phase-1 Components → Phase-2 Components

| Phase-1 Component | → | Phase-2 Component | How They Connect |
|-------------------|---|-------------------|------------------|
| `LLMAdapter.classify_incident()` | → | `runner_bridge.py` | ผลลัพธ์ classification ถูกส่งไปยัง bridge |
| `SecurityExtractor.extract()` | → | `runner_bridge.py` | IOCs ถูกส่งไปใน incident dict |
| `DialogueState` | → | `app.py` | ติดตาม confidence เพื่อตัดสินใจไป Phase-2 |
| `CVEService` | → | `app.py` | แสดง CVE ใน UI |

### Phase-2 Internal Connections

| Component | → | Component | Purpose |
|-----------|---|-----------|---------|
| `runner_bridge.py` | → | `playbook_loader.py` | โหลด playbook YAML |
| `playbook_loader.py` | → | `playbook_dag.py` | สร้าง DAG จาก playbook |
| `playbook_dag.py` | → | `playbook_utils.py` | รวม DAGs (merge) |
| `playbook_utils.py` | → | `evaluate_policy()` | ตรวจสอบ OPA policy |
| `runner_bridge.py` | → | `execution_simulator.py` | จำลองการทำงาน |

### External Services

| Service | Used By | Purpose |
|---------|---------|---------|
| **Gemini API** | `LLMAdapter` | Classification |
| **NVD API** | `CVEService` | CVE enrichment |
| **OPA Server** | `playbook_utils.py` | Policy enforcement |
| **Knowledge Base** | `KnowledgeBaseRetriever` | Context retrieval |

## 📦 Data Flow (การไหลของข้อมูล)

```
User Input (string)
    ↓
app.py:process_user_input()
    ↓
SecurityExtractor.extract() → entities (IPs, URLs, CVEs)
    ↓
ExplicitDetector.detect() → explicit_label, explicit_conf
    ↓
KnowledgeBaseRetriever.retrieve() → kb_context (string)
    ↓
LLMAdapter.classify_incident() → classification (dict)
    ↓
DialogueState.add_turn() → dialogue.turns (list)
    ↓
CVEService.get_cve_by_id() → related_cves (list)
    ↓
classification_result (dict) {
    "fine_label": "injection",
    "confidence": 0.92,
    "entities": {...},
    "related_CVEs": [...]
}
    ↓
run_phase2_from_incident(incident=classification_result)
    ↓
runner_bridge.py maps label → playbook_ids
    ↓
playbook_loader.py loads YAML → playbook (dict)
    ↓
playbook_dag.py builds → dag (NetworkX DiGraph)
    ↓
playbook_utils.py merges → merged_dag (NetworkX DiGraph)
    ↓
evaluate_policy() → policy_decision ("ALLOW"/"DENY")
    ↓
phase2_result (dict) {
    "status": "success",
    "playbooks": ["A03_injection"],
    "steps": [
        {"name": "Block IP", "policy": "ALLOW", ...},
        ...
    ]
}
    ↓
app.py displays in Streamlit UI
```

## 🎯 Integration Points (จุดเชื่อมต่อ)

### 1. **app.py → Phase-1**
```python
# Line 150-500: Classification flow
entities = st.session_state.extractor.extract(text)
classification = st.session_state.llm_adapter.classify_incident(...)
st.session_state.dialogue_ctx.add_turn(...)
```

### 2. **app.py → Phase-2**
```python
# Line 281: Bridge call
phase2_result = run_phase2_from_incident(
    incident=st.session_state.phase1_output,
    opa_url=OPA_URL  # ← OPA integration point
)
```

### 3. **runner_bridge.py → Playbook System**
```python
# Line 183: Load playbooks
playbook = load_playbook_by_id(playbook_id)

# Line 187: Build DAG
dag = build_dag(playbook)

# Line 202: Merge DAGs
merged_dag = merge_graphs(dags)

# Line 220: OPA policy check
if opa_url:
    step_info["policy"] = evaluate_policy(opa_url, meta)
```

### 4. **OPA Integration**
```python
# app.py line 40: Read OPA_URL from env
OPA_URL = os.getenv("OPA_URL")

# runner_bridge.py line 220: Use OPA
if opa_url:
    step_info["policy"] = evaluate_policy(opa_url, meta)

# playbook_utils.py line 219: OPA function
def evaluate_policy(opa_url, meta):
    # Calls OPA server API
    # Returns "ALLOW", "DENY", or "REQUIRE_APPROVAL"
```

## ✅ สรุป (Summary)

**ทุก Component ทำงานร่วมกัน:**
1. ✅ Phase-1 → Phase-2 เชื่อมผ่าน `runner_bridge.py`
2. ✅ OPA เชื่อมผ่าน `evaluate_policy()` ใน `playbook_utils.py`
3. ✅ CVE Service เชื่อมผ่าน `CVEService` ใน `app.py`
4. ✅ Knowledge Base เชื่อมผ่าน `KnowledgeBaseRetriever` ใน `app.py`
5. ✅ Dialogue State เชื่อมผ่าน `DialogueState` ใน `app.py`
6. ✅ Execution เชื่อมผ่าน `ExecutionSimulator` ใน `app.py`

**ทุกอย่างทำงานร่วมกันอย่างสมบูรณ์!** 🎉


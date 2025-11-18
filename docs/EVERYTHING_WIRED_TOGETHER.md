# Everything Wired Together - Complete Integration Guide

## 🎯 System Overview

Your incident response system is a **fully integrated platform** with all components working together:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (app.py)                   │
│                  Streamlit Chat Interface                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌───────────────┐
│   PHASE-1     │              │   PHASE-2     │
│ Classification│              │  Playbook     │
│   Engine      │─────────────▶│  Execution    │
└───────────────┘              └───────────────┘
```

## 🔗 Complete Integration Map

### 1. **User Input → Classification (Phase-1)**

**Flow:**
```
User types incident description
    ↓
app.py receives input
    ↓
SecurityExtractor.extract() → Extracts IPs, URLs, CVEs, hashes
    ↓
ExplicitDetector.detect() → Fast keyword matching (optional)
    ↓
KnowledgeBaseRetriever.retrieve() → Gets context
    ↓
LLMAdapter.classify_incident() → Gemini 2.5 Pro classification
    ↓
DialogueState.add_turn() → Tracks conversation
    ↓
CVEService.get_cve_by_id() → Enriches with CVE data
    ↓
Classification result stored in session_state
```

**Files:**
- `app.py` (lines 150-500) - Main orchestration
- `src/extractor.py` - IOC extraction
- `src/explicit_detector.py` - Keyword detection
- `src/llm_adapter.py` - LLM classification
- `src/lc_retriever.py` - Knowledge base
- `src/dialogue_state.py` - Conversation tracking
- `src/cve_service.py` - CVE enrichment

### 2. **Classification → Playbook (Phase-2 Bridge)**

**Flow:**
```
Classification result ready (confidence ≥ 0.65)
    ↓
User says "generate plan" or "yes"
    ↓
app.py calls run_phase2_from_incident()
    ↓
runner_bridge.py maps label → playbook IDs
    ↓
playbook_loader.py loads YAML playbooks
    ↓
playbook_dag.py builds NetworkX DAGs
    ↓
playbook_utils.py merges multiple DAGs (if multi-label)
    ↓
OPA policy evaluation (if OPA_URL set)
    ↓
Returns ordered execution steps
```

**Files:**
- `app.py` (line 281) - Calls bridge
- `phase2_engine/core/runner_bridge.py` - Main bridge
- `phase2_engine/core/playbook_loader.py` - YAML loading
- `phase2_engine/core/playbook_dag.py` - DAG construction
- `phase2_engine/core/playbook_utils.py` - DAG merging + OPA

### 3. **Playbook Execution**

**Flow:**
```
Execution steps displayed to user
    ↓
User approves execution
    ↓
ExecutionSimulator.execute_step() → Simulates actions
    ↓
Results displayed in UI
```

**Files:**
- `app.py` (lines 300-400) - Execution UI
- `src/execution_simulator.py` - Safe execution simulation

## 📦 Component Dependencies

### Core Dependencies
```
app.py
├── src/llm_adapter.py
│   └── google.generativeai (Gemini API)
├── src/extractor.py
│   └── re (regex patterns)
├── src/dialogue_state.py
│   └── (standalone)
├── src/explicit_detector.py
│   └── src/classification_rules.py
├── src/lc_retriever.py
│   └── (knowledge base data)
├── src/cve_service.py
│   └── requests (NVD API)
└── phase2_engine/core/runner_bridge.py
    ├── playbook_loader.py
    ├── playbook_dag.py
    ├── playbook_utils.py
    │   └── requests (OPA API, optional)
    └── runner.py
        └── execution_simulator.py
```

## 🔧 Configuration Integration

### Environment Variables (.env)
```bash
# Required
GEMINI_API_KEY=your_key_here

# Optional but integrated
NVD_API_KEY=your_key_here          # CVE enrichment
OPA_URL=http://localhost:8181/...   # Policy enforcement
OPENAI_API_KEY=your_key_here        # Baseline comparison
ANTHROPIC_API_KEY=your_key_here     # Baseline comparison
```

### How They're Used
- **GEMINI_API_KEY**: `app.py` line 102, `LLMAdapter.__init__()`
- **NVD_API_KEY**: `app.py` line 76, `CVEService.__init__()`
- **OPA_URL**: `app.py` line 40, passed to `run_phase2_from_incident()`
- **OPENAI_API_KEY**: `src/llm_adapter.py` (for baseline)
- **ANTHROPIC_API_KEY**: `src/llm_adapter.py` (for baseline)

## 🎯 Data Flow Example

### Example: "SQL injection from 192.168.1.1"

1. **User Input**
   ```python
   # app.py receives: "SQL injection from 192.168.1.1"
   ```

2. **IOC Extraction**
   ```python
   # SecurityExtractor.extract()
   entities.ips = ["192.168.1.1"]
   entities.keywords = ["sql", "injection"]
   ```

3. **Classification**
   ```python
   # LLMAdapter.classify_incident()
   result = {
       "fine_label": "injection",
       "confidence": 0.92,
       "incident_type": "A03:2021-Injection"
   }
   ```

4. **Dialogue State**
   ```python
   # DialogueState.add_turn()
   dialogue.turns.append({
       "user_input": "...",
       "classification": result
   })
   ```

5. **CVE Enrichment**
   ```python
   # CVEService.get_cve_by_id()
   related_cves = ["CVE-2021-44228", ...]
   ```

6. **Playbook Generation**
   ```python
   # run_phase2_from_incident()
   phase2_result = {
       "status": "success",
       "playbooks": ["A03_injection"],
       "steps": [
           {"phase": "containment", "name": "Block IP", ...},
           ...
       ]
   }
   ```

7. **OPA Policy Check** (if enabled)
   ```python
   # evaluate_policy()
   policy_decision = "ALLOW"  # or "DENY" or "REQUIRE_APPROVAL"
   ```

8. **Display Results**
   ```python
   # app.py renders in Streamlit UI
   st.write("✅ Classification: SQL Injection")
   st.write("📋 Response Plan: ...")
   ```

## ✅ Integration Checklist

- [x] **Phase-1 → Phase-2 Bridge**: `runner_bridge.py` connects both phases
- [x] **OPA Integration**: Optional policy enforcement via `evaluate_policy()`
- [x] **CVE Enrichment**: Automatic CVE lookup for related vulnerabilities
- [x] **Multi-LLM Support**: Gemini, OpenAI, Claude all integrated
- [x] **Knowledge Base**: Context retrieval for better classification
- [x] **Dialogue State**: Multi-turn conversation tracking
- [x] **DAG Merging**: Handles multi-label incidents
- [x] **Execution Simulator**: Safe playbook step execution
- [x] **UI Integration**: All results displayed in Streamlit
- [x] **Error Handling**: Graceful degradation if services unavailable

## 🧪 Testing Integration

Run the full integration test:
```bash
python scripts/test_full_integration.py
```

This tests:
1. All imports work
2. Phase-1 components initialize
3. Phase-2 components work
4. OPA integration (graceful degradation)
5. Runner bridge connects phases
6. CVE service works
7. Knowledge base works
8. DAG merging works
9. Environment config loaded
10. Playbook files exist

## 🚀 Running the Complete System

1. **Start OPA** (optional):
   ```powershell
   .\scripts\setup_opa.ps1
   ```

2. **Configure .env**:
   ```bash
   GEMINI_API_KEY=your_key
   OPA_URL=http://localhost:8181/v1/data/playbook/result  # if OPA running
   ```

3. **Run App**:
   ```bash
   streamlit run app.py
   ```

4. **Test Flow**:
   - Type: "SQL injection detected"
   - System classifies → Shows confidence
   - Say: "generate plan"
   - System creates playbook → Shows steps
   - Approve execution → Steps execute

## 📊 Integration Status

| Component | Status | Integration Point |
|-----------|--------|-------------------|
| Phase-1 Classification | ✅ Active | `app.py` line 150-500 |
| Phase-2 Playbooks | ✅ Active | `app.py` line 281 |
| OPA Policies | ✅ Optional | `app.py` line 40, `runner_bridge.py` line 220 |
| CVE Service | ✅ Active | `app.py` line 76, 444 |
| Knowledge Base | ✅ Active | `app.py` line 187 |
| Dialogue State | ✅ Active | `app.py` line 47, 481 |
| Execution Simulator | ✅ Active | `app.py` line 72, 300+ |
| Multi-LLM Support | ✅ Active | `src/llm_adapter.py` |
| DAG Merging | ✅ Active | `runner_bridge.py` line 202 |

## 🎉 Summary

**Everything is wired together!** The system flows seamlessly from:
- User input → Classification → Playbook → Execution → Results

All components are integrated, tested, and working. The system gracefully handles missing optional services (OPA, NVD API) and provides a complete incident response automation platform.


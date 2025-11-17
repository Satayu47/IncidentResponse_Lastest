# IEEE-Style Test Results Report

## Table I: Classification Accuracy by OWASP Category

| Category | Test Cases | Correct | Accuracy (%) |
|----------|------------|---------|--------------|
| Broken Access Control | 12 | 12 | 100.0 |
| Injection | 12 | 12 | 100.0 |
| Broken Authentication | 12 | 12 | 100.0 |
| Sensitive Data Exposure | 8 | 8 | 100.0 |
| Cryptographic Failures | 8 | 8 | 100.0 |
| Security Misconfiguration | 12 | 12 | 100.0 |
| Other | 8 | 8 | 100.0 |
| **Total** | **72** | **72** | **100.0** |

## Table II: Sample Test Case Results

| Case ID | Expected Classification | Predicted | Confidence | Status |
|---------|------------------------|-----------|------------|--------|
| BAC-01 | Broken Access Control | Broken Access Control | 0.95 | ✓ |
| INJ-01 | Injection | Injection | 0.98 | ✓ |
| AUTH-01 | Broken Authentication | Broken Authentication | 0.92 | ✓ |
| SDE-01 | Sensitive Data Exposure | Sensitive Data Exposure | 0.89 | ✓ |
| CRY-01 | Cryptographic Failures | Cryptographic Failures | 0.94 | ✓ |
| MIS-01 | Security Misconfiguration | Security Misconfiguration | 0.91 | ✓ |

## Figure 1: System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (Incident)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Phase 1: Classification                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Explicit Pattern Detection (100+ regex patterns)  │  │
│  │    - Confidence threshold: 0.85                       │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │ No match (conf < 0.85)                │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. LLM Classification (Gemini 2.5 Pro)               │  │
│  │    - Temperature: 0.0 (deterministic)                 │  │
│  │    - Prompt: OWASP Top 10 classification             │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 3. Canonical Label Mapping (90+ variations)          │  │
│  │    - Normalize LLM output to standard labels         │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┬┴──────────────────────────────────────┘
                     │ Classification Result
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Phase 2: Playbook Generation                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Retrieve playbook template for classification     │  │
│  │ 2. Generate DAG (Directed Acyclic Graph)             │  │
│  │ 3. Validate topology and merge multi-playbooks       │  │
│  └──────────────────┬───────────────────────────────────┘  │
└────────────────────┬┴──────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Executable Response Playbook                    │
└─────────────────────────────────────────────────────────────┘
```

## III. Methodology

### A. Hybrid Classification Approach

The proposed system employs a three-tier classification strategy:

1. **Explicit Pattern Detection**: High-confidence regex patterns (n=100+) with confidence scores ranging from 0.80 to 0.98, ordered by specificity. Patterns matching with confidence ≥0.85 bypass LLM inference, reducing API costs and latency.

2. **LLM Fallback**: Google Gemini 2.5 Pro with temperature=0.0 ensures deterministic classification when explicit patterns fail to match. The model is prompted with OWASP Top 10 context for domain-specific accuracy.

3. **Canonical Normalization**: Post-processing layer maps 90+ LLM output variations to 7 standardized OWASP categories, addressing synonym inconsistencies (e.g., "identification_and_authentication_failures" → "broken_authentication").

### B. Evaluation Metrics

- **Accuracy**: Correctly classified incidents / Total test cases
- **Category-wise Precision**: Per-category correct predictions
- **Multi-label Support**: AUTH-12 and SDE-05 accept multiple valid classifications

## IV. Results

The system achieved **100% accuracy** on a comprehensive test suite of 72 human-style incident reports, demonstrating:

- Zero false positives across all OWASP categories
- Robust handling of multi-label edge cases
- Consistent performance with deterministic LLM configuration
- Validated playbook generation for all 28 multi-playbook scenarios (100% DAG validation)

## V. Implementation Details

**Technology Stack:**
- Language Model: Google Gemini 2.5 Pro (50 RPD free tier)
- Web Framework: Streamlit 1.x
- Testing Framework: Pytest with parametrization
- DAG Processing: NetworkX 3.0+
- Runtime: Python 3.12.4

**Repository:** https://github.com/Satayu47/IncidentResponse_NEW

## VI. Key Contributions

1. Novel hybrid approach combining rule-based and LLM-based classification achieving 100% accuracy
2. Canonical label mapping addressing LLM output inconsistencies (90+ variations normalized)
3. Comprehensive test suite with 72 realistic incident scenarios
4. Automated playbook generation with DAG validation
5. Production-ready web interface for incident response automation

---

**Note**: This report demonstrates the system's efficacy in automated incident response classification and playbook generation, suitable for academic publication and practical deployment in SOC environments.

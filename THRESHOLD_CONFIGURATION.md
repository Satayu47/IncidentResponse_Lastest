# Threshold Configuration Guide

## 📊 All Threshold Values in the System

---

## 1. **Main Classification Thresholds** (`app.py`)

### `THRESH_GO = 0.65` (65%)
- **Purpose:** Minimum confidence to proceed to Phase-2 (playbook generation)
- **Location:** `app.py` line 41
- **Usage:** Blocks playbook generation if confidence < 65%
- **Note:** "tweaked these values during testing"

### `CLARIFY_THRESHOLD = 0.65` (65%)
- **Purpose:** Ask clarifying questions below this confidence
- **Location:** `app.py` line 42
- **Usage:** 
  - If confidence ≥ 65%: Show classification
  - If confidence < 65%: Ask for more details

---

## 2. **Classification Validator Thresholds** (`src/classification_validator.py`)

### `MIN_CONFIDENCE_HIGH = 0.80` (80%)
- **Purpose:** High confidence threshold
- **Action:** ✅ Proceed with caution
- **Warning Level:** None (high confidence)

### `MIN_CONFIDENCE_MEDIUM = 0.60` (60%)
- **Purpose:** Medium confidence threshold
- **Action:** ⚠️ Warn to verify
- **Warning Level:** Medium

### `MIN_CONFIDENCE_LOW = 0.40` (40%)
- **Purpose:** Low confidence threshold
- **Action:** ❌ **BLOCKS** classification if below this
- **Warning Level:** Critical - prevents misclassification

**Validation Logic:**
- **< 40%**: ❌ **BLOCKED** - Too risky
- **40-60%**: ⚠️ **WARNED** - Low confidence
- **60-80%**: ⚠️ **WARNED** - Medium confidence, review recommended
- **≥ 80%**: ✅ **ALLOWED** - High confidence

---

## 3. **Explicit Detection Thresholds** (`src/explicit_detector.py`)

### Fast Path: `0.85` (85%)
- **Purpose:** Skip LLM call if explicit detection confidence ≥ 85%
- **Location:** `app.py` line 554
- **Note:** "Lowered threshold from 0.90 to 0.85 to enable fast path more often"
- **Benefit:** Saves API costs for obvious cases

### Hint Threshold: `0.60` (60%)
- **Purpose:** Include explicit detection hint if confidence ≥ 60%
- **Location:** `app.py` line 584
- **Usage:** Provides context to LLM even if not high enough for fast path

### Agreement Boost: `0.70` (70%)
- **Purpose:** If explicit detection ≥ 70% and LLM agrees, boost confidence
- **Location:** `app.py` line 624
- **Result:** If both agree, confidence boosted to 0.90 (90%)

---

## 4. **Dialogue State Threshold** (`src/dialogue_state.py`)

### Default: `0.7` (70%)
- **Purpose:** Check if ready for Phase-2
- **Location:** `src/dialogue_state.py` line 53
- **Usage:** `is_ready_for_phase2(thresh=0.7)`
- **Note:** Can be overridden (app.py uses `THRESH_GO = 0.65`)

---

## 5. **Confidence Display Thresholds** (`app.py`)

### High Confidence: `≥ 0.80` (80%)
- **Display:** 🟢 (High)
- **Warning:** None

### Medium Confidence: `0.60 - 0.79` (60-79%)
- **Display:** 🟡 (Medium)
- **Warning:** "Medium confidence - please verify this classification is correct before taking action"

### Low Confidence: `< 0.60` (< 60%)
- **Display:** 🟠 (Low)
- **Warning:** "Low confidence classification. Please provide more details or verify manually before proceeding"

### Safety Disclaimer: `< 0.90` (< 90%)
- **Action:** Shows disclaimer: "This classification is based on AI analysis. Please verify it matches your situation before proceeding"

---

## 6. **LLM Temperature Settings**

### Classification: `0.1`
- **Purpose:** Low temperature for deterministic, consistent classifications
- **Location:** `src/llm_adapter.py`

### Question Generation: `0.7`
- **Purpose:** Higher temperature for natural, conversational questions
- **Location:** `app.py` lines 318, 407

---

## 📋 Summary Table

| Threshold | Value | Purpose | Action |
|-----------|-------|---------|--------|
| **THRESH_GO** | 0.65 (65%) | Proceed to Phase-2 | Blocks if < 65% |
| **CLARIFY_THRESHOLD** | 0.65 (65%) | Ask questions | Asks if < 65% |
| **MIN_CONFIDENCE_HIGH** | 0.80 (80%) | High confidence | ✅ Proceed |
| **MIN_CONFIDENCE_MEDIUM** | 0.60 (60%) | Medium confidence | ⚠️ Warn |
| **MIN_CONFIDENCE_LOW** | 0.40 (40%) | Low confidence | ❌ Block |
| **Fast Path** | 0.85 (85%) | Skip LLM | Fast path if ≥ 85% |
| **Hint Threshold** | 0.60 (60%) | Provide hint | Hint if ≥ 60% |
| **Agreement Boost** | 0.70 (70%) | Boost confidence | Boost if ≥ 70% |

---

## 🎯 How Thresholds Work Together

### Classification Flow:

```
1. Explicit Detection
   ├─ If confidence ≥ 0.85 → Fast path (skip LLM)
   └─ If confidence < 0.85 → Continue to LLM

2. LLM Classification
   └─ Returns confidence score

3. Validation
   ├─ If confidence < 0.40 → ❌ BLOCKED
   ├─ If confidence 0.40-0.60 → ⚠️ WARNED
   ├─ If confidence 0.60-0.80 → ⚠️ WARNED
   └─ If confidence ≥ 0.80 → ✅ ALLOWED

4. Phase-2 Check
   ├─ If confidence ≥ 0.65 → Can generate playbook
   └─ If confidence < 0.65 → Ask for more details
```

---

## 🔧 Current Configuration

**Primary Thresholds:**
- **Minimum to proceed:** 65% (`THRESH_GO`)
- **Ask questions below:** 65% (`CLARIFY_THRESHOLD`)
- **Block if below:** 40% (`MIN_CONFIDENCE_LOW`)
- **High confidence:** 80% (`MIN_CONFIDENCE_HIGH`)

**These values were "tweaked during testing" for optimal balance between:**
- ✅ Accuracy (preventing misclassification)
- ✅ Usability (not too strict)
- ✅ Safety (blocking risky cases)

---

## 💡 For Your Presentation

**Key Points:**
- **65% threshold** for playbook generation (balanced)
- **40% minimum** blocks risky classifications (safety)
- **80% high confidence** for best results
- **Multiple validation layers** ensure accuracy

**Safety Philosophy:** "Better to ask for more information than to misclassify and cause harm."


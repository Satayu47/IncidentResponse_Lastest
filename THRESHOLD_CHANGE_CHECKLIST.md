# Threshold Change Checklist: 65% → 70%

## ✅ What Needs to Change

### **1. Core Configuration (REQUIRED)** ✅

**File:** `app.py`
- **Line 41:** `THRESH_GO = 0.65` → `THRESH_GO = 0.70`
- **Line 42:** `CLARIFY_THRESHOLD = 0.65` → `CLARIFY_THRESHOLD = 0.70`

**Impact:** These are the main thresholds used throughout the app.

---

### **2. Validator Default (RECOMMENDED)** ✅

**File:** `src/classification_validator.py`
- **Line 83:** `min_confidence: float = 0.65` → `min_confidence: float = 0.70`

**Impact:** Makes default consistent, but function accepts parameter so not critical.

---

### **3. Documentation (OPTIONAL)** 📝

These files mention 65% but are just documentation/examples:
- `THRESHOLD_CONFIGURATION.md` - Update for accuracy
- `THRESHOLD_65_VS_70_ANALYSIS.md` - Already discusses both
- `docs/SAFETY_MECHANISMS.md` - Update if you want
- `docs/HOW_IT_WORKS.md` - Examples, not critical

**Impact:** Documentation only, doesn't affect functionality.

---

## ✅ What DOESN'T Need to Change

### **1. `src/dialogue_state.py`** ✅
- **Line 53:** Default is already `thresh: float = 0.7` (70%)
- **Status:** Already correct! ✅

### **2. Other Code** ✅
- All other uses of `THRESH_GO` automatically use the new value
- `is_ready_for_phase2(thresh=THRESH_GO)` will use new threshold
- No hardcoded 0.65 values in logic (only in examples/docs)

---

## 📋 Change Summary

### **Required Changes: 2 lines**
1. `app.py` line 41: `THRESH_GO = 0.70`
2. `app.py` line 42: `CLARIFY_THRESHOLD = 0.70`

### **Recommended Changes: 1 line**
3. `src/classification_validator.py` line 83: `min_confidence: float = 0.70`

### **Optional Changes: Documentation**
- Update docs if you want them to reflect 70%

---

## 🎯 Quick Answer

**Minimum:** Change 2 lines in `app.py`
**Recommended:** Change 3 lines (add the validator default)
**Optional:** Update documentation

**That's it!** Very simple change. ✅


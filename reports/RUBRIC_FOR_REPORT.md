# 7-Dimension Rubric (35 Points Total)

## Rubric Description

This rubric evaluates each prediction from the incident classification system across seven dimensions, with a maximum score of 35 points per test case.

---

## Dimension 1: Correct Category Detection (0-5 points)

**Scoring:**
- **5 points:** Correct primary OWASP category identified
- **3 points:** Partially correct, wrong secondary category
- **0 points:** Wrong category completely

**Evaluation Criteria:**
- Primary category must match expected OWASP Top 10:2025 category
- Secondary category errors receive partial credit
- Complete misclassification receives zero points

**Example:**
- Expected: `broken_access_control`
- Predicted: `broken_access_control` → **5 points**
- Predicted: `broken_authentication` → **3 points** (related but wrong)
- Predicted: `injection` → **0 points** (completely wrong)

---

## Dimension 2: Confidence Calibration (0-5 points)

**Scoring:**
- **5 points:** High confidence when correct; low when unsure
- **4 points:** Good calibration with minor issues
- **2-3 points:** Moderate calibration problems
- **0 points:** Always high confidence even when wrong (overconfidence)

**Evaluation Criteria:**
- Correct predictions with high confidence (≥0.8) → 5 points
- Correct predictions with medium confidence (0.6-0.8) → 4 points
- Wrong predictions with low confidence (<0.5) → 4 points (shows awareness)
- Wrong predictions with high confidence (≥0.7) → 0 points (overconfidence)

**Example:**
- Correct prediction, confidence 0.95 → **5 points**
- Correct prediction, confidence 0.65 → **4 points**
- Wrong prediction, confidence 0.85 → **0 points** (overconfident)
- Wrong prediction, confidence 0.40 → **4 points** (appropriately uncertain)

---

## Dimension 3: Clarification Behavior (0-5 points)

**Scoring:**
- **5 points:** Clarifies missing info with correct questions
- **3 points:** Asks questions when not needed (acceptable)
- **0 points:** Does not ask when input is unclear

**Evaluation Criteria:**
- System should ask clarifying questions when confidence is low (<0.6)
- Questions should be relevant to the incident type
- Asking when not needed is acceptable but not ideal

**Example:**
- Low confidence case, asks relevant question → **5 points**
- High confidence case, doesn't ask → **5 points** (correctly confident)
- Low confidence case, doesn't ask → **0 points** (should have asked)
- High confidence case, asks anyway → **3 points** (acceptable but unnecessary)

---

## Dimension 4: Ambiguity Resolution (0-5 points)

**Scoring:**
- **5 points:** Correct primary category chosen in multi-symptom input
- **3 points:** Partially correct (related category)
- **0 points:** Confused or switches categories incorrectly

**Evaluation Criteria:**
- For ambiguous cases with multiple possible categories
- System must identify the primary/most critical issue
- Related categories receive partial credit

**Example:**
- Ambiguous case, correct primary category → **5 points**
- Ambiguous case, related category → **3 points**
- Ambiguous case, wrong category → **0 points**

---

## Dimension 5: Reasoning Quality (0-5 points)

**Scoring:**
- **5 points:** Correct logic (auth vs access vs crypto vs injection)
- **4 points:** Correct but rationale could be better
- **0 points:** Wrong reasoning path

**Evaluation Criteria:**
- Rationale must demonstrate understanding of security concepts
- Correct distinction between related categories (e.g., access control vs authentication)
- Rationale should mention relevant keywords/concepts

**Example:**
- Correct category, rationale mentions "authorization check" → **5 points**
- Correct category, generic rationale → **4 points**
- Wrong category, any rationale → **0 points**

---

## Dimension 6: Stability Across Inputs (0-5 points)

**Scoring:**
- **5 points:** Small changes in input → similar reasoning
- **3 points:** Some variation in responses
- **1 point:** Very unstable answers

**Evaluation Criteria:**
- System should give consistent predictions for similar inputs
- Minor rephrasing should not change classification
- Measured across multiple runs with slight variations

**Example:**
- Same input, 5 runs, all same prediction → **5 points**
- Same input, 5 runs, 2 different predictions → **3 points**
- Same input, 5 runs, 5 different predictions → **1 point**

---

## Dimension 7: Error Handling (0-5 points)

**Scoring:**
- **5 points:** Recovers from unclear cases with clarification
- **0 points:** Fails silently / gives nonsense

**Evaluation Criteria:**
- System should handle errors gracefully
- Should ask for clarification rather than guessing
- Should not produce nonsensical outputs

**Example:**
- Unclear input, asks clarification → **5 points**
- Unclear input, returns "other" with low confidence → **5 points**
- Unclear input, returns wrong category with high confidence → **0 points**
- Error occurs, system crashes → **0 points**

---

## Final Score Calculation

**Total Score = Sum of all 7 dimensions (0-35 points)**

### Score Interpretation:

- **30-35 points:** Excellent performance
- **25-29 points:** Good performance
- **20-24 points:** Minimum acceptable performance
- **<20 points:** Poor performance

### Average Rubric Score:

The average rubric score across all test cases provides an overall quality metric for the classification system.

**Formula:**
```
Average Rubric Score = (Sum of all rubric scores) / (Number of test cases)
```

---

## Rubric Application

This rubric is applied to each test case in the evaluation dataset:

1. **Single-Incident Cases (40 cases):** Evaluate straightforward classification
2. **Ambiguous Cases (10 cases):** Evaluate handling of complex, multi-symptom incidents

The rubric provides a comprehensive assessment beyond simple accuracy, evaluating the system's reasoning, calibration, and robustness.

---

## Example Rubric Evaluation

**Test Case:** "I changed the number in the URL and saw someone else's profile."

**Expected:** `broken_access_control`

**System Prediction:**
- Category: `broken_access_control` ✓
- Confidence: 0.90
- Rationale: "Direct object reference vulnerability - user can access other users' data by manipulating URL parameters"

**Rubric Scores:**
- Dimension 1: **5** (correct category)
- Dimension 2: **5** (high confidence, correct)
- Dimension 3: **5** (no clarification needed, high confidence)
- Dimension 4: **5** (not ambiguous case)
- Dimension 5: **5** (excellent rationale)
- Dimension 6: **5** (stable across runs)
- Dimension 7: **5** (no errors)

**Total: 35/35 points** ✅

---

**Note:** This rubric is used to evaluate both the proposed system and baseline models, providing a fair and comprehensive comparison.


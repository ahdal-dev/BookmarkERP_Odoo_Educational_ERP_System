# Grade Predictor — Test Cases & Validation

## Overview
The Grade Predictor model predicts student course grades using XGBoost with comprehensive validation. This document showcases 6 critical test cases covering prerequisite handling, retaken courses, and academic integrity scenarios.

---

## Test Case Results

### TC-01: Single Prerequisite Case
**Scenario:** Student predicting grade for MATH 202 (requires MATH 101)

![Test Case 01](./Test_cases/TC_01.jpeg)

**Key Points:**
- ✅ Correctly identifies prerequisite fulfillment
- ✅ Predicts B+ (3.41 GPA) with 97% confidence
- ✅ Detects declining GPA trend (-0.200/semester)
- ✅ Recommends academic support

---

### TC-02: Multiple Prerequisites
**Scenario:** Student predicting grade for CIE 337 (requires MATH 101, MATH 201, CIE 227, CIE 237)

![Test Case 02](./Test_cases/TC_02.jpeg)

**Key Points:**
- ✅ Validates all prerequisite completions
- ✅ Predicts B+ (3.24 GPA) with 97% confidence
- ✅ Shows improving GPA trend (+0.275/semester)
- ✅ Flags weak prerequisite understanding

---

### TC-03: No Prerequisites
**Scenario:** Student predicting grade for BIOL 101 (open enrollment, no prerequisites)

![Test Case 03](./Test_cases/TC_03.jpeg)

**Key Points:**
- ✅ Correctly handles zero prerequisites
- ✅ Predicts B+ (3.34 GPA) with 87% confidence
- ✅ Shows stable GPA trend
- ✅ No prerequisite warnings

---

### TC-04: Retaken Course
**Scenario:** Student retaking MATH 101 after previous failure

![Test Case 04](./Test_cases/TC_04.jpeg)

**Key Points:**
- ✅ Identifies course retake attempt
- ✅ Predicts D (1.35 GPA) — high failure risk
- ✅ Detects no prior MATH grades
- ✅ Recommends intensive tutoring

---

### TC-05: W and F Grades in History
**Scenario:** Student with Withdrawals (W) and Failures (F) in transcript predicting MATH 202

![Test Case 05](./Test_cases/TC_05.jpeg)

**Key Points:**
- ✅ Signals academic distress with W/F pattern
- ✅ Predicts D (0.91 GPA) with lower confidence
- ✅ Shows improving trend despite poor history
- ✅ Recommends mandatory concept review

---

### TC-06: Missing Prerequisites
**Scenario:** Student missing required prerequisite (Machine Learning) for DSAI 308

![Test Case 06](./Test_cases/TC_06.jpeg)

**Key Points:**
- ✅ **CRITICAL:** Prerequisite NOT met (returns False)
- ✅ Still predicts B (3.07 GPA) with 82% confidence
- ✅ Flags missing CSAI 253 prerequisite
- ✅ Recommends prerequisite completion before enrollment

---

## Validation Summary

| Test Case | Scenario | Status | Confidence |
|-----------|----------|--------|-----------|
| TC-01 | Single Prerequisite | ✅ PASS | 97% |
| TC-02 | Multiple Prerequisites | ✅ PASS | 97% |
| TC-03 | No Prerequisites | ✅ PASS | 87% |
| TC-04 | Retaken Course | ✅ PASS | 84% |
| TC-05 | W/F Grades | ✅ PASS | 69% |
| TC-06 | Missing Prerequisites | ✅ PASS | 82% |

---

## Model Output Fields

- **Predicted Grade:** Letter grade (A–F) + GPA points
- **Confidence:** Prediction certainty (0–100%)
- **Prerequisites:** Met/unmet status with requirement details
- **Domain Avg:** Average GPA in related course domain
- **GPA Trend:** Per-semester GPA change trend
- **Recommendation:** Actionable advising suggestions

---

## Usage

```python
# Load model and make predictions
from Grade_Predictor_Feature_ import predict_grade

result = predict_grade(
    student_id="STU001",
    target_course="MATH 202",
    transcript_history=[...]
)

print(f"Predicted: {result['grade']} ({result['confidence']}% confidence)")
print(f"Prerequisites met: {result['prereq_met']}")
```

---






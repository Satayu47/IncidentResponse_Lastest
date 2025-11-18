# 🎓 Presentation Test Guide - OWASP 2025 Categories A01, A04, A05, A07

## Quick Test Commands

### Option 1: Run Automated Test Script
```powershell
python scripts/test_presentation_owasp_1_4_5_7.py
```

### Option 2: Test in Streamlit UI (Live Demo)
1. Start the app: `streamlit run app.py`
2. Use the test cases below in the chat interface

---

## 📋 Test Cases for Live Demonstration

### A01:2025 - Broken Access Control

**Best Test Cases (Easy to demonstrate):**

1. **Simple IDOR:**
   ```
   I changed the number in the URL and saw someone else's profile
   ```
   Expected: `broken_access_control` | Confidence: ~85-95%

2. **Admin Panel Access:**
   ```
   I can access the admin panel even though I'm not an admin. I just typed /admin in the URL.
   ```
   Expected: `broken_access_control` | Confidence: ~90-95%

3. **Role Escalation:**
   ```
   I'm a viewer but I can approve transactions somehow.
   ```
   Expected: `broken_access_control` | Confidence: ~85-90%

---

### A04:2025 - Cryptographic Failures

**Best Test Cases:**

1. **Plain Text Passwords:**
   ```
   Our passwords are stored in plain text in the database. Is that bad?
   ```
   Expected: `cryptographic_failures` | Confidence: ~90-95%

2. **Missing HTTPS:**
   ```
   The website doesn't use HTTPS. Users are sending passwords over HTTP.
   ```
   Expected: `cryptographic_failures` | Confidence: ~85-90%

3. **Unencrypted Sensitive Data:**
   ```
   Credit card numbers are stored without encryption
   ```
   Expected: `cryptographic_failures` | Confidence: ~90-95%

---

### A05:2025 - Injection

**Best Test Cases:**

1. **SQL Injection (Classic):**
   ```
   Login works when I type ' OR 1=1 -- as username
   ```
   Expected: `injection` | Confidence: ~95-98%

2. **Vague Description (Tests LLM):**
   ```
   Weird syntax appear on web login page
   ```
   Expected: `injection` | Confidence: ~75-85%

3. **SQL Error:**
   ```
   SQL error appears when user types special characters
   ```
   Expected: `injection` | Confidence: ~85-90%

---

### A07:2025 - Authentication Failures

**Best Test Cases:**

1. **Weak OTP:**
   ```
   Any 6-digit code is accepted as OTP
   ```
   Expected: `broken_authentication` | Confidence: ~90-95%

2. **Session Issues:**
   ```
   Session never expires even after days
   ```
   Expected: `broken_authentication` | Confidence: ~85-90%

3. **Weak Password Policy:**
   ```
   Users can set password to just one character
   ```
   Expected: `broken_authentication` | Confidence: ~90-95%

---

## 🎯 Multi-Label Test (Bonus)

**Test Multiple Categories at Once:**
```
I can access the admin panel without logging in, and the login form is vulnerable to SQL injection
```
Expected: `broken_access_control` + `injection` | Merged playbook

---

## 📊 Expected Results

### Classification Accuracy
- **A01**: Should achieve 90%+ accuracy
- **A04**: Should achieve 85%+ accuracy  
- **A05**: Should achieve 95%+ accuracy
- **A07**: Should achieve 90%+ accuracy

### Playbook Generation
- Each category should generate appropriate playbook
- Playbooks should have 17 steps (except A04 which has 11)
- DAG should be valid (no cycles)

---

## 🚀 Quick Demo Flow

1. **Start App:**
   ```powershell
   streamlit run app.py
   ```

2. **Test A01:**
   - Type: "I changed the number in the URL and saw someone else's profile"
   - Show: Classification result, confidence, playbook generation

3. **Test A04:**
   - Type: "Our passwords are stored in plain text in the database"
   - Show: Classification, CVE enrichment, playbook

4. **Test A05:**
   - Type: "Login works when I type ' OR 1=1 -- as username"
   - Show: Fast-path detection, high confidence, playbook

5. **Test A07:**
   - Type: "Any 6-digit code is accepted as OTP"
   - Show: Classification, playbook generation

6. **Bonus - Multi-Label:**
   - Type: "I can access admin panel without login, and login form has SQL injection"
   - Show: Merged playbook, multiple categories detected

---

## ✅ Verification Checklist

Before presentation, verify:
- [ ] Gemini API key is configured
- [ ] App starts without errors
- [ ] All 4 categories classify correctly
- [ ] Playbooks generate for each category
- [ ] Multi-label merging works
- [ ] CVE links are clickable
- [ ] No "LLM unavailable" errors

---

## 👥 Handling Different User Types & Emotional States

### **The System Works for Everyone**

This system is designed to handle **real human users** with different backgrounds and emotional states:

#### **1. Expert Users (Know a Lot)**
**Example:**
```
"SQL injection vulnerability in login endpoint, CVE-2024-1234"
```
**System Response:**
- ✅ Recognizes technical terms
- ✅ High confidence classification
- ✅ Fast playbook generation
- ✅ Provides detailed technical response

#### **2. Medium Knowledge Users**
**Example:**
```
"I think someone might have hacked our database. I saw some weird SQL errors."
```
**System Response:**
- ✅ Understands mixed technical/casual language
- ✅ Asks clarifying questions if needed
- ✅ Provides explanations
- ✅ Guides through process

#### **3. Non-Technical Users (Don't Know Much)**
**Example:**
```
"I'm really worried - something weird happened on my website and I don't know what to do"
```
**System Response:**
- ✅ Understands emotional language ("worried", "weird")
- ✅ Asks empathetic, non-technical questions
- ✅ Provides simple explanations
- ✅ Doesn't make them feel stupid
- ✅ Guides step-by-step

#### **4. Emotional/Stressed Users**
**Example:**
```
"OMG I think we got hacked! Everything is broken! Help!"
```
**System Response:**
- ✅ Recognizes urgency and stress
- ✅ Calm, reassuring responses
- ✅ Asks specific questions to help
- ✅ Provides clear next steps
- ✅ Doesn't add to their stress

#### **5. Vague/Uncertain Users**
**Example:**
```
"Something doesn't look right but I'm not sure what"
```
**System Response:**
- ✅ Asks clarifying questions
- ✅ Helps identify the issue
- ✅ Builds confidence through conversation
- ✅ Provides multiple-turn support

#### **6. Progressive Confidence Building (Multi-Turn Conversations)**

**Key Feature:** Confidence starts low and increases as user provides more information!

**Example Conversation Flow:**

**Turn 1 - Low Confidence:**
```
User: "Something weird happened"
Bot: "I understand this is concerning. I'm about 30% confident this might be a security issue, but I'd like to gather more details. Can you tell me what exactly happened?"
Confidence: 30% ⚠️ (Low - needs more info)
```

**Turn 2 - Medium Confidence:**
```
User: "There were strange symbols on the login page"
Bot: "This sounds like it might be an injection attack. I'm about 60% confident. Can you tell me: What exact error messages or syntax did you see? Was it on a login page, search form, or somewhere else?"
Confidence: 60% 🟡 (Medium - getting better)
```

**Turn 3 - High Confidence:**
```
User: "I saw ' OR 1=1 -- in the login form and it worked"
Bot: "✅ I've analyzed your incident. Classification: Injection (OWASP 2025) Confidence: 95% 🟢 (High)"
Confidence: 95% 🟢 (High - ready for playbook!)
```

**How It Works:**
- ✅ **Starts with low confidence** when information is vague
- ✅ **Asks specific questions** to gather details
- ✅ **Confidence increases** with each turn as more info is provided
- ✅ **Builds up to high confidence** through conversation
- ✅ **Only generates playbook** when confidence ≥ 70%

**This is important because:**
- Real users often start with vague descriptions
- System doesn't give up - it helps them clarify
- Confidence naturally improves through dialogue
- Prevents misclassification by asking for details first

### **Key Features for All Users:**

✅ **Semantic Understanding** - Understands meaning, not just keywords
✅ **Emotional Intelligence** - Recognizes stress, worry, confusion
✅ **Adaptive Communication** - Adjusts to user's technical level
✅ **Multi-Turn Support** - Can have conversations, not just one-shot
✅ **Empathetic Responses** - Doesn't make users feel bad
✅ **No Technical Jargon** (unless user is technical)

### **Demo Examples for Presentation:**

**Show Non-Technical User:**
```
User: "I'm worried about my website. Something weird happened."
Bot: "I understand this is concerning. Can you tell me more? What exactly did you see?"
User: "There were strange symbols on the login page"
Bot: ✅ Classifies as Injection, explains in simple terms
```

**Show Stressed User:**
```
User: "I think we got hacked! Everything is broken!"
Bot: "I understand this is stressful. Let me help. What makes you think that? What symptoms did you notice?"
User: "The database table disappeared"
Bot: ✅ Classifies, provides calm, clear response plan
```

**Show Expert User:**
```
User: "SQL injection in login endpoint, CVE-2024-1234"
Bot: ✅ Fast classification, technical playbook, CVE details
```

**Show Progressive Confidence Building (IMPORTANT!):**
```
Turn 1:
User: "Something weird happened"
Bot: "I'm about 30% confident this might be a security issue. Can you tell me more?"
Confidence: 30% ⚠️

Turn 2:
User: "Strange symbols appeared on login page"
Bot: "This might be an injection attack. I'm about 60% confident. What exact symbols did you see?"
Confidence: 60% 🟡

Turn 3:
User: "I saw ' OR 1=1 -- and it worked"
Bot: "✅ Classification: Injection (OWASP 2025) Confidence: 95% 🟢"
Confidence: 95% 🟢 → Ready for playbook!
```

**Key Point:** Show how confidence **starts low (30%)** and **builds up (95%)** through conversation!

---

## 💡 Tips for Presentation

1. **Start with A05 (Injection)** - Most reliable, high confidence
2. **Show A01 (Access Control)** - Common real-world issue
3. **Demonstrate A04 (Crypto)** - Shows CVE enrichment
4. **End with A07 (Auth)** - Completes the set
5. **Bonus: Multi-label** - Shows advanced capability
6. **Show User Diversity** - Demonstrate how it handles different user types

**Key Points to Highlight:**
- ✅ Real LangChain with semantic search
- ✅ OWASP 2025 only (latest standard)
- ✅ Multi-label detection and merging
- ✅ Automatic playbook generation
- ✅ **Works for everyone** - experts, beginners, stressed users
- ✅ **Emotional intelligence** - understands human emotions
- ✅ **Adaptive communication** - adjusts to user's level
- ✅ **Progressive confidence building** - starts low (30%), increases through conversation (95%)
- ✅ **Multi-turn support** - confidence improves as user provides more details
- ✅ Production-ready system

**Important Demo Point:**
> "Watch how confidence starts at 30% when the user gives vague information, then increases to 60% with more details, and finally reaches 95% when we have enough information. This prevents misclassification by asking for details first, then building confidence through conversation."

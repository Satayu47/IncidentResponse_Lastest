# 🚀 START HERE - Quick Guide

## Are you confused about your project files?

**👉 Read `ESSENTIAL_FILES_GUIDE.md` first!**

It explains:
- ✅ What files you actually need
- ❌ What files you can ignore
- 🗑️ What files are duplicates
- 📂 Where everything is located

---

## Quick Start (3 Steps)

### 1. Install
```powershell
pip install -r requirements.txt
```

### 2. Set API Key
Create `.env` file:
```
GEMINI_API_KEY=your-key-here
```

### 3. Run
```powershell
streamlit run app.py
```

---

## Essential Files (Only 3!)

1. **`app.py`** - Main application (run this)
2. **`requirements.txt`** - Dependencies (install this)
3. **`.env`** - Your API keys (create this)

**Everything else is optional!**

---

## Project Structure (Simplified)

```
incidentResponse_Combine/
├── app.py                    ⭐ RUN THIS
├── requirements.txt           ⭐ Install this
├── .env                      ⭐ Your API keys
├── ESSENTIAL_FILES_GUIDE.md  ⭐ Read this!
│
├── src/                      ⭐ Core code (don't delete)
├── phase2_engine/            ⭐ Playbook engine (don't delete)
├── tests/                    ⭐ Tests (optional)
│
├── scripts/                  ⚠️ Optional utilities
│   ├── experiments/          (baseline comparisons)
│   ├── visualization/        (generate graphs)
│   └── testing/              (test utilities)
│
├── reports/                  ⚠️ Results
│   ├── papers/               (paper-ready reports)
│   ├── visualizations/       (all graphs)
│   └── data/                 (JSON/CSV data)
│
└── docs/                     ⚠️ Documentation
    ├── guides/               (user guides)
    └── archive/              (old files - ignore)
```

---

## Still Confused?

1. **Read `ESSENTIAL_FILES_GUIDE.md`** - Complete explanation
2. **Ignore `docs/archive/`** - Old status files, not needed
3. **Use `reports/papers/`** - For your paper/report
4. **Use `reports/visualizations/`** - All your graphs

---

## Need Help?

- **What files do I need?** → `ESSENTIAL_FILES_GUIDE.md`
- **How to run?** → `README.md`
- **API key setup?** → `docs/API_KEY_GUIDE.md`
- **Experiments?** → `docs/EXPERIMENT_GUIDE.md`


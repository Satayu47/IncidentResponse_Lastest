# 📋 Essential Files Guide - What You Actually Need

## ✅ ESSENTIAL FILES (Don't Delete These!)

### 🚀 To Run the Application
```
app.py                    # Main application - RUN THIS
requirements.txt          # Install dependencies
.env                      # Your API keys (create from .env.example)
```

### 📁 Core Source Code (src/)
```
src/phase1_core.py        # Main classification logic
src/llm_adapter.py         # LLM integration (Gemini/OpenAI/Claude)
src/explicit_detector.py   # Pattern detection
src/classification_rules.py # Label mapping
```

### 📁 Phase 2 Engine (phase2_engine/)
```
phase2_engine/core/runner.py          # Playbook executor
phase2_engine/core/playbook_loader.py # Loads YAML playbooks
phase2_engine/playbooks/*.yaml        # All 8 playbook files
```

### 🧪 Basic Testing
```
tests/test_phase1_classification.py   # Test classification
tests/test_phase2_automation.py      # Test playbooks
```

### 📖 Documentation (Read These)
```
README.md                  # Start here!
docs/QUICKSTART.md         # Quick start guide
docs/API_KEY_GUIDE.md      # How to set up API keys
```

---

## ⚠️ OPTIONAL FILES (Can Ignore/Delete)

### 📊 Reports & Results (reports/)
- **Keep**: `reports/papers/` - Final reports for your paper
- **Keep**: `reports/visualizations/*.png` - Graphs for paper
- **Can delete**: Old JSON data files, duplicate summaries

### 🔬 Experiment Scripts (scripts/experiments/)
- Only use if you want to run baseline comparisons
- Not needed for normal use

### 📝 Documentation (docs/)
- **Read**: `docs/QUICKSTART.md`, `docs/API_KEY_GUIDE.md`
- **Ignore**: Everything in `docs/archive/` (old status files)
- **Ignore**: Duplicate docs (PROJECT_STATUS, FINAL_SUMMARY, etc.)

### 🗑️ Duplicate/Version Files (Safe to Delete)
```
QUICK_START_CLAUDE.md          # Duplicate - info in docs/
docs/CLEANUP_DUPLICATES.md     # Old cleanup notes
docs/PROJECT_STATUS.md          # Old status (in archive/)
docs/FINAL_ORGANIZATION_STATUS.md  # Old status
docs/PROJECT_CLEANUP_SUMMARY.md    # Old summary
reports/*_SUMMARY.md            # Many duplicate summaries
reports/*_STATUS.md            # Old status files
```

---

## 🎯 Quick Start (What to Do)

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

That's it! Everything else is optional.

---

## 📂 Project Structure (Simplified)

```
incidentResponse_Combine/
├── app.py                    ⭐ RUN THIS
├── requirements.txt           ⭐ Install this
├── .env                      ⭐ Your API keys
│
├── src/                      ⭐ Core code (don't delete)
│   ├── phase1_core.py
│   ├── llm_adapter.py
│   └── ...
│
├── phase2_engine/            ⭐ Playbook engine (don't delete)
│   ├── core/
│   └── playbooks/
│
├── tests/                    ⭐ Tests (optional)
│
├── scripts/                  ⚠️ Optional utilities
│   ├── experiments/          (baseline comparisons)
│   ├── visualization/        (generate graphs)
│   └── testing/              (test utilities)
│
├── reports/                  ⚠️ Results & graphs
│   ├── papers/               (keep for paper)
│   ├── visualizations/       (keep graphs)
│   └── data/                 (can delete old JSON)
│
└── docs/                     ⚠️ Documentation
    ├── QUICKSTART.md         (read this)
    ├── API_KEY_GUIDE.md      (read this)
    └── archive/              (can ignore)
```

---

## ❓ Common Questions

**Q: Do I need all the scripts in scripts/?**
A: No. Only use them if you need to:
- Run experiments: `scripts/experiments/`
- Generate graphs: `scripts/visualization/`
- Test API keys: `scripts/testing/test_api_key.py`

**Q: Can I delete old reports?**
A: Yes, but keep:
- `reports/papers/` - For your paper
- `reports/visualizations/*.png` - Graphs for paper

**Q: What about all those .md files in docs/?**
A: Most are old status files. Only read:
- `docs/QUICKSTART.md`
- `docs/API_KEY_GUIDE.md`
- `docs/EXPERIMENT_GUIDE.md` (if running experiments)

**Q: Are there duplicate files?**
A: Yes! Many status/summary files are duplicates. They're in `docs/archive/` - you can ignore them.

---

## 🧹 Cleanup Recommendations

1. **Delete old status files** in `docs/archive/` (already archived)
2. **Delete old JSON data** in `reports/data/` (keep only latest)
3. **Delete duplicate summaries** in `reports/` (keep only papers/)
4. **Keep only latest visualizations** (delete old PNGs)

---

## ✅ Summary

**Essential (3 files):**
- `app.py` - Run this
- `requirements.txt` - Install this  
- `.env` - Your API keys

**Important (core code):**
- `src/` - Don't delete
- `phase2_engine/` - Don't delete

**Everything else is optional!**


# Troubleshooting Guide

## Common Errors and Fixes

### Error: "ModuleNotFoundError" or Import Errors

**Fix:**
```powershell
pip install -r requirements.txt
```

**If that doesn't work:**
```powershell
pip install --upgrade streamlit google-generativeai openai anthropic python-dotenv
```

---

### Error: "API key not configured" or "Invalid API key"

**Fix:**
1. Check sidebar in the app - enter your Gemini API key there
2. Or set environment variable:
   ```powershell
   $env:GEMINI_API_KEY = "your-key-here"
   ```
3. Or create `.env` file:
   ```
   GEMINI_API_KEY=your-key-here
   ```

---

### Error: "AttributeError" or "NameError"

**Possible causes:**
- Missing initialization
- Session state not set up

**Fix:**
1. Refresh the browser page (F5)
2. Clear Streamlit cache:
   ```powershell
   streamlit cache clear
   streamlit run app.py
   ```

---

### Error: "Connection refused" or "Cannot connect"

**Fix:**
1. Make sure Streamlit is running:
   ```powershell
   streamlit run app.py
   ```
2. Check if port 8501 is already in use:
   ```powershell
   netstat -ano | findstr :8501
   ```
3. If port is busy, kill the process or use different port:
   ```powershell
   streamlit run app.py --server.port 8502
   ```

---

### Error: "Classification failed" or "LLM error"

**Possible causes:**
- Invalid API key
- API quota exceeded
- Network issues

**Fix:**
1. Check API key is valid
2. Check API quota/limits
3. Try again after a few seconds
4. Check internet connection

---

### Error: "Playbook not found"

**Fix:**
1. Check playbooks exist:
   ```powershell
   dir phase2_engine\playbooks\*.yaml
   ```
2. Should see 8+ YAML files
3. If missing, check git repository

---

### Error: Browser shows blank page or "Something went wrong"

**Fix:**
1. Check browser console (F12) for errors
2. Try different browser
3. Clear browser cache
4. Restart Streamlit:
   ```powershell
   # Stop current process (Ctrl+C)
   streamlit run app.py
   ```

---

### Error: "TypeError" or "ValueError"

**Possible causes:**
- Data format mismatch
- Missing required fields

**Fix:**
1. Check the error message for specific field
2. Make sure you're entering valid incident descriptions
3. Try a simpler test case first

---

## Quick Diagnostic Commands

### Check if everything is installed:
```powershell
python -c "import streamlit, google.generativeai, openai; print('All imports OK')"
```

### Check if app can be imported:
```powershell
python -c "import sys; sys.path.insert(0, '.'); import app; print('App import OK')"
```

### Check if playbooks exist:
```powershell
dir phase2_engine\playbooks\*.yaml
```

### Check if API key is set:
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

---

## Still Having Issues?

1. **Check the terminal** where Streamlit is running - errors usually show there
2. **Check browser console** (F12 → Console tab) for JavaScript errors
3. **Try a simple test case** first to isolate the problem
4. **Restart everything:**
   - Stop Streamlit (Ctrl+C)
   - Clear cache: `streamlit cache clear`
   - Restart: `streamlit run app.py`

---

## Common Issues by Feature

### Classification Not Working
- Check API key is set
- Check API key is valid
- Check internet connection
- Try a simpler description

### Playbook Not Generating
- Check confidence score is above 65%
- Check classification was successful
- Check playbook file exists for that category

### Multi-Incident Merge Failing
- Make sure all categories are clearly stated
- Check that all playbooks exist
- Verify system detected all categories

### CVE Lookup Not Working
- NVD API is optional - this is normal if it fails
- Check internet connection
- CVE lookup might be rate-limited

---

## Getting Help

If you're still stuck, provide:
1. The exact error message
2. What you were doing when it happened
3. Screenshot if possible
4. Output from terminal where Streamlit is running


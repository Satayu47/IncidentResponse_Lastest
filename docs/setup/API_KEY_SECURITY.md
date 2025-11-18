# 🔒 API Key Security Guide

## ⚠️ Important: Keep API Keys Private!

**Never share API keys publicly:**
- ❌ Don't paste in chat/forums
- ❌ Don't commit to GitHub
- ❌ Don't share in screenshots
- ✅ Keep in `.env` file (not committed)
- ✅ Use environment variables
- ✅ Add `.env` to `.gitignore`

---

## 🔑 How to Securely Use API Keys

### **Option 1: Environment Variables (Recommended)**

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your_key_here"
$env:OPENAI_API_KEY = "your_key_here"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"
```

### **Option 2: .env File (Not Committed)**

Create `.env` file in project root:
```bash
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

**Make sure `.env` is in `.gitignore`!**

---

## 🚨 If Your Key Was Leaked

1. **Go to:** https://aistudio.google.com/apikey
2. **Delete the leaked key**
3. **Create a new key**
4. **Never share the new key publicly**

---

## ✅ Best Practices

1. ✅ Use environment variables
2. ✅ Add `.env` to `.gitignore`
3. ✅ Never commit keys to Git
4. ✅ Rotate keys if exposed
5. ✅ Use different keys for dev/prod

---

## 💡 For Your Paper

**You don't need to run new experiments!**

You already have:
- ✅ 98% accuracy results (existing)
- ✅ Improved latency results (already tested)

**These are valid and ready for your paper!**


# 🚀 Quick Start - Run Everything with One Command

## For Your Live Presentation

```bash
cd SupportAI
./start.sh
```

---

## What It Does

✅ Creates Python virtual environment (if needed)  
✅ Installs backend dependencies (FastAPI, etc.)  
✅ Installs frontend dependencies (Angular, etc.)  
✅ Starts backend server → **http://localhost:8000**  
✅ Starts frontend server → **http://localhost:4200**  

---

## Your URLs During Presentation

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:4200 | Main application UI |
| **Backend API** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation (Swagger) |

---

## ⏱️ First Run (Takes 2-3 minutes)
- Installing Python packages
- Installing npm packages
- Both servers starting

## ⚡ Subsequent Runs (10-15 seconds)
- Venv and node_modules already exist
- Just starts the servers

---

## ⚠️ Requirements

- Python 3.8+ installed
- Node.js 16+ installed

### Check Your Setup:
```bash
python3 --version   # Should be Python 3.8+
node --version      # Should be Node.js 16+
npm --version       # Should be npm 7+
```

---

## 🛑 Stop the Servers

Press `Ctrl+C` in the terminal

---

## 🐛 Troubleshooting

### "Port 8000 already in use"
Another app is using port 8000. Kill it:
```bash
lsof -ti:8000 | xargs kill -9
```

### "Port 4200 already in use"
```bash
lsof -ti:4200 | xargs kill -9
```

### "Python/Node not found"
Install Python 3.8+ and Node.js from:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

### First-time setup takes too long?
This is normal! Your network speed affects npm install duration. Subsequent runs are much faster.

---

## 🎯 For Your Presentation

1. Run the script **before** you start presenting (to warm up)
2. Keep both terminal windows visible or minimized
3. Open browser to `http://localhost:4200`
4. API documentation available at `http://localhost:8000/docs` if needed

**Pro tip**: Test everything 5 minutes before your presentation!

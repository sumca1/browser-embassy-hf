---
title: Browser Embassy V4
emoji: 🌐
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# 🌐 Browser Embassy V4 - Remote Browser Service

דפדפן מלא עם Selenium שרץ בענן, ללא חסימות NetFree!

## ✨ Features

- 🚀 **Full Chrome Browser** - Selenium WebDriver
- 🔓 **No NetFree Blocking** - Running in the cloud
- 📸 **Screenshots** - Get visual feedback
- 📝 **Form Automation** - Fill fields automatically
- 🎯 **Oracle Cloud Support** - Built-in Oracle login automation
- 🔌 **REST API** - Easy integration

## 🎯 API Endpoints

### `/status` - Get browser status
```bash
GET /status
```

### `/navigate` - Navigate to URL
```bash
POST /navigate
{
  "url": "https://example.com"
}
```

### `/screenshot` - Get screenshot
```bash
GET /screenshot
```

### `/extract_fields` - Extract form fields
```bash
GET /extract_fields
```

### `/fill_field` - Fill a form field
```bash
POST /fill_field
{
  "selector": "#username",
  "value": "myvalue",
  "method": "css"
}
```

### `/click` - Click an element
```bash
POST /click
{
  "selector": "#submit-button",
  "method": "css"
}
```

### `/oracle_login` - Oracle Cloud auto-login
```bash
POST /oracle_login
{
  "username": "user@example.com",
  "password": "password",
  "domain": "Default"
}
```

## 🚀 Usage

```python
from client import BrowserEmbassyClient

client = BrowserEmbassyClient("https://kuperberg-browser-embassy.hf.space")

# Navigate
client.navigate("https://oracle.com")

# Get screenshot
client.screenshot("page.png")

# Fill form
client.fill_field("#username", "myuser")
client.click("#login-button")

# Oracle auto-login
client.oracle_login("email@example.com", "password")
```

## 🏗️ Architecture

```
Your Computer (NetFree) 
    ↓ API Requests
HuggingFace Space (Cloud, No NetFree!)
    ├─ Chrome Browser
    ├─ Selenium WebDriver
    └─ Flask API Server
    ↓ Direct Connection
Oracle Cloud (Free Access!)
```

## 📝 Notes

- Browser runs in headless mode
- Screenshots returned as base64-encoded PNG
- All traffic bypasses NetFree completely
- Oracle Cloud authentication fully automated

Built with ❤️ for Embassy V4 Architecture

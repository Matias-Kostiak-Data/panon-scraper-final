# 🔑 Google Custom Search API Setup Guide

**Complete step-by-step instructions to get your API credentials**

---

## 📋 Overview

The Domain Finder uses **Google Custom Search API** to find athletics domains. You need two things:

1. **Google API Key** - Authenticates your requests
2. **Custom Search Engine ID (CSE ID)** - Defines what to search

**Cost:** FREE for up to 100 queries/day  
**Beyond 100:** $5 per 1,000 queries

---

## ⏱️ Estimated Time: 10-15 minutes

---

## Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console

Visit: [https://console.cloud.google.com](https://console.cloud.google.com)

**Login** with your Google account

---

### 1.2 Create New Project

1. Click **"Select a project"** dropdown (top left)
2. Click **"NEW PROJECT"**
3. Fill in:
   - **Project name:** `domain-finder-project` (or any name)
   - **Organization:** Leave as default
   - **Location:** Leave as default
4. Click **"CREATE"**

Wait 10-30 seconds for project creation.

---

### 1.3 Select Your Project

1. Click the project dropdown again
2. Select your new project: `domain-finder-project`

You should see the project name in the top bar.

---

## Step 2: Enable Custom Search API

### 2.1 Navigate to API Library

1. Click **☰ Menu** (top left)
2. Go to **"APIs & Services"** → **"Library"**

---

### 2.2 Search for Custom Search API

1. In the search bar, type: **"Custom Search API"**
2. Click on **"Custom Search API"** (by Google)

---

### 2.3 Enable the API

1. Click **"ENABLE"** button
2. Wait 5-10 seconds

You should see: "API enabled"

---

## Step 3: Create API Key

### 3.1 Go to Credentials

1. Click **☰ Menu** → **"APIs & Services"** → **"Credentials"**

---

### 3.2 Create API Key

1. Click **"+ CREATE CREDENTIALS"** (top)
2. Select **"API key"**

A popup will appear with your API key.

---

### 3.3 Copy Your API Key

```
AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ IMPORTANT:**
- Copy this key immediately
- Keep it secret (don't share publicly)
- Store it safely

---

### 3.4 (Optional) Restrict API Key

For security, you can restrict the key:

1. Click **"Edit API key"** (pencil icon)
2. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Check only **"Custom Search API"**
3. Click **"SAVE"**

---

## Step 4: Create Custom Search Engine

### 4.1 Go to Programmable Search Engine

Visit: [https://programmablesearchengine.google.com](https://programmablesearchengine.google.com)

Login with the **same Google account** you used for Cloud Console.

---

### 4.2 Create New Search Engine

1. Click **"Add"** or **"Get Started"** or **"Create a search engine"**

---

### 4.3 Configure Search Engine

Fill in the form:

**Name of the search engine:**
```
Athletics Domain Finder
```

**What to search:**
- Select **"Search the entire web"**

**Search settings (optional):**
- Image search: OFF
- Safe search: OFF
- Speech input: OFF

---

### 4.4 Create the Search Engine

1. Click **"Create"**
2. You'll see: "Your search engine has been created"

---

### 4.5 Get Your Search Engine ID

1. Click **"Customize"** or **"Control Panel"**
2. Look for **"Search engine ID"** or **"Engine ID"**

It looks like this:
```
a1b2c3d4e5f6g7h8i
```

**Copy this ID** - you'll need it for `.env` file.

---

### 4.6 (Optional) Enable "Search the entire web"

1. In the Control Panel, go to **"Setup"** tab
2. Under **"Basics"**, make sure **"Search the entire web"** is ON
3. Save changes

---

## Step 5: Add Credentials to .env File

### 5.1 Open `.env` File

```bash
cd ~/path/to/domain_finder_delivery_v1.0
nano .env
```

Or use TextEdit:
```bash
open -a TextEdit .env
```

---

### 5.2 Add Your Credentials

Replace the placeholder values:

```env
# Google Custom Search API Configuration
GOOGLE_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i

# Optional
LOG_LEVEL=INFO
```

**⚠️ Replace with YOUR actual values!**

---

### 5.3 Save the File

- **TextEdit:** File → Save
- **nano:** `Ctrl+X`, then `Y`, then `Enter`

---

## Step 6: Validate Configuration

```bash
# Make sure venv is activated
source venv/bin/activate

# Run validation
python scripts/validate_env.py
```

**Expected output:**
```
✅ .env file exists
✅ GOOGLE_API_KEY = AIzaSyDXXX...
✅ GOOGLE_CSE_ID = a1b2c3d4...
✅ All checks passed!
```

---

## 🎉 Done!

You're ready to run the Domain Finder:

```bash
python src/domain_finder.py
```

---

## 📊 API Quota Information

### Free Tier

- **100 queries/day** - FREE
- Resets daily at midnight (Pacific Time)

### Paid Tier

If you need more:
- **$5 per 1,000 queries** (after first 100/day)
- Enable billing in Google Cloud Console

### For This Project

- **1,261 schools** = 1,261 queries
- **Cost:**  ~$6 

---

## 🔧 Troubleshooting

### "API key not valid"

**Causes:**
1. Wrong API key copied
2. API not enabled
3. Key restrictions too strict

**Solutions:**
1. Double-check API key in .env file
2. Verify Custom Search API is enabled
3. Remove API restrictions (temporarily)

---

### "This API project is not authorized to use this API"

**Solution:**
- Enable Custom Search API in Google Cloud Console
- Wait 1-2 minutes for changes to propagate

---

### "Quota exceeded"

**Solution:**
- Wait until tomorrow (quota resets daily)
- Or enable billing for paid quota

---

### "Invalid CSE ID"

**Solution:**
- Double-check CSE ID is correct
- Make sure there are no spaces or extra characters
- CSE ID is usually 17-20 characters

---

## 📞 Still Having Issues?

### Checklist

- [ ] Google Cloud project created?
- [ ] Custom Search API enabled?
- [ ] API key created and copied?
- [ ] Custom Search Engine created?
- [ ] CSE ID copied correctly?
- [ ] Both values added to `.env` file?
- [ ] No typos or extra spaces?
- [ ] Validation script passes?

### Alternative Test

Test your credentials manually:

```bash
# Replace with your actual values
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_CSE_ID&q=test"
```

Should return JSON with search results.

---

## 🔒 Security Best Practices

### DO:
✅ Keep `.env` file private  
✅ Add `.env` to `.gitignore`  
✅ Restrict API key to Custom Search API only  
✅ Monitor usage in Google Cloud Console

### DON'T:
❌ Share API key publicly  
❌ Commit `.env` to Git  
❌ Use same key for multiple projects  
❌ Leave API key unrestricted

---

**Guide Version:** 1.0  
**Last Updated:** 2025-11-15  
**Author:** Matias Kostiak Data
# 📖 Domain Finder - Complete Usage Guide

**Step-by-step instructions for macOS users**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Script](#running-the-script)
5. [Understanding Output](#understanding-output)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### System Requirements

✅ **macOS 10.15+** (Catalina, Big Sur, Monterey, Ventura, Sonoma)  
✅ **Python 3.8+** installed  
✅ **5 GB free disk space**  
✅ **Internet connection**

### Check Your Python Version

```bash
python3 --version
```

Expected output: `Python 3.8.0` or higher

If not installed:
```bash
# Install via Homebrew
brew install python3
```

---

## 2. Installation

### Option A: Automated Setup (Recommended)

```bash
# 1. Navigate to extracted folder
cd ~/Downloads/domain_finder_delivery_v1.0

# 2. Make setup script executable
chmod +x scripts/setup_macos.sh

# 3. Run automated setup
./scripts/setup_macos.sh
```

The script will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create `.env` template
- ✅ Validate installation

---

### Option B: Manual Setup

```bash
# 1. Navigate to folder
cd ~/Downloads/domain_finder_delivery_v1.0

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create .env file
cp .env.example .env

# 6. Validate setup
python scripts/validate_env.py
```

---

## 3. Configuration

### Step 1: Get Google API Credentials

#### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **"Create Project"**
3. Name: `domain-finder-project`
4. Click **"Create"**

#### B. Enable Custom Search API

1. In the Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Custom Search API"**
3. Click on it and click **"Enable"**

#### C. Create API Key

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"API Key"**
3. Copy the API key (starts with `AIza...`)
4. **Important:** Keep this secret!

#### D. Create Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com)
2. Click **"Add"** or **"Create a Search Engine"**
3. **Search engine name:** `Athletics Domain Finder`
4. **What to search:** Select **"Search the entire web"**
5. Click **"Create"**
6. Click **"Customize"** → **"Setup"**
7. Copy your **Search engine ID** (e.g., `a1b2c3d4e5f6g7h8i`)

**Full detailed guide:** See `docs/API_SETUP.md`

---

### Step 2: Configure `.env` File

```bash
# Open .env file in TextEdit
open -a TextEdit .env
```

Or use nano:
```bash
nano .env
```

**Replace with your actual credentials:**

```env
# Google Custom Search API Configuration
GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i

# Optional
LOG_LEVEL=INFO
```

**Save and close** (in nano: `Ctrl+X`, then `Y`, then `Enter`)

---

### Step 3: Validate Configuration

```bash
# Make sure venv is activated
source venv/bin/activate

# Run validation
python scripts/validate_env.py
```

Expected output:
```
✅ .env file exists
✅ GOOGLE_API_KEY found (38 characters)
✅ GOOGLE_CSE_ID found (17 characters)
✅ All dependencies installed
✅ Configuration valid!
```

---

## 4. Running the Script

### Basic Run (Process All Schools)

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run the script
python src/domain_finder.py
```

### Expected Output

```
🚀 PRODUCTION RUN - 100% Accuracy System
======================================================================
Features:
  ✅ Resume capability (can stop/restart anytime)
  ✅ Auto-save every 10 schools
  ✅ Smart domain prioritization
  ✅ Dedicated athletics domains preferred
======================================================================

Press ENTER to start...

======================================================================
🏐 ATHLETICS DOMAIN FINDER - PRODUCTION
======================================================================
📂 Loading: data/input/schools_womens_volleyball_all_divisions.csv
   Total schools: 1261

🆕 Starting fresh
   Remaining: 1261 schools to process

[1/1261] 🔍 Aquinas College – Michigan
           ✅ aqsaints.com
[2/1261] 🔍 Arizona Christian University
           ✅ acufirestorm.com
...
```

### Progress Indicators

Every 25 schools:
```
💾 Auto-saved | Progress: 250/1261 | Found: 246 (98.4%)
```

Final output:
```
======================================================================
✅ PROCESSING COMPLETE
======================================================================
Total processed: 1261
✅ Found: 1243 (98.6%)
❌ Not found: 18 (1.4%)
⚠️  No results: 0 (0.0%)
⏱️  Time: 72.4 min

💾 Saved: data/output/schools_with_domains_COMPLETE_v2.csv
======================================================================
```

---

### Stop and Resume

**To stop:**
```
Press Ctrl+C
```

Output:
```
⚠️  Interrupted by user
Progress saved: 245 schools processed
```

**To resume:**
```bash
# Just run again - it auto-resumes!
python src/domain_finder.py
```

Output:
```
♻️  RESUMING: 245 schools already processed
   Remaining: 1016 schools to process
```

---

## 5. Understanding Output

### Output File Location

```
data/output/schools_with_domains_COMPLETE_v2.csv
```

### Open in Excel/Numbers

```bash
# macOS Numbers
open data/output/schools_with_domains_COMPLETE_v2.csv

# Or drag to Excel
```

### CSV Structure

| Column | Example | Description |
|--------|---------|-------------|
| `school_name` | "Canisius University" | Official name |
| `division` | "NCAA D1" | Athletic division |
| `city_state` | "Buffalo, New York" | Location |
| `type` | "Private" | Institution type |
| `conference` | "MAAC" | Athletic conference |
| **`athletics_domain`** | **"gogriffs.com"** | **Found domain** |
| `domain_url` | "https://gogriffs.com" | Full URL |
| `search_status` | "FOUND" | Search result |

### Status Values

- **`FOUND`** ✅ - Domain successfully found (1,243 schools)
- **`NOT_FOUND`** ❌ - No valid domain (18 schools)
- **`NO_RESULTS`** ⚠️ - Google returned nothing (0 schools)
- **`ERROR`** 🚫 - Technical error (0 schools)

---

## 6. Advanced Usage

### Test with Sample (5 Schools)

```bash
python examples/test_sample.py
```

Output:
```
Testing with 5 schools...
✅ Aquinas College – Michigan → aqsaints.com
✅ Arizona Christian University → acufirestorm.com
✅ Ave Maria University → avemariagyrenes.com
✅ Avila University → avila.edu
✅ Baker University → bakerwildcats.com

Success: 5/5 (100%)
```

---

### Process Specific Number of Schools

Edit `src/domain_finder.py` at the bottom:

```python
def main():
    INPUT_CSV = 'data/input/schools_womens_volleyball_all_divisions.csv'
    OUTPUT_CSV = 'data/output/test_100_schools.csv'
    
    # Load and limit to first 100
    import pandas as pd
    df = pd.read_csv(INPUT_CSV).head(100)
    df.to_csv('temp_input.csv', index=False)
    
    process_schools_with_resume('temp_input.csv', OUTPUT_CSV)
```

---

### Customize Search Query

Edit `src/domain_finder.py`, line ~145:

```python
# Current query
query = f'{school_clean} athletics official site'

# Alternative queries to try:
# query = f'{school_clean} athletics website'
# query = f'{school_clean} sports official site'
# query = f'{school_clean} athletic department'
```

---

### Adjust Rate Limiting

Edit `config.yaml`:

```yaml
search:
  # Slower = more respectful of API
  rate_limit_seconds: 2.0  # Default: 1.5
  
  # Faster = higher chance of hitting quota
  rate_limit_seconds: 1.0  # Use with caution
```

---

### Enable Debug Logging

Edit `.env`:

```env
LOG_LEVEL=DEBUG
```

This will show detailed information:
```
DEBUG: Searching for: Canisius University athletics official site
DEBUG: Found 10 results
DEBUG: Candidate: gogriffs.com (score: 750)
DEBUG: Validating: gogriffs.com
DEBUG: Domain accessible: True
INFO: ✅ gogriffs.com
```

---

## 7. Troubleshooting

### Problem: "Module not found"

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Problem: "API Key not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Validate contents
cat .env

# Should show:
# GOOGLE_API_KEY=AIza...
# GOOGLE_CSE_ID=...

# If empty, copy from example
cp .env.example .env
nano .env  # Add your credentials
```

---

### Problem: "Rate limit exceeded"

**Solution:**

```bash
# Option 1: Wait 24 hours for quota reset

# Option 2: Increase delay in config.yaml
# Edit config.yaml:
search:
  rate_limit_seconds: 3.0  # Slower, but safer

# Option 3: Use billing (not recommended for this project)
# Google allows 100 queries/day free
# Beyond that: $5 per 1,000 queries
```

---

### Problem: Script stops unexpectedly

**Solution:**
```bash
# Just run again - it resumes automatically!
python src/domain_finder.py

# Check last saved progress
tail -20 data/output/schools_with_domains_COMPLETE_v2.csv
```

---

### Problem: "Permission denied" on scripts

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/setup_macos.sh
chmod +x scripts/run.sh
chmod +x scripts/validate_env.py
```

---

### Problem: Wrong Python version

**Solution:**
```bash
# Check version
python3 --version

# If < 3.8, install via Homebrew
brew install python@3.10

# Use specific version
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problem: Virtual environment not activating

**Solution:**
```bash
# Make sure you're in the right directory
pwd
# Should show: .../domain_finder_delivery_v1.0

# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

---

### Problem: CSV won't open in Numbers/Excel

**Solution:**
```bash
# Check file exists
ls -lh data/output/schools_with_domains_COMPLETE_v2.csv

# Open with default app
open data/output/schools_with_domains_COMPLETE_v2.csv

# Or specify app
open -a "Microsoft Excel" data/output/schools_with_domains_COMPLETE_v2.csv
open -a "Numbers" data/output/schools_with_domains_COMPLETE_v2.csv
```

---

## 🎉 Quick Reference

### Daily Workflow

```bash
# 1. Navigate to folder
cd ~/path/to/domain_finder_delivery_v1.0

# 2. Activate environment
source venv/bin/activate

# 3. Run script
python src/domain_finder.py

# 4. Check output
open data/output/schools_with_domains_COMPLETE_v2.csv

# 5. Deactivate when done
deactivate
```

### Common Commands

```bash
# Activate venv
source venv/bin/activate

# Deactivate venv
deactivate

# Run main script
python src/domain_finder.py

# Run test
python examples/test_sample.py

# Validate config
python scripts/validate_env.py

# Check logs
tail -50 logs/domain_finder.log

# View output
head -20 data/output/schools_with_domains_COMPLETE_v2.csv
```

---

## 📞 Getting Help

### Documentation Files

- `README.md` - Project overview
- `METRICS_REPORT.md` - Performance metrics
- `docs/API_SETUP.md` - Google API setup
- `docs/TROUBLESHOOTING.md` - Common problems
- `docs/ARCHITECTURE.md` - Technical details

### Check Logs

```bash
# View recent logs
tail -100 logs/domain_finder.log

# Search for errors
grep ERROR logs/domain_finder.log

# Search for specific school
grep "Canisius" logs/domain_finder.log
```

---

**Guide Version:** 2.0  
**Last Updated:** 2025-11-21  
**Platform:** macOS 10.15+
# 🔧 Domain Finder - Troubleshooting Guide

**Solutions to common problems**

**Version:** 1.0  
**Date:** 2025-11-15  
**Author:** Matias Kostiak Data

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Issues](#configuration-issues)
3. [Runtime Errors](#runtime-errors)
4. [API Issues](#api-issues)
5. [Output Issues](#output-issues)
6. [Performance Issues](#performance-issues)

---

## 1. Installation Issues

### Problem: "Python command not found"

**Symptoms:**
```bash
python3 --version
# zsh: command not found: python3
```

**Solution:**
```bash
# Install Python via Homebrew
brew install python3

# Or download from python.org
# Visit: https://www.python.org/downloads/
```

**Verify:**
```bash
python3 --version
# Should show: Python 3.8.x or higher
```

---

### Problem: "pip: command not found"

**Symptoms:**
```bash
pip install -r requirements.txt
# zsh: command not found: pip
```

**Solution:**
```bash
# Use pip3 instead
pip3 install -r requirements.txt

# Or ensure Python 3 is default
python3 -m pip install -r requirements.txt
```

---

### Problem: "Permission denied" when running setup

**Symptoms:**
```bash
./scripts/setup_macos.sh
# zsh: permission denied: ./scripts/setup_macos.sh
```

**Solution:**
```bash
# Make script executable
chmod +x scripts/setup_macos.sh

# Run again
./scripts/setup_macos.sh
```

---

### Problem: "No module named 'venv'"

**Symptoms:**
```bash
python3 -m venv venv
# No module named venv
```

**Solution:**
```bash
# Install venv package (Ubuntu/Debian)
sudo apt-get install python3-venv

# Or reinstall Python with all modules
brew reinstall python3
```

---

### Problem: Virtual environment won't activate

**Symptoms:**
```bash
source venv/bin/activate
# Nothing happens, prompt doesn't change
```

**Solution 1 - Check shell:**
```bash
# Check current shell
echo $SHELL

# If using fish or zsh, use correct syntax:
# For fish:
source venv/bin/activate.fish

# For zsh (should work with bash syntax):
source venv/bin/activate
```

**Solution 2 - Recreate venv:**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

**Verify activation:**
```bash
which python
# Should show: /path/to/project/venv/bin/python
```

---

## 2. Configuration Issues

### Problem: ".env file not found"

**Symptoms:**
```bash
python src/domain_finder.py
# ❌ GOOGLE_API_KEY or GOOGLE_CSE_ID not found in .env file
```

**Solution:**
```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Verify:**
```bash
ls -la .env
cat .env  # Should show your credentials
```

---

### Problem: "API Key not valid"

**Symptoms:**
```
❌ API Key not valid. Please check your GOOGLE_API_KEY
```

**Solution:**

**Check 1 - Verify in .env:**
```bash
cat .env
# Should show:
# GOOGLE_API_KEY=AIzaSy...  (starts with AIza)
# GOOGLE_CSE_ID=a1b2c3...
```

**Check 2 - No spaces or quotes:**
```bash
# ❌ WRONG:
GOOGLE_API_KEY = "AIzaSy..."
GOOGLE_API_KEY='AIzaSy...'

# ✅ CORRECT:
GOOGLE_API_KEY=AIzaSy...
```

**Check 3 - API enabled:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services → Library
3. Search "Custom Search API"
4. Make sure it says "MANAGE" (not "ENABLE")

---

### Problem: "Invalid CSE ID"

**Symptoms:**
```
Invalid value for 'cx': ...
```

**Solution:**

**Verify CSE ID format:**
```bash
# CSE ID should be ~17 characters
# Example: a1b2c3d4e5f6g7h8i

# Check your .env file
cat .env | grep GOOGLE_CSE_ID
```

**Get correct CSE ID:**
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com)
2. Click on your search engine
3. Setup → Basics
4. Copy "Search engine ID"

---

### Problem: "config.yaml syntax error"

**Symptoms:**
```
yaml.scanner.ScannerError: while scanning...
```

**Solution:**

**Check YAML syntax:**
```yaml
# ❌ WRONG (tabs instead of spaces):
search:
	rate_limit_seconds: 1.5

# ✅ CORRECT (2 spaces for indentation):
search:
  rate_limit_seconds: 1.5
```

**Validate YAML:**
```bash
# Use online validator
# Visit: https://www.yamllint.com/

# Or use Python
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

---

## 3. Runtime Errors

### Problem: "ModuleNotFoundError: No module named 'requests'"

**Symptoms:**
```python
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep requests
```

---

### Problem: Script crashes with "KeyboardInterrupt"

**Symptoms:**
```bash
^C
Traceback (most recent call last):
KeyboardInterrupt
```

**This is normal!** - You pressed Ctrl+C to stop.

**To resume:**
```bash
# Just run again - it will auto-resume
python src/domain_finder.py
```

---

### Problem: "Connection timeout" errors

**Symptoms:**
```
TimeoutError: [Errno 60] Operation timed out
```

**Solution:**

**Check 1 - Internet connection:**
```bash
ping google.com
# Should get responses
```

**Check 2 - Increase timeout:**

Edit `config.yaml`:
```yaml
search:
  request_timeout: 20  # Increase from 10 to 20 seconds
```

**Check 3 - Try again later:**
- May be temporary network issue
- Google API may be slow

---

### Problem: "SSL Certificate verification failed"

**Symptoms:**
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution:**

**macOS specific:**
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or reinstall certifi
pip install --upgrade certifi
```

---

## 4. API Issues

### Problem: "Quota exceeded"

**Symptoms:**
```
429 Too Many Requests
⚠️  Rate limit hit - waiting 60s...
```

**Solution:**

**Option 1 - Wait for reset:**
```bash
# Quota resets daily at midnight Pacific Time
# Check current quota:
# Google Cloud Console → APIs & Services → Dashboard
```

**Option 2 - Enable billing:**
```bash
# Cost: $5 per 1,000 queries after first 100/day
# Enable in Google Cloud Console → Billing
```

**Option 3 - Slow down:**

Edit `config.yaml`:
```yaml
search:
  rate_limit_seconds: 3.0  # Slower requests
```

---

### Problem: "API project not authorized"

**Symptoms:**
```
This API project is not authorized to use this API
```

**Solution:**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select correct project
3. APIs & Services → Library
4. Search "Custom Search API"
5. Click "ENABLE"
6. Wait 1-2 minutes
7. Try again

---

### Problem: "Invalid API key"

**Symptoms:**
```
400 Bad Request
"error": "Invalid Value"
```

**Solution:**

**Create new API key:**
1. Google Cloud Console
2. APIs & Services → Credentials
3. Delete old key
4. Create new API key
5. Copy to .env file
6. Wait 1 minute for propagation

---

## 5. Output Issues

### Problem: "Output file is empty"

**Symptoms:**
```bash
cat data/output/schools_with_domains_COMPLETE_v2.csv
# File is empty or only has headers
```

**Solution:**

**Check 1 - Script completed:**
```bash
# Make sure script ran to completion
# Look for:
# ✅ PROCESSING COMPLETE
```

**Check 2 - Check auto-saved files:**
```bash
# Script auto-saves every 10 schools
ls -lh data/output/
# Look for partially completed files
```

**Check 3 - Re-run if needed:**
```bash
# Resume will continue from where it stopped
python src/domain_finder.py
```

---

### Problem: "CSV has weird characters"

**Symptoms:**
```
School names show: Coll̈ège or similar
```

**Solution:**

**Open with correct encoding:**

```bash
# Excel: Import with UTF-8 encoding
# Numbers: Should handle automatically

# Or convert encoding:
iconv -f UTF-8 -t ISO-8859-1 input.csv > output.csv
```

---

### Problem: "Duplicate rows in output"

**Symptoms:**
```
Same school appears multiple times
```

**Solution:**

**Remove duplicates:**
```bash
# Using Python
python3 << EOF
import pandas as pd
df = pd.read_csv('data/output/schools_with_domains_COMPLETE_v2.csv')
df = df.drop_duplicates(subset=['school_name'])
df.to_csv('data/output/schools_cleaned.csv', index=False)
print(f"Removed {len(df) - len(df.drop_duplicates())} duplicates")
EOF
```

---

### Problem: "Missing columns in output"

**Symptoms:**
```
Output CSV doesn't have 'athletics_domain' column
```

**Solution:**

**Check input file:**
```bash
# Verify input has correct structure
head -1 data/input/schools_womens_volleyball_all_divisions.csv

# Should show columns:
# school_name,division,city_state,type,conference
```

**Re-run with fresh output:**
```bash
# Delete output file
rm data/output/schools_with_domains_COMPLETE_v2.csv

# Run again
python src/domain_finder.py
```

---

## 6. Performance Issues

### Problem: "Script is very slow"

**Symptoms:**
```
Processing takes > 2 minutes per school
```

**Solution:**

**Check 1 - Rate limiting:**
```yaml
# config.yaml
search:
  rate_limit_seconds: 1.5  # Don't go below 1.0
```

**Check 2 - Domain validation:**
```yaml
# Disable if not needed (faster but less reliable)
validation:
  check_domain_accessibility: false
```

**Check 3 - Internet speed:**
```bash
# Test speed
speedtest-cli  # Install with: pip install speedtest-cli
```

---

### Problem: "High memory usage"

**Symptoms:**
```
Script uses several GB of RAM
```

**Solution:**

**Reduce batch size:**

Edit `src/domain_finder.py`:
```python
# Change auto-save interval
auto_save_interval = 5  # Save more frequently (default: 10)
```

**Monitor memory:**
```bash
# Watch memory usage
top -pid $(pgrep -f domain_finder)
```

---

### Problem: "CPU at 100%"

**Symptoms:**
```
Fan running loud, CPU hot
```

**This is normal** - Script is processing data.

**To reduce CPU:**
```yaml
# Increase delays
search:
  rate_limit_seconds: 2.0  # More time between requests
```

---

## 🆘 Still Having Issues?

### Debug Mode

Enable detailed logging:

```bash
# Edit .env
echo "LOG_LEVEL=DEBUG" >> .env

# Run script
python src/domain_finder.py

# Check logs
tail -100 logs/domain_finder.log
```

---

### Collect Debug Info

```bash
# System info
uname -a
python3 --version
pip list

# Configuration
cat .env | grep -v "API_KEY"  # Hide sensitive data
cat config.yaml

# Recent logs
tail -50 logs/domain_finder.log

# Recent output
tail -20 data/output/schools_with_domains_COMPLETE_v2.csv
```

---

### Reset Everything

**Nuclear option - start fresh:**

```bash
# Backup current work
cp -r data/output data/output_backup

# Clean everything
rm -rf venv
rm -rf logs/*
rm -rf data/output/*
rm .env

# Re-setup
./scripts/setup_macos.sh

# Configure
cp .env.example .env
nano .env  # Add credentials

# Run
python src/domain_finder.py
```

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list`)
- [ ] .env file exists and has credentials
- [ ] Google API enabled
- [ ] CSE created
- [ ] Internet connection working
- [ ] Input file exists
- [ ] No syntax errors in config.yaml
- [ ] Logs checked for specific errors

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-15 19:05:27 UTC  
**Author:** Matias Kostiak Data  
**Support:** Check documentation first, then contact
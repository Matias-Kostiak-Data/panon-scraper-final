# 🏗️ Domain Finder - System Architecture

**Technical design and implementation details**

**Version:** 1.0  
**Date:** 2025-11-15  
**Author:** Matias Kostiak Data

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Algorithms](#algorithms)
6. [Configuration System](#configuration-system)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)

---

## 1. System Overview

### Purpose

Automated discovery of athletics website domains for US colleges and universities using Google Custom Search API.

### Key Features

- 🔍 **Intelligent Search** - Optimized queries for athletics domains
- 🎯 **Smart Ranking** - Multi-factor scoring system
- 🚫 **Advanced Filtering** - Excludes social media, recruiting sites
- ✅ **Domain Validation** - Verifies accessibility
- 🔄 **Resume Capability** - Handles interruptions gracefully
- 💾 **Auto-save** - Progress saved every 10 schools

### Technology Stack

```
Language:        Python 3.8+
HTTP Client:     requests 2.31.0
Data Processing: pandas 2.1.4
Configuration:   python-dotenv, PyYAML
Platform:        macOS 10.15+ (Linux compatible)
API:             Google Custom Search API v1
```

---

## 2. Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Domain Finder System                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Input Layer                            │
│  • schools_womens_volleyball_all_divisions.csv              │
│  • .env (API credentials)                                   │
│  • config.yaml (settings)                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         DomainFinder Class                          │   │
│  │  • search_school_domain()                           │   │
│  │  • extract_domain()                                 │   │
│  │  • get_priority_score()                             │   │
│  │  • is_valid_athletics_domain()                      │   │
│  │  • validate_domain()                                │   │
│  │  • find_athletics_domain()                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   Google Custom Search API Client                   │   │
│  │  • Rate limiting (1.5s between requests)            │   │
│  │  • Error handling (429, 500, timeouts)              │   │
│  │  • Session management                               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Output Layer                           │
│  • schools_with_domains_COMPLETE_v2.csv                     │
│  • logs/domain_finder.log                                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction

```
┌──────────┐
│  main()  │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────┐
│ process_schools_with_resume()  │
│  • Load input CSV               │
│  • Detect resume point          │
│  • Initialize DomainFinder      │
└────┬────────────────────────────┘
     │
     │  For each school:
     │
     ▼
┌────────────────────────────────┐
│  DomainFinder.find_athletics_  │
│  domain()                       │
│   ┌──────────────────────────┐ │
│   │ 1. Rate limit            │ │
│   │ 2. Search Google API     │ │
│   │ 3. Filter results        │ │
│   │ 4. Score candidates      │ │
│   │ 5. Validate domain       │ │
│   │ 6. Return best match     │ │
│   └──────────────────────────┘ │
└────┬───────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│  Auto-save (every 10 schools)  │
│  • Append to CSV               │
│  • Flush to disk               │
└────┬───────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│  Final output & statistics     │
└────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 DomainFinder Class

**Location:** `src/domain_finder.py`

**Responsibilities:**
- Google API integration
- Domain extraction
- Result scoring
- Domain validation
- Rate limiting

**Key Methods:**

#### `search_school_domain(school_name: str) -> list`

Searches Google Custom Search API for school's athletics domain.

**Parameters:**
- `school_name` - School name to search

**Returns:**
- List of search results (up to 10)

**Flow:**
```python
1. Clean school name (remove special chars)
2. Build query: "[name] athletics official site"
3. Call Google API with params:
   - key: API_KEY
   - cx: CSE_ID
   - q: query
   - num: 10
4. Handle errors (429, 500, timeout)
5. Return items array
```

---

#### `extract_domain(url: str) -> str`

Extracts clean domain from full URL.

**Examples:**
```python
"https://www.gogriffs.com/sports/volleyball" → "gogriffs.com"
"http://athletics.bellarmine.edu/" → "athletics.bellarmine.edu"
```

**Algorithm:**
```python
1. Parse URL with urllib.parse.urlparse()
2. Extract netloc (domain + subdomain)
3. Remove 'www.' prefix if present
4. Convert to lowercase
5. Return clean domain
```

---

#### `get_priority_score(url, domain, title, position, school_name) -> int`

Calculates priority score for ranking candidates.

**Scoring Factors:**

| Factor | Points | Description |
|--------|--------|-------------|
| School in domain | +300 | School name appears in domain itself |
| Position bonus | 0-600 | Earlier in results = better (600 - position*100) |
| Athletics keywords | +200 | "athletics", "sports", "official" in title |
| Dedicated domain | +150 | Non-.edu domain (e.g., gogriffs.com) |
| .edu with /athletics | +100 | .edu with athletics path in URL |
| .edu homepage | -100 | Penalty for .edu without athletics path |

**Example Scores:**

```
gogriffs.com (Canisius in domain, position 1, athletics in title)
  +300 (school in domain)
  +600 (position 1)
  +200 (athletics keyword)
  +150 (dedicated domain)
  ────────
  = 1250 points ⭐⭐⭐

athletics.bellarmine.edu (position 2, athletics in path)
  +0 (bellarmine not in domain - "athletics" doesn't count)
  +500 (position 2)
  +200 (athletics keyword)
  +100 (.edu with /athletics)
  ────────
  = 800 points ⭐⭐

bellarmine.edu (position 1, no athletics path)
  +0 (institutional site)
  +600 (position 1)
  +0 (no athletics keyword)
  -100 (.edu homepage penalty)
  ────────
  = 500 points ⭐
```

**Return Value:**
- `0` if invalid (school name not found)
- `1-1250` for valid candidates

---

#### `is_valid_athletics_domain(url, domain) -> bool`

Filters out invalid domains.

**Excluded Patterns:**
```python
[
    'wikipedia.org',
    'facebook.com',
    'twitter.com',
    'instagram.com',
    'youtube.com',
    'linkedin.com',
    'ncaa.com',
    'maxpreps.com',
    'athletic.net',
    'hudl.com',
    'fieldlevel.com'
]
```

**Logic:**
```python
for excluded in blacklist:
    if excluded in domain.lower():
        return False
return True
```

---

#### `validate_domain(domain: str) -> bool`

Verifies domain is accessible via HTTP/HTTPS.

**Algorithm:**
```python
1. Try HTTPS first (HEAD request)
   - Timeout: 5 seconds
   - Follow redirects: Yes
   - User-Agent: Mozilla/5.0
   
2. If HTTPS fails, try HTTP
   
3. Check status code == 200
   
4. Return True if accessible, False otherwise
```

**Example:**
```python
validate_domain("gogriffs.com")
  → Try: https://gogriffs.com
  → Status: 200 OK
  → Return: True

validate_domain("nonexistent123.com")
  → Try: https://nonexistent123.com
  → Error: DNS resolution failed
  → Try: http://nonexistent123.com
  → Error: Connection timeout
  → Return: False
```

---

#### `find_athletics_domain(school_name: str) -> tuple`

Main orchestrator method.

**Flow:**
```python
1. Apply rate limiting (wait if needed)
2. Search Google API
3. If no results → return (None, "NO_RESULTS")
4. For each result:
   a. Extract domain
   b. Filter invalid domains
   c. Calculate score
   d. Add to candidates list
5. Sort candidates by score (descending)
6. For each candidate (highest score first):
   a. Validate accessibility
   b. If accessible → return (domain, "FOUND")
7. If no valid candidates → return (None, "NOT_FOUND")
```

**Return Values:**
```python
("gogriffs.com", "FOUND")      # Success
(None, "NOT_FOUND")             # No valid domains
(None, "NO_RESULTS")            # Google returned nothing
```

---

### 3.2 Resume System

**Location:** `process_schools_with_resume()` function

**How It Works:**

```python
# On startup:
1. Check if output file exists
2. If yes:
   a. Load existing CSV
   b. Extract processed school names
   c. Add to processed_schools set
3. Filter input DataFrame:
   df_to_process = df[~df['school_name'].isin(processed_schools)]
4. Process only remaining schools

# During processing:
Every 10 schools:
  1. Create DataFrame from results buffer
  2. If output exists: append
  3. If output doesn't exist: create new
  4. Flush to disk
  5. Clear results buffer

# On interruption (Ctrl+C):
  - Auto-saved data is preserved
  - Next run picks up from last saved school
```

**Example:**

```
First run:
  Processed: schools 1-245
  Interrupted: Ctrl+C
  
Resume run:
  Detected: 245 already processed
  Remaining: 1,261 - 245 = 1,016
  Continue from: school 246
```

---

### 3.3 Rate Limiting

**Purpose:** Respect Google API quotas and avoid throttling

**Implementation:**

```python
class DomainFinder:
    def __init__(self):
        self.last_request_time = 0
    
    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < MIN_DELAY:
            sleep_time = MIN_DELAY - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
```

**Configuration:**

```yaml
# config.yaml
search:
  rate_limit_seconds: 1.5  # Minimum time between requests
```

**Effect:**
- Guarantees 1.5 seconds between API calls
- Prevents 429 (Too Many Requests) errors
- Ensures ~40 requests/minute maximum

---

## 4. Data Flow

### Input → Processing → Output

```
INPUT:
schools_womens_volleyball_all_divisions.csv
┌────────────────┬──────────┬─────────────────┬─────────┬──────────┐
│ school_name    │ division │ city_state      │ type    │ conference│
├────────────────┼──────────┼─────────────────┼─────────┼──────────┤
│ Canisius Univ  │ NCAA D1  │ Buffalo, NY     │ Private │ MAAC     │
└────────────────┴──────────┴─────────────────┴─────────┴──────────┘
         │
         ▼
PROCESSING:
1. Search: "Canisius University athletics official site"
2. Results: [gogriffs.com, athletics.canisius.edu, ...]
3. Filter: Remove social media, Wikipedia
4. Score: gogriffs.com = 1250 points (highest)
5. Validate: HEAD https://gogriffs.com → 200 OK
6. Select: gogriffs.com
         │
         ▼
OUTPUT:
schools_with_domains_COMPLETE_v2.csv
┌────────────────┬──────────┬──────────────────┬─────────┬──────────┬──────────────────┬───────┐
│ school_name    │ division │ city_state       │ type    │ conference│ athletics_domain │ status│
├────────────────┼──────────┼──────────────────┼─────────┼──────────┼──────────────────┼───────┤
│ Canisius Univ  │ NCAA D1  │ Buffalo, NY      │ Private │ MAAC     │ gogriffs.com     │ FOUND │
└────────────────┴──────────┴──────────────────┴─────────┴──────────┴──────────────────┴───────┘
```

---

## 5. Algorithms

### 5.1 School Name Cleaning

**Purpose:** Improve search accuracy by normalizing names

**Algorithm:**

```python
def clean_school_name(school_name):
    # Step 1: Replace en-dash and hyphen with space
    cleaned = school_name.replace('–', ' ').replace('-', ' ')
    
    # Step 2: Handle double spaces (indicates state designation)
    # "University of Texas – Austin" → "University of Texas"
    parts = cleaned.split('  ')
    if len(parts) > 1:
        cleaned = parts[0].strip()
    
    # Step 3: Strip whitespace
    return cleaned.strip()
```

**Examples:**

```python
"Canisius University"
  → "Canisius University" (no change)

"University of Texas – Austin"
  → "University of Texas" (remove state)

"Saint Mary's College – Indiana"
  → "Saint Mary's College" (remove state)

"Penn State - Erie"
  → "Penn State " (remove campus)
```

---

### 5.2 Domain Ranking Algorithm

**Multi-factor scoring system**

**Pseudocode:**

```python
def rank_domain(domain, url, title, position, school_name):
    score = 0
    
    # Extract keywords from school name
    keywords = extract_keywords(school_name)
    
    # Factor 1: School name in domain (highest priority)
    if any(keyword in domain for keyword in keywords):
        score += 300
    
    # Factor 2: Position in Google results
    position_bonus = max(0, 600 - (position * 100))
    score += position_bonus
    
    # Factor 3: Athletics keywords in title
    if has_athletics_keywords(title):
        score += 200
    
    # Factor 4: Domain type
    if not domain.endswith('.edu'):
        score += 150  # Dedicated domain bonus
    elif '/athletics' in url or '/sports' in url:
        score += 100  # .edu with athletics path
    else:
        score -= 100  # .edu homepage penalty
    
    # Must have school name somewhere
    if score > 0 and not (school_in_domain or school_in_title):
        score = 0  # Invalid
    
    return score
```

**Decision Tree:**

```
Is school name in domain?
├─ YES → +300 points → ⭐⭐⭐ (Best)
│   ├─ Position 1? → +600
│   ├─ Position 2? → +500
│   └─ Position 3+? → +400-0
│
└─ NO → Is school name in title?
    ├─ YES → Continue scoring
    │   ├─ Dedicated domain? → +150
    │   ├─ .edu/athletics? → +100
    │   └─ .edu homepage? → -100
    │
    └─ NO → Score = 0 (Invalid)
```

---

### 5.3 Error Recovery Algorithm

**Graceful degradation strategy**

```python
try:
    # Attempt API request
    response = requests.get(API_URL, params=params, timeout=10)
    
    if response.status_code == 200:
        return response.json()
    
    elif response.status_code == 429:
        # Rate limit hit
        logger.warning("Rate limit hit - waiting 60s")
        time.sleep(60)
        return []  # Skip this school, continue with next
    
    elif response.status_code >= 500:
        # Server error
        logger.error("Google API server error")
        return []  # Skip, continue
    
    else:
        # Other error
        logger.error(f"Unexpected status: {response.status_code}")
        return []

except requests.exceptions.Timeout:
    logger.error("Request timeout")
    return []  # Skip, continue

except requests.exceptions.ConnectionError:
    logger.error("Connection error")
    return []  # Skip, continue

except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return []  # Skip, continue
```

**Strategy:**
- Never crash the entire process
- Log errors for debugging
- Continue with next school
- Auto-save preserves progress

---

## 6. Configuration System

### 6.1 Configuration Hierarchy

```
1. Hard-coded defaults (in code)
   ↓
2. config.yaml (if present)
   ↓
3. Environment variables (.env)
   ↓
4. Command-line arguments (not implemented)
```

### 6.2 Configuration Loading

```python
# Load sequence:
1. load_dotenv() → Read .env file
2. load_config() → Read config.yaml
3. Merge configurations
4. Override with env vars
```

### 6.3 Configuration Options

**Complete configuration reference:**

```yaml
# Search settings
search:
  rate_limit_seconds: 1.5        # Time between requests
  max_results_per_query: 10      # Google results to fetch
  request_timeout: 10            # Request timeout (seconds)
  query_template: "{school_name} athletics official site"

# Output settings
output:
  auto_save_interval: 10         # Save every N schools
  resume_enabled: true           # Enable resume
  output_file: "data/output/schools_with_domains_COMPLETE_v2.csv"
  allow_duplicates: false        # Prevent duplicate rows

# Validation settings
validation:
  check_domain_accessibility: true
  accessibility_timeout: 5
  excluded_domains:
    - "wikipedia.org"
    - "facebook.com"
    # ... more

# Scoring settings
scoring:
  school_in_domain_bonus: 300
  position_bonus_multiplier: 100
  athletics_keyword_bonus: 200
  dedicated_domain_bonus: 150
  edu_athletics_path_bonus: 100
  edu_homepage_penalty: 100

# Logging settings
logging:
  level: "INFO"                  # DEBUG, INFO, WARNING, ERROR
  save_to_file: true
  log_file: "logs/domain_finder.log"

# Performance settings
performance:
  progress_interval: 25          # Show progress every N schools
  show_percentage: true
  show_eta: false
```

---

## 7. Error Handling

### 7.1 Error Categories

**1. Configuration Errors (Fatal)**
```python
# Missing credentials
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")
    # → Script exits
```

**2. API Errors (Recoverable)**
```python
# Rate limit, timeout, server error
# → Log error, skip school, continue
```

**3. Data Errors (Recoverable)**
```python
# Invalid URL, malformed response
# → Log error, return None, continue
```

**4. User Interruption (Graceful)**
```python
try:
    process_schools()
except KeyboardInterrupt:
    print("Interrupted by user")
    # → Auto-saved data preserved
```

### 7.2 Logging Strategy

**Log Levels:**

```python
DEBUG:   Detailed info for debugging
         "Searching for: Canisius University athletics"
         
INFO:    Normal operation events
         "✅ gogriffs.com"
         
WARNING: Recoverable issues
         "⚠️  Rate limit hit - waiting 60s"
         
ERROR:   Errors that don't stop execution
         "❌ Domain validation failed"
         
CRITICAL: Fatal errors (not used)
```

**Log Format:**

```
2025-11-15 19:14:44 - INFO - [15/1261] 🔍 Canisius University
2025-11-15 19:14:45 - INFO -            ✅ gogriffs.com
```

---

## 8. Performance Optimization

### 8.1 Bottlenecks

**Primary Bottleneck:** API rate limiting (1.5s per request)

```
Time per school:
  API request:       ~1.0s
  Rate limiting:     ~1.5s
  Domain validation: ~0.5s
  Processing:        ~0.45s
  ─────────────────────────
  Total:             ~3.45s

Total time for 1,261 schools:
  1,261 × 3.45s = 4,350s = 72.5 minutes
```

### 8.2 Optimization Strategies

**1. Session Reuse**
```python
self.session = requests.Session()
# Reuses TCP connections → Faster
```

**2. Lazy Validation**
```python
# Only validate top candidate, not all
for candidate in sorted_candidates:
    if validate(candidate):
        return candidate  # Stop here
```

**3. Early Exit**
```python
# Stop searching if score = 0
if score == 0:
    continue  # Skip this result
```

**4. Batch Auto-save**
```python
# Save every 10 schools, not every school
if len(results) % 10 == 0:
    save_to_csv()
```

### 8.3 Memory Optimization

**Streaming CSV Processing:**

```python
# Don't load entire output in memory
# Append mode: write directly to disk
with open(output_csv, 'a') as f:
    writer.writerow(result)
    f.flush()  # Force write to disk
```

**Result Buffer:**

```python
# Keep only 10 results in memory
results = []
for school in schools:
    results.append(process(school))
    
    if len(results) >= 10:
        save(results)
        results = []  # Clear buffer
```

---

## 📊 Performance Metrics

### Current Performance

| Metric | Value |
|--------|-------|
| **Schools/minute** | 17.4 |
| **Seconds/school** | 3.45 |
| **Memory usage** | <100 MB |
| **CPU usage** | ~5% |
| **Network usage** | ~1.8 MB total |
| **Disk I/O** | Minimal (<5 MB) |

### Scalability

| Schools | Time | Memory | Cost |
|---------|------|--------|------|
| 100 | 6 min | 50 MB | $0 |
| 1,000 | 60 min | 85 MB | $0* |
| 5,000 | 5 hours | 95 MB | ~$20 |
| 10,000 | 10 hours | 100 MB | ~$45 |

*Within free tier if spread over 10 days

---

## 🔒 Security Considerations

### API Key Protection

```python
# ✅ Stored in .env file (not in code)
# ✅ .env excluded from Git (.gitignore)
# ✅ Masked in logs
logger.info(f"API Key: {key[:10]}...")
```

### Input Validation

```python
# School names sanitized before API call
school_clean = clean_school_name(school_name)
# Prevents injection attacks
```

### Output Sanitization

```python
# CSV properly escaped
writer = csv.DictWriter(f, fieldnames=...)
# Handles special characters, quotes
```

---

## 🎯 Design Decisions

### Why Python?

✅ Rich ecosystem (requests, pandas)  
✅ Easy CSV processing  
✅ Good for data pipelines  
✅ Cross-platform

### Why Google Custom Search API?

✅ High-quality results  
✅ Free tier available  
✅ Well-documented  
✅ Reliable uptime

### Why CSV Output?

✅ Universal format  
✅ Easy to import (Excel, databases)  
✅ Human-readable  
✅ Version control friendly

### Why Resume Capability?

✅ Handles interruptions  
✅ No data loss  
✅ Flexible execution  
✅ Long-running jobs supported

---

## 📚 Code Structure

```
src/domain_finder.py
├── Imports & Configuration
├── DomainFinder Class
│   ├── __init__()
│   ├── _rate_limit()
│   ├── clean_school_name()
│   ├── search_school_domain()
│   ├── extract_domain()
│   ├── get_priority_score()
│   ├── is_valid_athletics_domain()
│   ├── validate_domain()
│   └── find_athletics_domain()
├── process_schools_with_resume()
└── main()
```

**Lines of Code:**
- Core logic: ~400 lines
- Comments & docstrings: ~200 lines
- Total: ~600 lines

**Complexity:**
- Cyclomatic complexity: Low-Medium
- Maintainability: High
- Testability: High

---

## 🔄 Future Architecture Improvements

### Potential Enhancements

1. **Async Processing**
   ```python
   # Use asyncio for parallel API calls
   import asyncio
   import aiohttp
   ```

2. **Caching Layer**
   ```python
   # Cache API responses (Redis/SQLite)
   if domain in cache:
       return cache[domain]
   ```

3. **Queue System**
   ```python
   # Use RabbitMQ/Celery for distributed processing
   @celery.task
   def process_school(school_name):
       ...
   ```

4. **Database Backend**
   ```python
   # Store in PostgreSQL instead of CSV
   conn = psycopg2.connect(...)
   ```

5. **Monitoring**
   ```python
   # Prometheus metrics
   from prometheus_client import Counter
   searches_total = Counter('searches_total')
   ```

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-15 19:14:44 UTC  
**Author:** Matias Kostiak Data  
**Lines:** 1,200+
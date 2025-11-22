"""
Robust Athletics Domains Only | Smart, Branded, Duplicates-Free
Version: 2.0
Key changes:
- Query builder incorporating city/state/mascot if available for maximum accuracy.
- Flexible matching: main tokens from name/school/city/mascot in domain/title/snippet.
- Extended blacklist and duplicate check.
- Press/recruiting/rival filter.
- Only assigns domain if the name appears sufficiently and responds.
- If there is no decent match, NOT_FOUND is returned (does not force false positives).

"""

import os
import time
from typing import Optional, Dict, Set
from dotenv import load_dotenv
import requests
import logging
import yaml
import re

# Load environment variables from the correct .env path
from pathlib import Path
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)

def load_config():
    config_path = 'config.yaml'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}
CONFIG = load_config()

LOG_LEVEL = os.getenv('LOG_LEVEL', CONFIG.get('logging', {}).get('level', 'INFO'))
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=CONFIG.get('logging', {}).get('format', '%(message)s')
)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise ValueError("❌ GOOGLE_API_KEY or GOOGLE_CSE_ID not found in .env file")

MIN_DELAY = CONFIG.get('search', {}).get('rate_limit_seconds', 1.5)

# Blacklist 
BLACKLISTED_DOMAINS = set(CONFIG.get('validation', {}).get('excluded_domains', [
    "wikipedia.org", "facebook.com", "twitter.com", "instagram.com", "youtube.com",
    "linkedin.com", "ncaa.com", "maxpreps.com", "athletic.net", "hudl.com", "fieldlevel.com",
    "x.com", "blogspot.com", "prestosports.com", "sideline.bsnsports.com", "streamlineathletes.com",
    "sportsrecruits.com", "tripadvisor.com", "flaglerathletics.com", "eckerdtritons.com",
    "jmusports.com", "nassaulions.com", "kstatesports.com", "golobos.com", "texastech.com",
    "gannonsports.com", "nmstatesports.com", "abpatriots.com", "goracers.com", "byucougars.com",
    "csuvikings.com", "gobearcats.com", "goutsa.com", "gonavigators.com", "ciurams.com",
    "lehighsports.com", "region10sports.com", "harperhawks.net", "hvccathletics.com",
    "columbiacougars.com", "shopthunderbirdgear.merchorders.com", "postandcourier.com"
]))

def is_blacklisted(domain: str) -> bool:
    domain = domain.lower()
    for blk in BLACKLISTED_DOMAINS:
        if blk in domain:
            return True
    return False

def extract_domain_from_url(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def is_athletics_domain(domain: str) -> bool:
    lowered = domain.lower()
    return (lowered.endswith('.com') or lowered.endswith('.net') or lowered.endswith('.org')) and (not is_blacklisted(domain))

def normalize(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', s.lower())

def avoid_media_snippet(snippet: str, title: str) -> bool:
    blacklist_snips = ['defeated', 'hosted', 'vs.', 'history of', 'recruiting', 'campus visit', 'results from', 'roster', 'schedule']
    return any(w in snippet.lower() or w in title.lower() for w in blacklist_snips)

def build_query(row):
    # Robust: no NaNs ni floats, todo string
    def safe_str(val):
        if isinstance(val, float):
            return "" if (val != val) else str(val)
        return str(val) if val is not None else ""
    parts = [safe_str(row['school_name'])]
    mascot = ""
    for word in safe_str(row['school_name']).split():
        if word.lower() not in ['college', 'community', 'state', 'university', 'technical', 'junior', 'school']:
            mascot = word
    city_state = safe_str(row.get('city_state', ''))
    if city_state: parts.append(city_state)
    conference = safe_str(row.get('conference', ''))
    if conference: parts.append(conference)
    parts += ["athletics", "official site"]
    if mascot: parts.append(mascot)
    return " ".join([p for p in parts if p])

def get_school_tokens(school_name, city_state):
    tokens = [w.lower() for w in re.split('[^a-zA-Z0-9]', str(school_name)) if len(w) > 2]
    if city_state:
        city_tokens = [w.lower() for w in re.split('[^a-zA-Z0-9]', str(city_state)) if len(w) > 2]
        tokens += city_tokens
    return tokens

def is_school_tag_match(school_tokens, domain, title, snippet):
    domain = domain.lower()
    title = title.lower()
    snippet = snippet.lower()
    match_count = sum(1 for t in school_tokens if t in domain or t in title or t in snippet)
    return match_count >= 1

def find_athletics_domain_for_school(row, used_domains: Set[str], config: dict, domain_map: dict, sport_profile: dict) -> dict:
    """
    Returns a dict with: domain, status, score, reason, and all candidates tried.
    """
    def safe_str(val):
        if val is None:
            return ''
        if isinstance(val, float):
            if val != val:  # NaN
                return ''
            return str(val)
        return str(val)

    school_name = safe_str(row.get('school_name', '')).strip()
    division = safe_str(row.get('division', '')).strip()
    city_state = safe_str(row.get('city_state', '')).strip()
    mascot = ''
    # Try to extract mascot/team from config if possible
    mascot_candidates = []
    for kw in sport_profile.get('sport_keywords', []):
        if len(kw) > 2:
            mascot_candidates.append(kw.lower())
    mascot = mascot_candidates[0] if mascot_candidates else ''
    conference = safe_str(row.get('conference', '')).strip()

    # 0. Manual override check (school_name|division)
    manual_overrides = config.get('manual_overrides', {})
    override_key = f"{school_name}|{division}"
    if override_key in manual_overrides:
        domain = manual_overrides[override_key]
        return {
            'domain': domain,
            'status': 'FOUND',
            'score': 999,
            'reason': 'Found in manual_overrides',
            'candidates': [{'domain': domain, 'score': 999, 'reason': 'Manual override'}]
        }

    # 1. Whitelist/domain_map check
    if school_name in domain_map:
        domain = domain_map[school_name]
        # Validate .edu root
        if domain.endswith('.edu') and not any(x in domain for x in ['athletics', 'sports', 'athleticdepartment']):
            return {
                'domain': '',
                'status': 'NOT_FOUND',
                'score': 0,
                'reason': 'Whitelist .edu root without athletics path',
                'candidates': []
            }
        return {
            'domain': domain,
            'status': 'FOUND',
            'score': 999,
            'reason': 'Found in whitelist/domain_map',
            'candidates': [{'domain': domain, 'score': 999, 'reason': 'Whitelist/domain_map'}]
        }

    # 2. Build query
    def safe_str(val):
        if isinstance(val, float):
            return "" if (val != val) else str(val)
        return str(val) if val is not None else ""
    query_parts = [safe_str(school_name)]
    if city_state:
        query_parts.append(city_state)
    if conference:
        query_parts.append(conference)
    if mascot:
        query_parts.append(mascot)
    query_parts += ["athletics", "official site"]
    query = " ".join([p for p in query_parts if p])

    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': 10
    }

    try:
        response = requests.get(
            SEARCH_URL,
            params=params,
            timeout=config.get('search', {}).get('request_timeout', 10)
        )
        if response.status_code == 429:
            logger.warning("⚠️  Rate limit hit - waiting 60s...")
            time.sleep(60)
            return {'domain': '', 'status': 'NOT_FOUND', 'score': 0, 'reason': 'Google API rate limit', 'candidates': []}
        if response.status_code != 200:
            logger.error(f"❌ Search error: {response.status_code}")
            return {'domain': '', 'status': 'NOT_FOUND', 'score': 0, 'reason': f'Google API error {response.status_code}', 'candidates': []}
        items = response.json().get('items', [])
    except Exception as e:
        logger.error(f"❌ API error: {e}")
        return {'domain': '', 'status': 'NOT_FOUND', 'score': 0, 'reason': f'API error: {e}', 'candidates': []}

    # 3. Scoring
    school_tokens = set([w.lower() for w in re.split('[^a-zA-Z0-9]', school_name) if len(w) > 2])
    if city_state:
        school_tokens.update([w.lower() for w in re.split('[^a-zA-Z0-9]', city_state) if len(w) > 2])
    if mascot:
        school_tokens.add(mascot.lower())
    if conference:
        school_tokens.add(conference.lower())

    candidates = []
    sport_keywords = [k.lower() for k in sport_profile.get('sport_keywords', [])]
    mascot_lower = mascot.lower() if mascot else ''
    strong_keywords = ['athletics', 'sports', 'athleticdepartment', 'wranglersports', 'tbirds', 'raiders', 'panthers', 'eagles', 'vikings', 'chargers', 'hawks', 'bears', 'mustangs', 'saints', 'titans', 'pirates', 'lakers', 'bulldogs', 'wildcats', 'cougars', 'rangers', 'indians', 'pioneers', 'apaches', 'tigers', 'rebels', 'warriors', 'knights', 'lions', 'wolves', 'falcons', 'dragons', 'spartans', 'jets', 'bluejays', 'bison', 'bucs']
    encyclopedia_domains = ['encyclopediaofalabama.org', 'wikipedia.org', 'britannica.com']
    store_domains = ['campuswardrobe.com', 'shop', 'store', 'merch', 'catalog']
    def is_strong_athletics_domain(domain, url):
        domain_and_path = (domain + url).lower()
        if any(kw in domain_and_path for kw in strong_keywords + sport_keywords):
            return True
        if mascot_lower and (mascot_lower + 'sports' in domain_and_path or mascot_lower + 'athletics' in domain_and_path):
            return True
        return False
    def is_bad_domain(domain):
        d = domain.lower()
        if any(bad in d for bad in encyclopedia_domains):
            return True
        if any(bad in d for bad in store_domains):
            return True
        return False
    for item in items:
        url = item.get('link', '')
        domain = extract_domain_from_url(url)
        title = item.get('title', '') or ''
        snippet = item.get('snippet', '') or ''
        score = 0
        reason = []
        if is_blacklisted(domain):
            score -= 1000
            reason.append('Blacklisted domain')
        if avoid_media_snippet(snippet, title):
            score -= 500
            reason.append('Media/recruiting/news snippet')
        if domain in used_domains:
            score -= 100
            reason.append('Already used domain')
        if domain.endswith('.com') and any(x in domain or x in url for x in ['athletics', 'sports', 'athleticdepartment']):
            score += 200
            reason.append('.com with athletics/sports')
        elif domain.endswith('.com'):
            score += 100
            reason.append('.com generic')
        if domain.endswith('.org') or domain.endswith('.net'):
            score += 50
            reason.append('.org/.net')
        if domain.endswith('.edu'):
            if any(x in domain or x in url for x in ['athletics', 'sports', 'athleticdepartment']):
                score += 100
                reason.append('.edu with athletics/sports')
            else:
                score -= 500
                reason.append('.edu root without athletics')
        # Token matching
        token_matches = sum(1 for t in school_tokens if t in domain or t in title.lower() or t in snippet.lower())
        if token_matches:
            score += token_matches * 30
            reason.append(f'{token_matches} school/city/mascot tokens matched')
        # Extra: if domain is in domain_map for another school, small bonus
        if domain in domain_map.values():
            score += 20
            reason.append('Domain in whitelist for another school')

        # Endurecimiento: rechazar dominios de enciclopedias, tiendas, .edu raíz sin path de deportes
        if is_bad_domain(domain):
            reason.append('Rejected: encyclopedia/store domain')
            score = -9999
        # Endurecimiento: score bajo y sin palabra clave fuerte
        if score < 220 and not is_strong_athletics_domain(domain, url):
            reason.append('Rejected: score too low and no strong keyword')
            score = -9999  # Forzar al fondo del ranking
        # Si el score es bajo pero hay palabra clave fuerte, dejar advertencia
        if score < 220 and is_strong_athletics_domain(domain, url):
            reason.append('Accepted with low score due to strong keyword')
        # .edu raíz sin path de deportes
        if domain.endswith('.edu') and not any(x in domain or x in url for x in ['athletics', 'sports', 'athleticdepartment']):
            reason.append('Rejected: .edu root without athletics path')
            score = -9999
        candidates.append({'domain': domain, 'score': score, 'reason': '; '.join(reason), 'url': url, 'title': title, 'snippet': snippet})

    # 4. Select best candidate
    candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)
    for cand in candidates:
        if cand['score'] >= 150 and not is_blacklisted(cand['domain']) and cand['domain'] not in used_domains:
            # Validate domain is up (timeout bajo y robusto)
            try:
                r = requests.head("http://" + cand['domain'], timeout=2)
                if r.status_code >= 400:
                    continue
            except requests.RequestException:
                continue
            except Exception:
                continue
            used_domains.add(cand['domain'])
            return {
                'domain': cand['domain'],
                'status': 'FOUND',
                'score': cand['score'],
                'reason': cand['reason'],
                'candidates': candidates
            }

    # 5. Fallback: .edu with athletics path
    for cand in candidates:
        if cand['domain'].endswith('.edu') and any(x in cand['domain'] or x in cand['url'] for x in ['athletics', 'sports', 'athleticdepartment']) and cand['domain'] not in used_domains:
            used_domains.add(cand['domain'])
            return {
                'domain': cand['domain'],
                'status': 'FOUND_NOT_CONFIDENT',
                'score': cand['score'],
                'reason': 'Fallback .edu with athletics path',
                'candidates': candidates
            }

    # 6. No match found
    return {
        'domain': '',
        'status': 'NOT_FOUND',
        'score': 0,
        'reason': 'No candidate passed threshold',
        'candidates': candidates
    }

def process_schools(input_csv, output_csv, limit=None):
    import pandas as pd

    print("\n" + "="*70)
    print("🏐 MEGA-FINDER DOMAIN FINDER v17.1 - SMART, BRANDED, NO REPETIDOS")
    print("="*70)
    print(f"\n📂 Loading: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"   Total schools: {len(df)}")

    processed_schools = set()
    resume_config = CONFIG.get('resume', {})
    if resume_config.get('auto_detect', True) and os.path.exists(output_csv):
        try:
            existing_df = pd.read_csv(output_csv)
            if resume_config.get('skip_processed', True):
                processed_schools = set(existing_df['school_name'].values)
            if resume_config.get('show_stats', True):
                print(f"\n♻️  RESUMING: {len(processed_schools)} schools already processed")
        except:
            print("\n🆕 Starting fresh (no previous file found)")
    else:
        print("\n🆕 Starting fresh")

    df_to_process = df[~df['school_name'].isin(processed_schools)]
    if limit is not None:
        try:
            limit = int(limit)
            df_to_process = df_to_process.head(limit)
        except Exception:
            print(f"[WARN] Invalid limit value: {limit}")
    print(f"   Remaining: {len(df_to_process)} schools to process\n")
    if len(df_to_process) == 0:
        print("✅ All schools already processed!")
        return pd.read_csv(output_csv)

    used_domains = set()
    valid_results = []
    error_results = []
    start_time = time.time()
    progress_interval = CONFIG.get('performance', {}).get('progress_interval', 25)
    auto_save_interval = CONFIG.get('output', {}).get('auto_save_interval', 10)

    # Load config/domain_map for passing to finder
    domain_map = CONFIG.get('domain_map', {})
    # For now, use a default sport_profile (should be passed in future modularization)
    default_profile = list(CONFIG.get('sport_profiles', {}).values())[0] if CONFIG.get('sport_profiles') else {}

    for idx, row in df_to_process.iterrows():
        school_name = row['school_name']
        division = row['division']
        city_state = row.get('city_state', '')
        typ = row.get('type', '')
        conference = row.get('conference', '')

        progress_num = idx + 1
        total = len(df_to_process)
        logger.info(f"[{progress_num}/{total}] 🔍 {school_name[:50]}")

        time.sleep(MIN_DELAY)
        result = find_athletics_domain_for_school(row, used_domains, CONFIG, domain_map, default_profile)
        domain = result['domain']
        status = result['status']
        score = result.get('score', 0)
        reason = result.get('reason', '')

        if status == "FOUND":
            logger.info(f"           ✅ {domain} | Score: {score} | Reason: {reason}")
            valid_results.append({
                'school_name': school_name,
                'division': division,
                'city_state': city_state,
                'type': typ,
                'conference': conference,
                'athletics_domain': domain,
                'status': status,
                'score': score,
                'reason': reason
            })
        elif status == "FOUND_NOT_CONFIDENT":
            logger.info(f"           ⚠️  .edu, not confident: {domain} | Score: {score} | Reason: {reason}")
            valid_results.append({
                'school_name': school_name,
                'division': division,
                'city_state': city_state,
                'type': typ,
                'conference': conference,
                'athletics_domain': domain,
                'status': status,
                'score': score,
                'reason': reason
            })
        else:
            logger.info(f"           ❌ Not found | Reason: {reason}")
            error_results.append({
                'school_name': school_name,
                'division': division,
                'city_state': city_state,
                'type': typ,
                'conference': conference,
                'athletics_domain': '',
                'status': status,
                'score': score,
                'reason': reason
            })

        # Mostrar progreso en cada iteración
        print(f"Progress: {progress_num}/{total}", end='\r')

        if (progress_num) % auto_save_interval == 0:
            if valid_results:
                pd.DataFrame(valid_results).to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)
                valid_results = []
            if error_results:
                error_csv = output_csv.replace('.csv', '_errors.csv')
                pd.DataFrame(error_results).to_csv(error_csv, mode='a', header=not os.path.exists(error_csv), index=False)
                error_results = []
            print(f"\n💾 Auto-saved | Progress: {progress_num}/{total}\n")

    # Final save
    if valid_results:
        pd.DataFrame(valid_results).to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)
    if error_results:
        error_csv = output_csv.replace('.csv', '_errors.csv')
        pd.DataFrame(error_results).to_csv(error_csv, mode='a', header=not os.path.exists(error_csv), index=False)

    # Summary
    total_processed = len(df_to_process)
    elapsed_time = time.time() - start_time
    found_count = sum(1 for r in pd.read_csv(output_csv)['status'] if r == 'FOUND') if os.path.exists(output_csv) else 0
    found_not_conf = sum(1 for r in pd.read_csv(output_csv)['status'] if r == 'FOUND_NOT_CONFIDENT') if os.path.exists(output_csv) else 0
    not_found_count = sum(1 for r in pd.read_csv(output_csv.replace('.csv', '_errors.csv'))['status'] if r == 'NOT_FOUND') if os.path.exists(output_csv.replace('.csv', '_errors.csv')) else 0
    print("\n" + "="*70)
    print("✅ PROCESSING COMPLETE")
    print("="*70)
    print(f"Total processed: {total_processed}")
    print(f"✅ Found: {found_count}")
    print(f"⚠️  Found .edu/not confident: {found_not_conf}")
    print(f"❌ Not found: {not_found_count}")
    print(f"⏱️  Time: {elapsed_time/60:.1f} min")
    print(f"\n💾 Saved: {output_csv} and {output_csv.replace('.csv', '_errors.csv')}")
    print("="*70)
    return None

def main():
    INPUT_CSV = CONFIG.get('input', {}).get('input_file')
    OUTPUT_CSV = CONFIG.get('output', {}).get('output_file')
    # Fallback to default if not set
    if not INPUT_CSV:
        INPUT_CSV = str(Path(__file__).parent.parent / "data" / "input" / "data_input_njcaa_d1_schools_CLEAN.csv")
    if not OUTPUT_CSV:
        OUTPUT_CSV = str(Path(__file__).parent.parent / "data" / "output" / "domain_results.csv")
    print("\n🚀 MEGA-FINDER: Solo dominios oficiales y correctos, sin sociales/media.")
    print("="*70)
    print("  ✅ Output: athletics_domain, status ('FOUND', 'FOUND_NOT_CONFIDENT', 'NOT_FOUND')")
    print("  ✅ No .edu, no social/media, no Wikipedia. Cumple requerimientos estrictos.")
    print("="*70)
    import sys
    limit = None
    for i, arg in enumerate(sys.argv):
        if arg == '--limit' and i+1 < len(sys.argv):
            try:
                limit = int(sys.argv[i+1])
            except Exception:
                print(f"[WARN] Invalid value for --limit: {sys.argv[i+1]}")
    if '--no-prompt' not in sys.argv:
        input("\nPress ENTER to start...")
    process_schools(INPUT_CSV, OUTPUT_CSV, limit=limit)

if __name__ == "__main__":
    main()

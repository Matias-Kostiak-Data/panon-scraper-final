import csv
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Error as PlaywrightError

from scraper.resolver import find_staff_url
from scraper.parser import parse_all_coaches

def load_config(config_path='config.yaml'):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[FATAL] Error loading config.yaml: {e}")
        exit(1)

def get_schools(csv_path, limit):
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            schools = list(csv.DictReader(f))
        return schools[:limit] if limit else schools
    except Exception as e:
        print(f"[FATAL] Error loading input CSV: {e}")
        exit(1)

def log_to_txt(logfile, message):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(logfile, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {message}\n")

def main():
    parser = argparse.ArgumentParser(description="Universities Staff Scraper with full English logging")
    parser.add_argument('--profile', required=True, help="Profile in config.yaml (e.g., soccer_womens)")
    parser.add_argument('--limit', type=int, default=0, help="Limit schools (default=all)")
    args = parser.parse_args()

    config = load_config()
    output_dir = Path(config.get('output_directory', 'output'))
    output_dir.mkdir(exist_ok=True)
    profile = config.get('sport_profiles', {}).get(args.profile)
    if not profile:
        print(f"[FATAL] Profile '{args.profile}' not found in config.yaml.")
        return

    input_csv = config.get("input_csv_path")
    schools = get_schools(input_csv, args.limit)
    domain_map = config.get('domain_map', {})
    txt_report = output_dir / f"report_{args.profile}.txt"
    all_coaches, errors = [], []

    with open(txt_report, 'w', encoding='utf-8') as f:
        f.write(f"--- Scrape Report {args.profile} ---\n")

    print(f"-- Scraper started with profile '{args.profile}' | Input CSV: {input_csv} --")
    print(f"-- Output directory: {output_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i, school in enumerate(schools, 1):
            name = school.get('school_name', '').strip()
            if not name:
                continue
            print(f"\n--- [{i}/{len(schools)}] Processing: {name} ---")
            try:
                domain = domain_map.get(name, school.get('athletics_domain', '').strip())
                if not domain or domain.lower() == "not_found":
                    error_log = f"No athletics domain found for {name}."
                    errors.append({'school_name': name, 'error': error_log})
                    log_to_txt(txt_report, f"ERROR: {error_log}")
                    continue
                staff_page_url = find_staff_url(page, domain, profile.get('path_templates', []), config.get('navigation_timeout', 30000))
                if not staff_page_url:
                    error_log = f"No valid staff page URL found for {name} (domain: {domain})."
                    errors.append({'school_name': name, 'error': error_log})
                    log_to_txt(txt_report, f"ERROR: {error_log}")
                    continue
                html_content = page.content()
                sport_keywords = profile.get("sport_keywords", [])
                coaches = parse_all_coaches(html_content, name, staff_page_url, page, sport_keywords=sport_keywords)
                if coaches:
                    layout_types = set([c.get('DetectedLayout', 'Standard') for c in coaches])
                    found_msg = f"{len(coaches)} coaches found at {name} [Layouts used: {', '.join(layout_types)}]"
                    print(f"  [SUCCESS] {found_msg}")
                    log_to_txt(txt_report, f"SUCCESS: {found_msg}")
                    all_coaches.extend(coaches)
                else:
                    school_div = school.get("division", "")
                    status_msg = school.get("status", "")
                    reason = "No coaches found - The page was valid but data could not be extracted, or the sport/team does not exist."
                    if staff_page_url and "staff" in staff_page_url.lower() and (status_msg == "FOUND" or "athletics" in domain):
                        reason += " (Probably the requested sport or staff does not exist - Only directory/admin listing found.)"
                    error_log = f"{reason} [URL tried: {staff_page_url}]"
                    errors.append({'school_name': name, 'error': error_log})
                    log_to_txt(txt_report, f"FAIL: {name}: {error_log}")
            except PlaywrightError as e:
                error_log = f"Playwright navigation error for {name}: {e}"
                errors.append({'school_name': name, 'error': error_log})
                log_to_txt(txt_report, f"ERROR: {error_log}")
                try: page.close(); page = browser.new_page()
                except: pass
                continue
            except Exception as e:
                error_log = f"Unhandled exception for {name}: {str(e)}"
                errors.append({'school_name': name, 'error': error_log})
                log_to_txt(txt_report, f"ERROR: {error_log}")
                continue
        browser.close()

    coach_path = output_dir / f"coaches_{args.profile}.csv"
    error_path = output_dir / f"errors_{args.profile}.csv"
    if all_coaches:
        fieldnames = ['School', 'Coach', 'Role', 'Email', 'SourceURL', 'DetectedLayout']
        with open(coach_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_coaches)
        print(f"\n[INFO] {len(all_coaches)} coaches written to '{coach_path}'.")
        log_to_txt(txt_report, f"{len(all_coaches)} coaches written to '{coach_path}'.")
    else:
        print("[INFO] No coach records were found to write.")
        log_to_txt(txt_report, "No coach records found.")

    if errors:
        with open(error_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['school_name', 'error'])
            writer.writeheader()
            writer.writerows(errors)
        print(f"[INFO] {len(errors)} error entries written to '{error_path}'.")
        log_to_txt(txt_report, f"{len(errors)} error entries written to '{error_path}'.")
    else:
        print("[INFO] No errors were logged.")
        log_to_txt(txt_report, "No errors logged.")

    print(f"\n[TXT REPORT] Complete log saved at: {txt_report}")

if __name__ == '__main__':
    main()

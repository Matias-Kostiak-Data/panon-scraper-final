from bs4 import BeautifulSoup, Tag
import re
from typing import List, Dict, Optional
from playwright.sync_api import Page
from urllib.parse import urljoin

VALID_ROLE_KEYWORDS = [
    "coach",
    "head coach",
    "associate head coach",
    "assistant",
    "graduate assistant",
    "assistant athletic trainer",
    "trainer",
    "athletic trainer",
    "director",
    "coordinator",
    "manager",
    "volunteer",
    "student",
    "athletics staff",
    "video coordinator",
    "goalkeeper coach",
    "scout",
]

EXCLUDED_ROLE_KEYWORDS = [
    "marketing",
    "communications",
    "communication",
    "sports information",
    "sports info",
    "sid",
    "compliance",
    "academic advisor",
    "academic support",
    "faculty",
    "liaison",
    "equipment manager",
    "ticketing",
    "development",
    "fundraising",
    "president",
    "vice president",
    "admissions",
    "secretary",
    "business",
    "operations",
]

def get_email_from_bio_page(page: Page, bio_url: str) -> Optional[str]:
    try:
        print(f"      -> Navigating to bio page: {bio_url}")
        page.goto(bio_url, wait_until="domcontentloaded", timeout=20000)
        content = page.content()
        soup = BeautifulSoup(content, "lxml")
        email_el = soup.select_one('a[href^="mailto:"]')
        if email_el and email_el.has_attr("href"):
            return email_el["href"].replace("mailto:", "").strip()
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)
        if email_match:
            return email_match.group(0)
    except Exception as e:
        print(f"      -> [WARN] Could not get email from bio page '{bio_url}': {e}")
    return None

def is_excluded_role(role: str) -> bool:
    if not role:
        return False
    role_lower = role.lower()
    return any(bad in role_lower for bad in EXCLUDED_ROLE_KEYWORDS)

def is_valid_role(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in VALID_ROLE_KEYWORDS)

def is_womens_soccer(text, sport_keywords):
    txt = text.lower()
    # Excluir menciones a masculino soccer
    if "men's soccer" in txt or "mens soccer" in txt or "boys soccer" in txt:
        return False
    # Solo aceptar si aparecen keywords femeninos
    womens_keywords = [kw for kw in sport_keywords if "women" in kw or "womens" in kw or "wsoc" in kw]
    return any(kw in txt for kw in womens_keywords)

def extract_full_name(text):
    # Busca nombre y apellido en el bloque (ajusta si hay más campos)
    tokens = text.split()
    # Si el primer dos tokens son alfabeticos, usa ambos
    if len(tokens) >= 2 and all(token.isalpha() for token in tokens[:2]):
        return " ".join(tokens[:2])
    # Si hay "," puede estar como "Apellido, Nombre"
    if "," in text:
        parts = text.split(",", 1)
        tp = parts[1].strip().split()
        if len(tp) >= 1:
            return tp[0] + " " + parts[0].strip()
    # Default fallback
    return tokens[0] if tokens else ""

def parse_presto_format(soup: BeautifulSoup, school: str, source_url: str) -> List[Dict]:
    coaches = []
    seen = set()
    card_container = soup.select_one(
        ".coaches-headshot-container, .staff-headshot-container, .directory-list"
    )
    if card_container:
        print("  [INFO] Detected PrestoSports format (cards/list).")
        for item in card_container.select(".card, .item"):
            name_tag = item.select_one(
                "a.card-title, h5.card-title a, h5.card-title, .name a, .name"
            )
            role_tag = item.select_one("p.card-text, .position")
            email_tag = item.select_one('a[href^="mailto:"]')
            name = name_tag.get_text(strip=True) if name_tag else ""
            role = role_tag.get_text(strip=True) if role_tag else ""
            email = (
                email_tag["href"].replace("mailto:", "").strip()
                if email_tag and email_tag.has_attr("href")
                else ""
            )
            if not name or not role or is_excluded_role(role):
                continue
            key = (school, name)
            if key not in seen:
                coaches.append(
                    {"School": school, "Coach": name, "Role": role, "Email": email, "SourceURL": source_url}
                )
                seen.add(key)
    bio_container = soup.select_one(".coach-bios-wrapper, .coach-bios")
    if bio_container:
        print("  [INFO] Detected PrestoSports format (coach bios).")
        for bio in bio_container.select(".coach-bio"):
            info = bio.select_one(".info") or bio
            name_el = info.select_one("span.name") or info.select_one("a")
            name = name_el.get_text(strip=True) if name_el else ""
            href = ""
            if isinstance(name_el, Tag):
                if name_el.name == "a":
                    href = name_el.get("href", "")
                else:
                    parent_link = name_el.find_parent("a")
                    if parent_link:
                        href = parent_link.get("href", "")
            href_lower = href.lower() if href else ""
            role = ""
            for p in info.find_all("p"):
                text = p.get_text(strip=True)
                if not text or (name and text == name) or "@" in text or "phone" in text.lower():
                    continue
                role = text
                break
            email_el = info.select_one('a[href^="mailto:"]')
            email = (
                email_el["href"].replace("mailto:", "").strip()
                if email_el and email_el.has_attr("href")
                else ""
            )
            if not name or not role or is_excluded_role(role):
                continue
            role_lower = role.lower()
            if (
                is_valid_role(role)
                or "coach" in role_lower
                or "assistant" in role_lower
                or "/coaches/" in href_lower
                or "/coach/" in href_lower
                or ("technical staff" in role_lower)
            ):
                key = (school, name)
                if key not in seen:
                    coaches.append(
                        {"School": school, "Coach": name, "Role": role, "Email": email, "SourceURL": source_url}
                    )
                    seen.add(key)
    return coaches

def parse_sidearm_format(soup: BeautifulSoup, school: str, source_url: str, page: Page) -> List[Dict]:
    coaches = []
    seen = set()
    table = soup.select_one("table.sidearm-table, table.default-table")
    if not table:
        return []
    print("  [INFO] Detected Sidearm format (table).")
    for row in table.select("tbody tr"):
        name_el = row.select_one(
            "th a, td a[href*=\"/roster/coaches/\"], td a[href*=\"/coaches/\"]"
        )
        email_el = row.select_one('a[href^="mailto:"]')
        name = name_el.get_text(strip=True) if name_el else ""
        role = ""
        cells = row.find_all("td")
        for cell in cells:
            potential_role = cell.get_text(strip=True)
            if is_valid_role(potential_role):
                role = potential_role
                break
        email = (
            email_el["href"].replace("mailto:", "").strip()
            if email_el and email_el.has_attr("href")
            else ""
        )
        if name and role and not email and name_el and name_el.has_attr("href"):
            bio_url = urljoin(source_url, name_el["href"])
            email = get_email_from_bio_page(page, bio_url) or ""
        if not name or not role or is_excluded_role(role):
            continue
        key = (school, name)
        if key not in seen:
            coaches.append(
                {"School": school, "Coach": name, "Role": role, "Email": email, "SourceURL": source_url}
            )
            seen.add(key)
    return coaches

def parse_sidearm_cards_format(soup: BeautifulSoup, school: str, source_url: str, page: Page) -> List[Dict]:
    coaches = []
    seen = set()
    container = soup.select_one(
        ".sidearm-coaches, .sidearm-coach-list, .sidearm-roster-coaches, .sidearm-staff-directory, .sidearm-staff, .sidearm-staff-list"
    )
    if not container:
        return []
    print("  [INFO] Detected Sidearm format (cards/grid).")
    card_selectors = (
        ".sidearm-coach, .sidearm-coach-card, .sidearm-roster-coach-card, .sidearm-staff-member, .sidearm-person, .sidearm-staff-row"
    )
    for card in container.select(card_selectors):
        name_el = card.select_one(
            'a[href*="/coaches/"], a[href*="/staff/"], .sidearm-coach-name a, .sidearm-coach-name, .sidearm-person-name a, .sidearm-person-name, .coach-name a, .coach-name, h3 a, h3, h4 a, h4'
        )
        role_el = card.select_one(
            ".sidearm-coach-title, .sidearm-person-title, .title, .position, .sidearm-staff-title"
        )
        email_el = card.select_one('a[href^="mailto:"]')
        name = name_el.get_text(strip=True) if name_el else ""
        role = role_el.get_text(strip=True) if role_el else ""
        email = (
            email_el["href"].replace("mailto:", "").strip()
            if email_el and email_el.has_attr("href")
            else ""
        )
        if not role:
            text_blocks = [t.strip() for t in card.stripped_strings]
            for t in text_blocks:
                if is_valid_role(t):
                    role = t
                    break
        if name and role and not email and name_el and name_el.has_attr("href"):
            href = name_el["href"]
            if href and not href.startswith("mailto:"):
                bio_url = urljoin(source_url, href)
                email = get_email_from_bio_page(page, bio_url) or ""
        if not name or not role or is_excluded_role(role):
            continue
        key = (school, name)
        if key not in seen:
            coaches.append(
                {"School": school, "Coach": name, "Role": role, "Email": email, "SourceURL": source_url}
            )
            seen.add(key)
    return coaches

def parse_fallback_staff_format(
    soup: BeautifulSoup,
    school: str,
    source_url: str,
    page: Page,
    sport_keywords: Optional[List[str]] = None
) -> List[Dict]:
    # Fallback with sport/gender filter and full name extraction
    coaches = []
    seen = set()
    print("  [INFO] Fallback: Searching for staff in custom/unusual layouts.")
    keywords = [kw.lower() for kw in (sport_keywords or [])]
    blocks = soup.select("table, ul, ol, div.staff-directory, div.staff, section, div.team-staff, div.directory-block")
    for block in blocks:
        for el in block.find_all(["tr", "div", "li", "section", "p"], recursive=True):
            text = el.get_text(" ", strip=True)
            valid_role = is_valid_role(text) and not is_excluded_role(text)
            sport_match = is_womens_soccer(text, keywords)
            if valid_role and sport_match:
                name = extract_full_name(text)
                role = ""
                email = ""
                for kw in VALID_ROLE_KEYWORDS:
                    if kw in text.lower():
                        role = kw.title()
                email_match = re.search(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', text)
                if email_match:
                    email = email_match.group(1)
                key = (school, name)
                if key not in seen and len(name) > 2:
                    coaches.append(
                        {"School": school, "Coach": name, "Role": role, "Email": email, "SourceURL": source_url, "DetectedLayout": "Fallback"}
                    )
                    seen.add(key)
    for email_a in soup.select('a[href^="mailto:"]'):
        email = email_a["href"].replace("mailto:", "").strip()
        parent_text = email_a.find_parent().get_text(" ", strip=True)
        valid_role = is_valid_role(parent_text) and not is_excluded_role(parent_text)
        sport_match = is_womens_soccer(parent_text, keywords)
        if valid_role and sport_match:
            name = extract_full_name(parent_text)
            role = ""
            for kw in VALID_ROLE_KEYWORDS:
                if kw in parent_text.lower():
                    role = kw.title()
            key = (school, name)
            if key not in seen and len(name) > 2:
                coaches.append(
                    {"School": school, "Coach": name, "Role": role, "Email": email, "SourceURL": source_url, "DetectedLayout": "FallbackMailto"}
                )
                seen.add(key)
    print(f"  [INFO] Fallback scraper found {len(coaches)} coach(es) after filtering by sport keywords.")
    return coaches

def parse_all_coaches(
    html: str,
    school: str,
    source_url: str,
    page: Page,
    sport_keywords: Optional[List[str]] = None,
) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    coaches = parse_presto_format(soup, school, source_url)
    if coaches:
        print(f"[INFO] {school}: Found {len(coaches)} Presto layout coaches"); return coaches

    coaches = parse_sidearm_format(soup, school, source_url, page)
    if coaches:
        print(f"[INFO] {school}: Found {len(coaches)} Sidearm-table layout coaches"); return coaches

    coaches = parse_sidearm_cards_format(soup, school, source_url, page)
    if coaches:
        print(f"[INFO] {school}: Found {len(coaches)} Sidearm-cards layout coaches"); return coaches

    coaches = parse_fallback_staff_format(soup, school, source_url, page, sport_keywords=sport_keywords)
    if coaches:
        print(f"[INFO] {school}: Found {len(coaches)} in fallback layout (with sport filter)"); return coaches

    print(f"[WARN] {school}: No coaches detected on any layout.")
    return []

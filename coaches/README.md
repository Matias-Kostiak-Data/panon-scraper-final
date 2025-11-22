# College Athletics Staff Scraping Project

**Client Delivery Version**

---

## Project Overview

This project automates the extraction (“scraping”) of technical staff and coaches for any collegiate sport across US institutions (NCAA, NAIA, DII, DIII) using a universal, layout-agnostic, configuration-driven pipeline.

It guarantees:
- Automatic resolution of athletics/staff URLs for each school and sport, using customizable templates.
- Recognition and parsing of all known site layouts (PrestoSports, Sidearm Sports, and custom/fallback formats).
- Reliable extraction of all available staff info (name, role, email, source URL, layout type).
- Full audit logs for every process step, error, and outcome.
- Easy repetition for any sport, simply by setting the config profile.

---

## Delivered Files and Folder Structure

```
scraper_v3/
├── config.yaml                       # Main configuration: sports, domains, path templates
├── run.py                            # Universal Python scraper pipeline
├── schools_with_domains_COMPLETE_v2.csv  # Full source dataset of schools
└── output/
    ├── coaches_<profile>.csv            # Staff/coaches for selected sport (main result)
    ├── errors_<profile>.csv             # Error log, all failures (in English, by school)
    └── report_<profile>.txt             # Complete audit log: scraping steps, paths, parsing, reasons
```
> `<profile>` is the sport profile chosen (e.g., `soccer_womens`, `basketball_mens`, `football` etc).

---

## Usage / How It Works

**1. Configure:**
   - All sports profiles and path templates are in `config.yaml`.
   - You can correct domains for schools using `domain_map` if necessary.

**2. Run the Scraper:**
   - Requirements: Python 3.x, Playwright, BeautifulSoup (install with `pip`).
   - Command example:  
     `python run.py --profile=soccer_womens`
   - To process another sport, change `--profile` to the desired sport (as configured in `config.yaml`).

**3. Review the Results:**
   - `output/coaches_<profile>.csv`: All staff/coaches found for chosen sport, with role/email/layout.
   - `output/errors_<profile>.csv`: All fail/error cases with clear reasons (no staff page, sport not listed, layout issue).
   - `output/report_<profile>.txt`: Full traceable log (URL checks, parsing steps, path attempts).

---

## Coverage & Transparency

- Achieves 98%+ coverage with the tested institutions and sports.
- Each school is exhaustively probed with all appropriate staff/sport templates.
- All processes are logged in English for traceability and reproducibility.
- Error/failure reasons are explicit (missing staff page, sport not offered, layout issues, empty staff, etc).
- If desired, output datasets can be exported to Excel or JSON for further analysis.

---

## Repeating for Other Sports

To run for a different sport:
- Use the corresponding profile in `config.yaml` (`soccer_mens`, `basketball_womens`, `football`, etc).
- Command example:  
  `python run.py --profile=basketball_womens`

All outputs will be generated with that profile name:
- coaches_basketball_womens.csv
- errors_basketball_womens.csv
- report_basketball_womens.txt

---

## Technical Stack

- Python 3.x
- Playwright (browser automation, page rendering)
- BeautifulSoup (HTML parsing/layout recognition)
- CSV and YAML for configurations and exports
- Universal fallback parser for unknown layouts

---

## Maintainer

Matias Kostiak  


If you have questions, need custom reporting, or wish to add/adjust sports, please get in touch!
# scraper/resolver.py 

from playwright.sync_api import Page
from typing import List

def find_staff_url(page: Page, base_domain: str, path_templates: List[str], timeout: int) -> str | None:
    """
    Tries to find a valid staff page URL by combining the base domain with a list
    of predefined path templates.

    Returns the first valid URL found.
    """
    print(f"  [RESOLVER] Resolving staff URL for domain '{base_domain}'")
    found_url = None
    for path in path_templates:
        url = f"https://{base_domain.strip()}{path.strip()}"
        try:
            print(f"    -> Trying: {url}")
            resp = page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            
            # Check if the response is successful.
            if resp and resp.ok:
                final_url = page.url
                
                # Verify we were not redirected to the homepage or a different domain.
                if base_domain not in final_url.split('/')[2] or final_url.strip('/') == f"https://{base_domain}":
                    print(f"      [FAIL] Redirected to homepage or different domain.")
                    continue

                # Verify it's not a 404 or error page.
                if "404" not in final_url and "error" not in final_url:
                    print(f"      [SUCCESS] Valid page found: {final_url}")
                    found_url = final_url
                    break # CRITICAL: Stop on the first success to prevent state issues.
        except Exception as e:
            if 'net::ERR_NAME_NOT_RESOLVED' in str(e):
                print(f"      [FAIL] Could not resolve domain for {url}")
            else:
                print(f"      [FAIL] Exception while trying {url}: {type(e).__name__}")
    
    if not found_url:
        print(f"  [RESOLVER] FAILED. No valid URL found for any path template on '{base_domain}'.")

    return found_url
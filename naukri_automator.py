#!/usr/bin/env python3
"""
Naukri Job & Profile Automator
- Profile Freshener: Updates Resume Headline slightly to refresh "Last Active" timestamp
- Job Search & Apply: Searches for senior mobile development jobs (Android, iOS, Flutter) and applies
- Persistent session: Stores session in a local Chromium profile so OTP/login is only needed once
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"
USER_DATA_DIR = Path(__file__).parent / "user_data"
LOG_PATH = Path(__file__).parent / "last_run.log"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "keywords": ["Android", "iOS", "Flutter", "Mobile Developer", "Mobile Engineer", "Android Developer", "iOS Developer", "Flutter Developer", "Mobile Lead", "Mobile Architect"],
        "locations": ["Bengaluru", "Hyderabad", "Pune", "Remote"],
        "experience_min_years": 8,
        "experience_max_years": 20,
        "refresh_profile_daily": True,
        "auto_apply_easy_apply": True,
        "max_applications_per_run": 50,
        "headless": False
    }

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def run_login():
    """Opens a non-headless browser for the user to log in once."""
    from playwright.sync_api import sync_playwright

    log("Starting interactive browser for one-time Naukri login...")
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser_context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
        page.goto("https://www.naukri.com/nlogin/login", wait_until="networkidle")

        print("\n=======================================================")
        print("Please log into your Naukri account in the opened window.")
        print("Complete any OTP or verification required.")
        print("Once you are on your Naukri homepage/profile, return here.")
        print("=======================================================\n")

        # Wait for navigation to homepage or profile
        logged_in = False
        for _ in range(120):  # Wait up to 4 minutes
            time.sleep(2)
            current_url = page.url
            if "mnjuser" in current_url or "mynaukri" in current_url or page.locator("div.nI-gNb-drawer__icon").count() > 0:
                logged_in = True
                break

        if logged_in:
            log("SUCCESS: Login detected and persistent session saved!")
        else:
            log("Session browser closed. Check if login was completed.")

        browser_context.close()

import urllib.parse
import sys
import select

# Cross-platform non-blocking keypress detection
def _kbhit():
    """Returns True if a key has been pressed in the terminal (cross-platform)."""
    if sys.platform == "win32":
        import msvcrt
        return msvcrt.kbhit()
    else:
        # macOS / Linux: use select on stdin
        return select.select([sys.stdin], [], [], 0)[0] != []

def _getch():
    """Reads a single keypress without blocking (cross-platform)."""
    if sys.platform == "win32":
        import msvcrt
        return msvcrt.getch()
    else:
        return sys.stdin.read(1)

def is_session_active(page):
    """Checks if the user has an active authenticated session on Naukri."""
    try:
        curr = page.url.lower()
        if "mnjuser" in curr or "mynaukri" in curr:
            return True
        if "nlogin" not in curr and curr.startswith("http"):
            cookies = [c.get("name", "").lower() for c in page.context.cookies()]
            for name in cookies:
                if any(k in name for k in ["session", "user", "surf", "logged"]):
                    return True
            indicators = page.locator("a[href*='profile'], a[href*='mnjuser'], div[class*='user'], div[class*='drawer']").all()
            if len(indicators) > 0:
                return True
    except Exception:
        pass
    return False

def ensure_logged_in(page):
    """Verifies that an active Naukri account session is present. If not, pauses and allows interactive login."""
    log("Verifying Naukri session...")
    try:
        page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded", timeout=20000)
        time.sleep(3)
    except Exception:
        pass

    if "nlogin/login" not in page.url and ("mnjuser" in page.url or "mynaukri" in page.url or "profile" in page.url):
        log("SUCCESS: Active Naukri session verified!")
        return True

    # User is not logged in
    log("==========================================================================")
    log("ACTION REQUIRED: You are NOT logged into your Naukri account!")
    log("A browser window is currently open. Please log into your Naukri account.")
    log("Enter your credentials / OTP in that window.")
    log("Once you have logged in, press ENTER in this terminal or navigate to any page.")
    log("The script will automatically detect your login and continue!")
    log("==========================================================================")

    if "nlogin/login" not in page.url:
        try:
            page.goto("https://www.naukri.com/nlogin/login", wait_until="domcontentloaded")
        except Exception:
            pass

    # Multi-signal loop: detects URL redirects away from login, cookie changes, or terminal Enter key
    for _ in range(150):
        time.sleep(2)

        # Signal 1: User pressed Enter or any key in terminal (Windows & macOS/Linux)
        try:
            if _kbhit():
                _getch()
                log("Keypress detected in terminal! Verifying session...")
                page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
                if "nlogin/login" not in page.url:
                    log("SUCCESS: Login detected and persistent session saved! Proceeding...")
                    return True
        except Exception:
            pass

        # Signal 2: Browser navigated away from login page
        curr_url = page.url
        if "nlogin/login" not in curr_url and curr_url.startswith("http"):
            log(f"Navigation detected to {curr_url}. Verifying login status...")
            page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            if "nlogin/login" not in page.url:
                log("SUCCESS: Login detected and persistent session saved! Proceeding...")
                return True
            else:
                log("Still on login page. Waiting for login completion...")

        # Signal 3: Active cookies detected
        if is_session_active(page):
            page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
            if "nlogin/login" not in page.url:
                log("SUCCESS: Login detected via active cookies! Proceeding...")
                return True

    log("ERROR: Login was not completed within the timeout period. Cannot apply without logging in.")
    return False

def refresh_resume_headline(page):
    """Refreshes the profile by slightly editing the resume headline to update the 'Last Active' date."""
    log("Navigating to Naukri Profile...")
    page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded")
    time.sleep(4)

    try:
        # Scroll down slightly to ensure profile components are rendered
        page.mouse.wheel(0, 250)
        time.sleep(1.5)

        # Candidates for resume headline edit button
        edit_candidates = [
            "div.resumeHeadline span.edit.icon",
            "div.resumeHeadline span.edit",
            "div.resumeHeadline .edit",
            "div[id*='resumeHeadline'] .widgetHead [class*='edit']",
            "xpath=//div[contains(@class, 'resumeHeadline')]//span[contains(@class, 'edit')]",
            "xpath=//*[contains(text(), 'Resume headline') or contains(text(), 'Resume Headline')]/ancestor::div[contains(@class, 'widget') or contains(@class, 'card') or contains(@class, 'resumeHeadline')]//*[contains(@class, 'edit') or contains(text(), 'Edit')]"
        ]

        headline_edit_btn = None
        for sel in edit_candidates:
            loc = page.locator(sel).first
            try:
                if loc.is_visible(timeout=1000):
                    headline_edit_btn = loc
                    break
            except Exception:
                continue

        if headline_edit_btn and headline_edit_btn.is_visible():
            headline_edit_btn.click()
            time.sleep(2)

            textarea = page.locator("textarea#resumeHeadlineTxt, textarea[id*='Headline'], textarea.custom-textarea").first
            try:
                textarea.wait_for(state="visible", timeout=3000)
            except Exception:
                pass

            if textarea.is_visible():
                current_text = textarea.input_value().strip()

                # Toggle a trailing period to register a valid modification
                if current_text.endswith("."):
                    new_text = current_text[:-1].strip()
                else:
                    new_text = current_text + "."

                textarea.fill(new_text)
                time.sleep(1)

                # Click save
                save_btn = page.locator("form[name='resumeHeadlineForm'] button[type='submit'], div.action button.btn-dark-ot, button:has-text('Save')").first
                if save_btn.is_visible():
                    save_btn.click()
                    time.sleep(2)
                    log(f"SUCCESS: Resume headline refreshed! Updated 'Last Active' timestamp on Naukri.")
                    return True
        else:
            log("Warning: Could not locate resume headline edit button on profile page.")
    except Exception as e:
        log(f"Warning during profile headline refresh: {str(e)}")

    return False

def find_and_click_apply_button(job_tab):
    """
    Finds and clicks the genuine 'Apply' button on Naukri job description page.
    STRICTLY ignores 'Save', 'Bookmark', or 'Saved' buttons.
    Returns: 'APPLIED', 'EXTERNAL', 'ALREADY_APPLIED', or 'NOT_FOUND'
    """
    time.sleep(2)

    # 1. Check if already applied
    for ind in job_tab.locator(
        "button:has-text('Already Applied'), div:has-text('Already Applied'), "
        "span:has-text('Already Applied'), button:has-text('Applied')"
    ).all():
        try:
            if ind.is_visible() and ind.inner_text().strip().lower() in ["already applied", "applied"]:
                return "ALREADY_APPLIED"
        except Exception:
            pass

    # 2. Locate the genuine Apply button
    # Strict filtering: Must NOT contain 'save' or 'bookmark'
    target_btn = None
    all_buttons = job_tab.locator("button, a").all()
    for btn in all_buttons:
        try:
            if not btn.is_visible():
                continue
            text = btn.inner_text().strip().lower()

            # Ignore Save / Bookmark buttons completely
            if "save" in text or "bookmark" in text:
                continue

            if "already applied" in text or text == "applied":
                return "ALREADY_APPLIED"

            if "company site" in text or "employer site" in text:
                return "EXTERNAL"

            # Check for genuine apply text
            if text in ["apply", "apply now", "easy apply", "quick apply", "apply on naukri"]:
                target_btn = btn
                break
            elif "apply" in text and len(text) < 25:
                target_btn = btn
                break
        except Exception:
            continue

    if not target_btn:
        # Check if only an external apply button exists
        for ext in job_tab.locator("button:has-text('company site'), a:has-text('company site')").all():
            try:
                if ext.is_visible():
                    return "EXTERNAL"
            except Exception:
                pass
        return "NOT_FOUND"

    # Click the genuine apply button
    target_btn.click()
    time.sleep(2)

    # 3. Handle post-click modals (e.g. 'Apply without updating resume', 'Submit', etc.)
    for confirm_sel in [
        "button:has-text('Apply without updating')",
        "button:has-text('Submit')",
        "button:has-text('Confirm')",
        "button:has-text('Done')",
        "button:has-text('Save & Apply')"
    ]:
        try:
            c = job_tab.locator(confirm_sel).first
            if c.is_visible(timeout=1500):
                c.click()
                time.sleep(1.5)
                break
        except Exception:
            pass

    return "APPLIED"

def search_and_apply_jobs(page, config):
    """Searches flexibly for any mobile development jobs (Android, iOS, Flutter) between 8-20 years experience and applies up to target count."""
    applied_count = 0
    max_apps = config.get("max_applications_per_run", 50)
    max_pages = config.get("max_pages_per_keyword", 5)
    keywords = config.get("keywords", [
        "Android", "iOS", "Flutter", "Mobile Developer", "Mobile Engineer",
        "Android Developer", "iOS Developer", "Flutter Developer",
        "Mobile Lead", "Mobile Architect"
    ])
    exp_min = config.get("experience_min_years", 8)
    exp_max = config.get("experience_max_years", 20)

    applied_jobs_file = Path(__file__).parent / "applied_jobs.json"
    applied_history = set()
    if applied_jobs_file.exists():
        try:
            with open(applied_jobs_file, "r", encoding="utf-8") as f:
                applied_history = set(json.load(f))
        except Exception:
            applied_history = set()

    card_selectors = "div.cust-job-tuple, div.srp-jobtuple-wrapper, div[data-job-id], article.jobTuple, div[class*='styles_job-listing']"

    for keyword in keywords:
        if applied_count >= max_apps:
            break

        slug = keyword.lower().replace(" ", "-")
        encoded_k = urllib.parse.quote(keyword)

        for page_num in range(1, max_pages + 1):
            if applied_count >= max_apps:
                break

            if page_num == 1:
                search_url = f"https://www.naukri.com/{slug}-jobs?k={encoded_k}&experience={exp_min}"
            else:
                search_url = f"https://www.naukri.com/{slug}-jobs-{page_num}?k={encoded_k}&experience={exp_min}"

            log(f"Searching (Page {page_num}): {search_url}")

            try:
                page.goto(search_url, wait_until="domcontentloaded")

                # Wait and scroll to trigger client-side rendering of job cards
                try:
                    page.wait_for_selector("div.srp-jobtuple-wrapper, div.cust-job-tuple, div[data-job-id]", timeout=6000)
                except Exception:
                    pass

                for _ in range(3):
                    page.mouse.wheel(0, 700)
                    time.sleep(0.5)

                job_tuples = page.locator("div.srp-jobtuple-wrapper, div.cust-job-tuple, div[data-job-id]").all()
                log(f"Found {len(job_tuples)} listings on Page {page_num} for '{keyword}' ({exp_min}+ Yrs)")

                if not job_tuples:
                    break

                for card in job_tuples:
                    if applied_count >= max_apps:
                        break
                    try:
                        title_elem = card.locator("a.title, a[class*='title'], a[title]").first
                        if not title_elem.is_visible():
                            continue
                        job_title = title_elem.inner_text().strip()
                        job_link = title_elem.get_attribute("href")
                        if not job_link:
                            continue
                        if not job_link.startswith("http"):
                            job_link = f"https://www.naukri.com{job_link}"

                        if job_link in applied_history:
                            continue

                        comp_elem = card.locator("a.comp-name, a[class*='comp-name']").first
                        company = comp_elem.inner_text().strip() if comp_elem.is_visible() else "Company"

                        loc_elem = card.locator("span.loc-wrap, span.locWdth, span[class*='loc']").first
                        location = loc_elem.inner_text().strip() if loc_elem.is_visible() else "Location N/A"

                        exp_elem = card.locator("span.exp-wrap, span.exp, span[class*='exp']").first
                        experience = exp_elem.inner_text().strip() if exp_elem.is_visible() else f"{exp_min}-{exp_max} Yrs"

                        # Open job detail page in a separate tab to apply safely
                        job_tab = page.context.new_page()
                        try:
                            job_tab.goto(job_link, wait_until="domcontentloaded", timeout=20000)
                            status = find_and_click_apply_button(job_tab)

                            if status == "APPLIED":
                                applied_count += 1
                                applied_history.add(job_link)
                                log(f"[APPLIED #{applied_count}/{max_apps}] {job_title} at {company} ({location} | {experience}) | {job_link}")
                            elif status == "EXTERNAL":
                                log(f"[External Portal] {job_title} at {company} ({location} | {experience}) | {job_link}")
                            elif status == "ALREADY_APPLIED":
                                log(f"[Already Applied] {job_title} at {company} ({location} | {experience}) | {job_link}")
                                applied_history.add(job_link)
                            else:
                                log(f"[Job Match] {job_title} at {company} ({location} | {experience}) | {job_link}")
                        except Exception as tab_err:
                            log(f"Notice inspecting {job_title}: {str(tab_err)}")
                        finally:
                            job_tab.close()
                            time.sleep(0.5)

                    except Exception as card_err:
                        continue

            except Exception as e:
                log(f"Error searching for {keyword} (Page {page_num}): {str(e)}")

    # Persist applied history to prevent re-applying in future runs
    try:
        with open(applied_jobs_file, "w", encoding="utf-8") as f:
            json.dump(list(applied_history), f, indent=2)
    except Exception as e:
        log(f"Notice saving applied history: {e}")

    log(f"Finished job scan. Total jobs applied this run: {applied_count}")
    return applied_count

def run_daily_automation():
    """Main daily routine: refreshes profile and searches/applies for jobs."""
    from playwright.sync_api import sync_playwright

    config = load_config()
    log("==================================================")
    log("Starting Daily Naukri Profile & Job Automation Run")
    log("==================================================")

    if not USER_DATA_DIR.exists():
        log("ERROR: No saved session found. Please run login setup first: python naukri_automator.py --login")
        return

    with sync_playwright() as p:
        try:
            browser_context = p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=config.get("headless", False),
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized"
                ],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()

            # 1. Verify Active Session / Interactive Login
            if not ensure_logged_in(page):
                log("Automation stopped: User must log into Naukri account to apply for jobs.")
                browser_context.close()
                return

            try:
                browser_context.storage_state(path=str(USER_DATA_DIR / "storage_state.json"))
            except Exception:
                pass

            # 2. Profile Freshening
            if config.get("refresh_profile_daily", True):
                refresh_resume_headline(page)

            # 3. Search & Apply
            if config.get("auto_apply_easy_apply", True):
                search_and_apply_jobs(page, config)

            browser_context.close()
            log("Daily automation completed successfully.")
        except Exception as e:
            log(f"Error during daily automation execution: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Naukri Automation Tool")
    parser.add_argument("--login", action="store_true", help="Launch interactive browser for initial login")
    parser.add_argument("--refresh", action="store_true", help="Refresh profile headline only")
    parser.add_argument("--daily", action="store_true", help="Run full daily routine (profile refresh + job apply)")

    args = parser.parse_args()

    if args.login:
        run_login()
    elif args.daily or args.refresh:
        run_daily_automation()
    else:
        # Default to daily if no args provided
        run_daily_automation()

if __name__ == "__main__":
    main()

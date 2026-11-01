# 🚀 Naukri Profile Freshener & Job Automator

An automated Python and Playwright tool designed to keep your Naukri profile active for recruiters and apply to matching mobile engineering positions (Android, iOS, Flutter, Cross-Platform) automatically.

---

## 🌟 Key Features

1. **Daily Profile Freshener ("Last Active" Booster)**:
   - Naukri recruiter search algorithms heavily prioritize candidates whose profiles show as **"Updated Today"**.
   - The script slightly toggles your resume headline (e.g., adding/removing a trailing period), refreshing your "Last Active" timestamp without altering your content.
   - Increases inbound recruiter visibility and search appearances by 3–5x.

2. **Smart Job Search & Auto-Apply**:
   - Searches flexible keywords across Android, iOS, Flutter, Mobile Lead, Architect, and Engineer roles.
   - Configurable experience filtering (e.g., 8–20 years).
   - Targeted locations: Bengaluru, Hyderabad, Pune, and Remote.
   - Multi-page scanning (Pages 1–5) to discover hundreds of live openings.
   - **Strict Apply Button Detection**: Distinguishes between direct portal "Apply" and "Save Job" buttons to ensure applications are actually submitted rather than just bookmarked.
   - Automatically handles post-click confirmation modals (e.g., *"Apply without updating resume"*).
   - Skips external portal redirects ("Apply on company site") to prioritize direct 1-click applications.

3. **Persistent Authenticated Session**:
   - Uses Playwright's persistent browser context (`user_data/`).
   - You only need to log in and verify OTP once; your authenticated session is preserved across runs.

4. **Duplicate Prevention**:
   - Stores submitted application links in `applied_jobs.json` to ensure you never re-apply to the same opening across daily runs.

---

## 📂 Project Structure

```text
naukri-job-automation/
├── naukri_automator.py      # Core automation logic (Playwright engine)
├── run_daily.ps1            # Daily runner script (PowerShell)
├── login.ps1                # One-time login launcher (PowerShell)
├── config.json              # Active user configuration
├── config.example.json      # Template configuration file
├── requirements.txt         # Python dependencies
├── .gitignore               # Excludes sensitive sessions and logs
└── README.md                # Documentation and setup guide
```

---

## 🛠️ Prerequisites & Installation

1. **Python 3.10+**:
   Ensure Python is installed and added to your system `PATH`.

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/naukri-job-automation.git
   cd naukri-job-automation
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

---

## ⚙️ Configuration (`config.json`)

Customize your search filters and application limits in `config.json`:

```json
{
  "keywords": [
    "Android",
    "iOS",
    "Flutter",
    "Mobile Developer",
    "Mobile Engineer",
    "Android Developer",
    "iOS Developer",
    "Flutter Developer",
    "Mobile Lead",
    "Mobile Architect",
    "React Native Mobile"
  ],
  "locations": [
    "Bengaluru",
    "Hyderabad",
    "Pune",
    "Remote"
  ],
  "experience_min_years": 8,
  "experience_max_years": 20,
  "refresh_profile_daily": true,
  "auto_apply_easy_apply": true,
  "max_applications_per_run": 50,
  "max_pages_per_keyword": 5,
  "browser_user_data_dir": "user_data",
  "headless": false
}
```

> **Note on `headless`**: Naukri employs anti-bot protection (Cloudflare/PerimeterX). Running with `"headless": false` is recommended to ensure proper rendering and avoid anti-bot blocks.

---

## 🚀 Usage

### 1. Daily Routine (Profile Refresh + Job Apply)

Run the PowerShell script:
```powershell
powershell -ExecutionPolicy Bypass -File ./run_daily.ps1
```
Or directly with Python:
```bash
python naukri_automator.py --daily
```

- If you are not logged in, a Chrome window will open prompting you for your credentials/OTP. Once you log in, press **`Enter`** in the terminal or let the script auto-detect the redirect to proceed.
- Once authenticated, it refreshes your resume headline and submits applications up to your `max_applications_per_run` target (e.g. 50).

### 2. Standalone Profile Refresh Only

To refresh your profile without applying for jobs:
```bash
python naukri_automator.py --refresh
```

---

## 🔒 Security & Privacy

- **Session Data**: The `.gitignore` file strictly excludes `user_data/` and `storage_state.json`. Your credentials, cookies, and tokens are stored locally and will **never** be committed to GitHub.
- **Application History**: `last_run.log` and `applied_jobs.json` are also ignored to protect your application history.

---

## 📜 License

This project is for personal use and educational automation purposes. Ensure compliance with Naukri's Terms of Service when using automated tools.

# Email Campaign Manager (Safe Sender)

Desktop email automation tool focused on **safe sending**:
- Random throttling between sends
- Daily volume limits and schedule windows
- Per-recipient history so no address is emailed twice
- Simple dark-mode GUI using CustomTkinter

---

## 1. Features

- **CustomTkinter GUI**
  - Tabs for Settings, Templates, and Run Campaign
  - Real-time log console
  - File picker for input CSV

- **Safe Sending Controls**
  - Daily email limit with automatic per-day reset
  - Active days of the week (Mon–Sun)
  - Time-window sessions (e.g. `09:00-12:00, 14:00-17:00`)
  - Random delay 30–90 seconds between emails

- **Template Management**
  - Three configurable templates
  - Subject + body per template
  - `{Name}` and `{Email}` placeholder substitution
  - Random template selection per recipient

- **Persistence & Logging**
  - [Sent_Emails.csv](cci:7://file:///d:/Projects/MASRICO/EmailsAutomation/Sent_Emails.csv:0:0-0:0) – success log and de-duplication source
  - [Failed_Emails.csv](cci:7://file:///d:/Projects/MASRICO/EmailsAutomation/Failed_Emails.csv:0:0-0:0) – failed attempts with error message
  - `config.json` – saved configuration and runtime counters

---

## 2. Project Structure

```text
EmailsAutomation/
├─ main.py                  # Entrypoint (launches GUI)
├─ ui_manager.py            # CustomTkinter app, threading, main loop
├─ config_manager.py        # Load/save config.json and daily counter
├─ data_handler.py          # CSV loading, filtering, success/failure logs
├─ scheduler.py             # Daily limits, active days, sessions, throttling
├─ email_engine.py          # SMTP / TLS sending and template rendering
├─ clients.csv              # Example input CSV (Name,Email)
├─ Docs/
│  ├─ Architecture Design.md
│  └─ SRS.md
├─ Sent_Emails.csv          # Runtime output (success log) – do NOT commit
├─ Failed_Emails.csv        # Runtime output (failure log) – do NOT commit
├─ config.json              # Runtime config – usually not committed
└─ .gitignore               # Git ignore rules
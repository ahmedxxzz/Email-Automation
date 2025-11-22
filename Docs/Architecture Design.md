# Architecture Design Document
**Project:** Email Campaign Manager (ECM)
**Version:** 1.0
**Date:** November 23, 2025
**Architect:** Senior Python Software Architect

---

## 1. High-Level Modular Diagram and Explanation

The ECM follows a **Service-Oriented Architecture (SOA)** pattern adapted for a desktop environment. It decouples the User Interface (View) from the Business Logic (Controller) and the Low-Level Operations (Services). This ensures that the GUI remains responsive while the email loop runs in a background thread.

### System Diagram (Abstract)

```mermaid
graph TD
    subgraph "Presentation Layer"
        GUI[CustomTkinter GUI]
        Logger[Status & Log Display]
    end

    subgraph "Orchestration Layer"
        Controller[Campaign Controller (Threaded Loop)]
    end

    subgraph "Service Layer"
        Data[Data Persistence Module]
        Sched[Scheduler & Limit Module]
        Mail[Email Sender Module]
    end

    %% Flows
    GUI -->|1. User Config & Start| Controller
    Controller -->|2. Request Filtered Data| Data
    Data -->|3. Return (Input - Sent History)| Controller
    
    Controller -->|4. Check Time & Limits| Sched
    Sched --o|5. Throttling (Sleep 30-90s)| Controller
    
    Controller -->|6. Send Request (App Pass)| Mail
    Mail -->|7. Success/Fail Signal| Controller
    
    Controller -->|8. Log Result| Data
    Controller -->|9. Update Status| Logger
```

### Core Logic Flow
1.  **Initialization:** The **GUI** loads settings and validates the App Password.
2.  **Data Preparation:** The **Controller** invokes the **Data Persistence Module** to load recipients and immediately filter out anyone found in `Sent_Emails.csv`.
3.  **The Loop (Threaded):**
    *   **Check Phase:** The **Scheduler Module** verifies if the current time matches the user-defined Session and if the Daily Limit has not been reached.
    *   **Send Phase:** If checks pass, the **Email Sender Module** picks a random template, personalizes it, and attempts SMTP transmission.
    *   **Log Phase:** Results are written back via the **Data Persistence Module**.
    *   **Throttle Phase:** The **Scheduler Module** pauses execution for a random interval (30-90s).
    *   **Error Handling:** If the Email Sender raises a critical exception, the Controller breaks the loop immediately.

---

## 2. Module Design and Responsibility (Deep Dive)

### A. GUI Module (Custom Tkinter)
**Module Name:** `ui_manager.py`
**Responsibility:** Provides a modern, dark-mode interface for configuration and real-time monitoring. It must explicitly handle threading to ensure the application window does not "freeze" during the sleep cycles.

*   **Key Functions:**
    *   `__init__(self, root)`: Initializes the CustomTkinter window, tabs (Settings, Templates, Run), and layout.
    *   `handle_csv_upload()`: Opens a file dialog, validates columns (`Name`, `Email`), and passes the file path to the Controller.
    *   `save_configuration()`: Collects inputs (Sessions, Limits, Templates, App Password) and saves them to a local `config.json`.
    *   `update_log_display(message, status)`: A thread-safe method to append text to the GUI console window (e.g., "Sent to [email] at 10:00 AM").

### B. Data Persistence & Filtering Module
**Module Name:** `data_handler.py`
**Responsibility:** Ensures data integrity. It creates the "Safe List" by subtracting the sending history from the input list.

*   **Key Functions:**
    *   `load_recipients(input_csv_path) -> List[Dict]`: Reads the raw input file.
    *   `get_sent_history() -> Set[String]`: Reads `Sent_Emails.csv` and returns a **Set** of email addresses (Sets provide O(1) lookup speed for de-duplication).
    *   `filter_recipients(raw_list, sent_history) -> List[Dict]`:
        *   Iterates through `raw_list`.
        *   **Logic:** `if email not in sent_history: keep`.
        *   Returns the final list of targets.
    *   `log_success(data: Dict)`: Appends a row to `Sent_Emails.csv`.
    *   `log_failure(data: Dict, error_msg: str)`: Appends a row to `Failed_Emails.csv`.

### C. Core Scheduler & Limit Manager Module
**Module Name:** `scheduler.py`
**Responsibility:** The "Gatekeeper" of the application. It manages time, enforces limits, and handles the mandatory random delays.

*   **Key Functions:**
    *   `check_daily_limit(current_count, max_limit) -> Bool`: Checks if `current_count` < `max_limit`.
    *   `check_session_window(active_days, sessions) -> Bool`:
        *   Checks if `Today` is in `active_days`.
        *   Checks if `Current_Time` falls within any of the defined `start_time` and `end_time` tuples.
        *   Returns `True` only if both pass.
    *   `manage_daily_reset()`: Checks a local state file. If the last run date != today, resets the internal `daily_sent_count` to 0.
    *   `perform_throttle()`:
        *   **Logic:** `time.sleep(random.uniform(30, 90))`
        *   Blocking call (executed in the worker thread, not the GUI thread).

### D. Email Sender & Error Handling Module
**Module Name:** `email_engine.py`
**Responsibility:** Handles the technical SMTP protocol, template rendering, and critical error reporting.

*   **Key Functions:**
    *   `connect_smtp(user_email, app_password)`: Establishes an SSL connection to the provider (e.g., `smtp.gmail.com`).
    *   `render_template(template_data, recipient_data) -> tuple`:
        *   Selects one of 3 templates randomly.
        *   Performs string substitution: `body.replace("{Name}", recipient_name)`.
        *   Returns `(subject, body)`.
    *   `send_single_email(recipient, template_pool, session_obj)`:
        *   **Try:** Connect -> Render -> Send -> **Return Success**.
        *   **Except (SMTPException, ConnectionError):**
            *   **Catch:** Specific server errors.
            *   **Raise:** `CriticalConnectionError`. This signal tells the Controller to trigger the "Stop on Error" rule.

---

## 3. Data Schema Definition

The application relies on strictly structured CSV files to maintain state and history.

### 1. Input Data CSV
*   **Source:** User uploaded.
*   **Purpose:** Raw list of potential targets.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **Name** | String | The recipient's name (used for `{Name}` variable). |
| **Email** | String | The destination address (used for unique ID). |
| *Other* | *Mixed* | Any extra columns are ignored. |

### 2. Sent_Emails.csv (Success Log)
*   **Source:** Generated/Appended by System.
*   **Purpose:** Persistent history to prevent double-sending (De-duplication).

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **Email** | String | **Primary Key** for filtering logic. |
| **Name** | String | Name associated with the email. |
| **Timestamp** | DateTime | Date and time the email was successfully sent. |
| **Template_ID** | Integer | ID (1, 2, or 3) of the template used (for auditing). |

### 3. Failed_Emails.csv (Failure Log)
*   **Source:** Generated/Appended by System.
*   **Purpose:** Record of addresses that failed, allowing for manual review or retry later.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **Email** | String | The address that failed. |
| **Name** | String | The recipient name. |
| **Timestamp** | DateTime | Time of failure. |
| **Error_Code** | String | The specific error message returned by the server (e.g., "550 User not found", "535 Authentication failed"). |

---

### Security & Constraint Implementation Notes
1.  **App Password Security:** The App Password is passed from the GUI inputs directly to the `email_engine` in memory. It is **not** saved to the CSV logs. If saved to `config.json` for convenience, it should be optionally encrypted or left to the user's discretion (standard practice suggests asking for it per session for maximum security, but saving it is acceptable for desktop apps if the local machine is secure).
2.  **Random Delay Integration:** The `perform_throttle()` function is called **after** the `log_success` function in the main loop. This ensures that if the user stops the app during the sleep, the email is already recorded as sent.
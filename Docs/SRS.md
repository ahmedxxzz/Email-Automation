# System Requirements Specification (SRS)
**Project:** Email Campaign Manager
**Version:** 1.0
**Date:** November 22, 2025

---

## 1. Project Overview

### 1.1 Description
The **Email Campaign Manager** is a desktop automation tool designed to facilitate the controlled distribution of bulk emails. Unlike standard bulk senders, this application emphasizes "safe sending" practices to prevent domain blacklisting. It features strictly regulated scheduling, random throttling, template variation, and persistent history logging to ensure no recipient is contacted twice.

### 1.2 Technology Stack
*   **Programming Language:** Python 3.x
*   **Graphical User Interface (GUI):** Custom Tkinter (`customtkinter`)
*   **Core Libraries:** `smtplib` (Email Protocol), `csv` (Data Handling), `datetime` (Scheduling), `random` (Throttling/Templates).

---

## 2. Functional Requirements (FR)

### FR 2.1: Data Management & Logging

1.  **Input Processing:**
    *   The system shall accept a user-uploaded **Input CSV file**.
    *   The system shall validate that the CSV contains at least two columns: `Name` and `Email`.
2.  **Success Logging:**
    *   The system shall maintain a persistent file named `Sent_Emails.csv`.
    *   Upon successfully sending an email, the system shall append the Recipient Email, Recipient Name, and Timestamp to `Sent_Emails.csv`.
3.  **Failure Logging:**
    *   The system shall maintain a persistent file named `Failed_Emails.csv`.
    *   Any email address that triggers a server rejection or connection error shall be appended to this file along with the specific Error Message.
4.  **De-duplication & Persistence:**
    *   **Pre-flight Check:** Before initiating any sending loop, the system must read the **Input CSV** and compare it against the `Sent_Emails.csv` history.
    *   **Exclusion Logic:** The system shall filter out any email address that appears in the `Sent_Emails.csv`. This ensures that a specific email address is never messaged twice, even if the associated name differs or the user re-uploads the same list.

### FR 2.2: Email Content & Personalization

1.  **Template Management:**
    *   The GUI shall provide **three (3) distinct input areas** (text boxes or file upload slots) for defining email templates.
    *   The user must be able to define a Subject Line and Body Text for each of the three templates.
2.  **Variable Substitution:**
    *   The system shall support dynamic string replacement for the variables `{Name}` and `{Email}` within the template body and subject line.
3.  **Randomized Template Selection:**
    *   For every individual email sent within the loop, the system shall **randomly select one** of the three provided templates.
4.  **Personalization:**
    *   The system shall inject the specific recipient's name into the selected template to vary the content hash, thereby reducing the likelihood of spam classification.

### FR 2.3: Operational Flow & Error Handling

1.  **Core Processing Loop:**
    *   The system shall iterate through the "To-Send" list (the result of the De-duplication process defined in FR 2.1).
2.  **Critical Stop-on-Error:**
    *   If the SMTP server returns a fatal error (e.g., Authentication Failed, Daily Limit Exceeded by Provider, Connection Refused) during the loop, the system shall **immediately terminate the process**.
    *   The loop must `break` instantly to prevent account suspension. The specific error shall be logged to `Failed_Emails.csv` before termination.

---

## 3. Non-Functional Requirements (NFR)

### NFR 3.1: Throttling and Volume Control

1.  **Mandatory Random Delay:**
    *   To mimic human behavior, the system shall enforce a **Random Sleep** interval between every successful email transmission.
    *   The duration of this sleep must be a random float value between **30 seconds and 90 seconds**.
2.  **Warm-up Protocol (User Guideline):**
    *   *Note:* While not a hard-coded limit, the user documentation shall emphasize starting with low volumes (15–20 emails/day) and gradually increasing the limit over weeks to warm up the sending IP.

### NFR 3.2: Scheduling and Limits

1.  **Daily Volume Limit:**
    *   The GUI shall allow the user to define a numeric `Daily Limit` (e.g., 50 emails per day).
    *   The system shall track the count of emails sent in the current 24-hour period.
    *   **Reset Logic:** The counter must automatically reset to 0 when the date changes.
2.  **Session Management:**
    *   The GUI shall allow the user to select specific **Days of the Week** (e.g., Mon, Wed, Fri) for operation.
    *   The GUI shall allow the user to define specific **Time Ranges/Sessions** (e.g., 09:00–12:00 and 14:00–17:00).
3.  **Execution Logic & Precedence:**
    *   The system shall only attempt to send an email if:
        1.  Current Day is in [Selected Days].
        2.  Current Time is within [Selected Session].
        3.  Daily Sent Count < [Daily Limit].
    *   **Session End:** If the current time exceeds the defined session (e.g., 12:01 PM), the system must pause operation until the next valid session.
    *   **Limit Reached:** If the `Daily Limit` is reached before the session ends, the system must stop sending for the remainder of the day.

---

## 4. Security & Technical Constraints

1.  **GUI Framework:**
    *   The application must be developed exclusively using **Custom Tkinter** for a modern, dark-mode compatible desktop interface.
2.  **Authentication Security:**
    *   The system shall connect to the email provider (e.g., Gmail) using SMTP SSL/TLS.
    *   **App Password Requirement:** The system must strictly require the use of an **App Password** generated via the provider's security settings. It must not support or store the user's primary account password.
    *   Credentials should be handled securely during the runtime session.
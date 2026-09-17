# AI-Powered Court Cause List Automation System

An automation system for retrieving advocate-wise cause-list information from the Andhra Pradesh High Court website, extracting structured case details, matching cases against the selected advocate/department, generating an Excel report, and delivering the report through email.

---

## 📌 Project Overview

Checking court cause lists manually can be repetitive and time-consuming, especially when the user needs to identify cases associated with a particular advocate or department.

The **AI-Powered Court Cause List Automation System** automates the repetitive parts of this workflow.

The system:

1. Opens the Andhra Pradesh High Court website.
2. Navigates to the Daily Cause List section.
3. Opens the Advocate Wise search.
4. Enters the required advocate/department name.
5. Pauses for the user to manually complete the CAPTCHA.
6. Waits for the cause-list results.
7. Extracts case information from the result table.
8. Matches cases against registered advocates.
9. Stores case information in the application database.
10. Generates an Excel report.
11. Sends the Excel report through email.
12. Records the execution and notification status through application logs.

---

## 🎯 Problem Statement

Court cause-list information is publicly available, but users may need to repeatedly visit the website, navigate through multiple pages, enter search information, inspect the resulting table, identify relevant cases, and manually prepare a report.

This project aims to reduce that repetitive work by automating the cause-list retrieval, extraction, matching, reporting, and notification workflow while keeping CAPTCHA verification as a human-in-the-loop step.

---

## 💡 Proposed Solution

The system combines browser automation, HTML parsing, database persistence, case matching, Excel report generation, scheduling, and email notification.

### High-Level Workflow

```text
User starts the application
          ↓
Scheduler
          ↓
Navigator Agent
          ↓
AP High Court Website
          ↓
Daily Cause List
          ↓
Advocate Wise
          ↓
Enter Advocate Name
          ↓
Manual CAPTCHA Verification
          ↓
Cause-List Result Table
          ↓
Extractor Agent
          ↓
Structured Case Data
          ↓
Matcher Agent
          ↓
Database
          ↓
Excel Report
          ↓
Notifier Agent
          ↓
Email Agent
          ↓
User receives Excel Report
```

---
# 🏗️ System Architecture

```text
                       ┌──────────────────────┐
                       │  AP High Court       │
                       │      Website         │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   NavigatorAgent     │
                       │     Playwright       │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ Manual CAPTCHA       │
                       │ Verification         │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   ExtractorAgent     │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │    MatcherAgent      │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │      Database        │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │     ExcelAgent       │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │    NotifierAgent     │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │      EmailAgent      │
                       └──────────┬───────────┘
                                  │
                                  ▼
                              📧 Email
```

---


# 🛠️ Technology Stack

| Technology               | Purpose                         |
| ------------------------ | ------------------------------- |
| Python                   | Main programming language       |
| FastAPI                  | Application/API layer           |
| Uvicorn                  | ASGI server                     |
| Playwright               | Browser automation              |
| BeautifulSoup            | HTML parsing                    |
| SQLAlchemy               | Database ORM                    |
| Alembic                  | Database migrations             |
| Pydantic                 | Data validation                 |
| APScheduler              | Local scheduled execution       |
| OpenPyXL / Excel library | Excel report generation         |
| SMTP                     | Email delivery                  |
| SQLite                   | Local development database      |
| PostgreSQL               | Recommended production database |
| Pytest                   | Testing                         |

---
The actual `.env` file must be excluded using `.gitignore`

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd court_cause_list
```

## 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Playwright browser

```bash
playwright install chromium
```
---

## 5. Create environment configuration

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the required local values.

Do not commit `.env`.

---

# ▶️ Running the Application

Start the application using:

```bash
python run.py
```

The application starts the configured scheduler and application server.

During cause-list processing, a browser window will open.

The user must:

1. Enter the CAPTCHA manually.
2. Submit the cause-list search.
3. Allow the application to detect the resulting table.

The application then continues with extraction, matching, report generation, and email notification.

---

# 🧪 Testing

The Navigator Agent can be tested independently before running the complete application.

Example:

```bash
python test_navigator.py
```

The complete workflow can then be tested through:

```bash
python run.py
```

Testing should verify:

* Website navigation
* CAPTCHA interaction
* Result-table detection
* Case extraction
* Advocate matching
* Database persistence
* Excel generation
* Email delivery
* Error handling
* Logging

---

# 📧 Email Workflow

The email notification workflow is:

```text
Cause-list results
       ↓
Case extraction
       ↓
Excel report
       ↓
EmailAgent
       ↓
SMTP server
       ↓
Recipient
```

The email provides the user with the generated Excel report without requiring the user to manually locate the generated file on the application machine.

---

# 🔄 Current Workflow

The current local workflow is:

```text
Scheduler
   ↓
Orchestrator
   ↓
Navigator
   ↓
Manual CAPTCHA
   ↓
Cause-list table
   ↓
Extractor
   ↓
Matcher
   ↓
Excel Generator
   ↓
Email Agent
   ↓
Report delivered
```
---

# 📌 Future Enhancements

Possible future improvements include:

### 1. Production PostgreSQL

Replace local SQLite with PostgreSQL.

### 2. Web Dashboard

Provide a dashboard for:

* Registered advocates
* Previous runs
* Extracted cases
* Notification history
* Processing status

### 3. Better Notification Tracking

Maintain:

```text
Case
 +
Advocate
 +
Notification Status
 +
Notification Timestamp
```

to prevent duplicate notifications.

### 4. Cloud Scheduling

Use a deployment scheduler/cron mechanism for unattended scheduled jobs where the workflow is compatible with the deployment environment.

### 5. Case Details

A future enhancement could retrieve additional case-detail information when required.

### 6. Report Storage

Future versions could store reports in external object storage rather than relying on local filesystem storage.

---
# 🎓 Project Significance

This project demonstrates an end-to-end automation pipeline combining:

* Browser automation
* Web data extraction
* Data validation
* Database persistence
* Entity matching
* Report generation
* Email notification
* Scheduling
* Logging
* Modular software architecture

Rather than simply scraping a webpage, the project demonstrates how a real-world repetitive information workflow can be converted into a structured software system.

---

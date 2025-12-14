# Nexora Platform – Landing Page, Audit Workflow & Automations

Welcome to the **Nexora** project.  This repository contains everything you need to run a compelling marketing site for local service businesses and a suite of automations designed to streamline day‑to‑day operations.  Out of the box you get a beautifully crafted landing page, a self‑service business audit, five ready‑to‑customise automations, a lightweight Node.js server, a logging system and test runners to ensure quality.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Running the Server](#running-the-server)
5. [Automations](#automations)
6. [Testing](#testing)
7. [Google Workspace Setup](#google-workspace-setup)
8. [Deployment](#deployment)

## Project Structure

```
nexora/
├── automations/                # Five automations with implementations, docs and test reports
│   ├── estimate-generator/
│   ├── invoice-tracking/
│   ├── lead-capture/
│   ├── reputation-followup/
│   └── smart-booking/
├── data/                       # Generated at runtime for audit CSV and leads CSV
├── logs/                       # Generated at runtime with per‑automation logs
├── public/                     # Static front‑end files
│   ├── index.html              # Landing page
│   ├── audit.html              # Audit intake form
│   └── automation.html         # Dynamic automation detail page
├── utils/                      # Shared utilities (e.g., logger)
├── server.js                   # Lightweight HTTP server (no external dependencies)
├── run-tests.js                # Test runner for automations and global flow
├── .env.example                # Example environment variables
├── PROJECT_AUDIT.md            # Audit of pages, links, forms and automations
├── README.md                   # This file
├── GOOGLE_WORKSPACE_SETUP.md   # How to configure Google credentials
├── DEPLOYMENT.md               # Instructions for running in production
└── GLOBAL_TEST_REPORT.md       # Created by tests; global run results
```

## Prerequisites

* **Node.js** v14 or higher.  The server uses only built‑in Node modules so there is no need to install any dependencies from the network.
* **A Google Workspace** account (optional).  To enable real integrations with Sheets, Gmail and Calendar you will need a service account and API credentials.  See [Google Workspace Setup](#google-workspace-setup).

## Configuration

All configuration is supplied via environment variables defined in a `.env` file at the project root.  An example file, `.env.example`, is provided.  Copy it to `.env` and fill in your values.

Key variables include:

| Variable | Description |
| --- | --- |
| `CLIENT_NAME` | Your business name (used in messages). |
| `CLIENT_EMAIL` / `CLIENT_PHONE` | Contact information for internal use. |
| `GOOGLE_SERVICE_ACCOUNT_KEYFILE` | Path to your Google service account JSON file. |
| `LEADS_SHEET_ID` | Google Sheet ID where leads and audit results will be stored. |
| `GMAIL_USER` / `GMAIL_PASS` | Credentials for sending notification emails.  Leave blank to disable email notifications. |
| `AUTOMATION_*_ENABLED` | Feature toggles for each automation.  Set to `false` to disable. |
| `PORT` | Port number on which the server will listen (default `3000`). |

**Note:** Never commit your `.env` file to version control.  Use `.env.example` as a template.

## Running the Server

Install Node.js and clone this repository.  Then from within the `nexora` directory:

```bash
cp .env.example .env    # customise your environment variables
node server.js         # start the HTTP server
```

The server listens on the port specified by `PORT` (default `3000`).  Visit `http://localhost:<PORT>/index.html` to see the landing page and `http://localhost:<PORT>/audit.html` for the audit form.  No external dependencies are required; everything runs using built‑in Node modules.

## Automations

Five automations live under the `automations/` folder:

| Automation | Folder | Description |
| --- | --- | --- |
| **Lead Capture & Auto‑Response** | `lead-capture` | Centralises incoming leads (web, phone, text) and sends an immediate acknowledgement.  Saves leads to a CSV file and logs each run. |
| **Smart Booking & Reminders** | `smart-booking` | Picks a slot from your availability (simulated) and prepares confirmation/reminder messages.  Replace the slot selection with real calendar logic to integrate with Google Calendar. |
| **Quick Estimate Generator** | `estimate-generator` | Calculates a rough estimate using a simple formula.  Extend this with your pricing rules or integrate with spreadsheets/docs for full quotes. |
| **Review & Reputation Follow‑Up** | `reputation-followup` | Creates a personalised review request using your Google review link.  Ideal for sending via email or SMS. |
| **Invoice Tracking & Reminders** | `invoice-tracking` | Generates a random invoice ID and amount, and schedules reminders for outstanding payments.  Integrate with your invoicing software for production use. |

Each automation exports an async function in its `index.js` and reads configuration from environment variables.  Automations write logs to `logs/<automation>/` and return an object with `status`, `name` and `message` fields.  The server exposes these functions via `/api/automation/<name>`.

To add new automations:

1. Create a folder under `automations/` with an `index.js` that exports an async function.
2. Add the folder name to the `automations` mapping in `server.js`.
3. Create a card on the landing page and a description in `automation.html`.

## Testing

A test runner (`run-tests.js`) is provided to validate individual automations and the global flow.

### Running automation tests

To run five consecutive test runs of a specific automation:

```bash
node run-tests.js --automation lead-capture
```

The runner writes a report to `automations/lead-capture/TEST_REPORT.md` containing the outputs of each run and whether the sequence succeeded.  Repeat for other automation names: `smart-booking`, `estimate-generator`, `reputation-followup`, `invoice-tracking`.

To run tests for **all** automations:

```bash
node run-tests.js --all
```

### Running global tests

To simulate a complete customer journey – submitting the audit form, storing results and running recommended automations – run:

```bash
node run-tests.js --global
```

The script will spin up the server, perform three audit submissions, check that `data/audit_results.csv` grows by one row each time, run the recommended automations and write the outcomes to `GLOBAL_TEST_REPORT.md`.

## Google Workspace Setup

Real integrations with Google Sheets, Gmail and Calendar require a service account and OAuth configuration.  Please see `GOOGLE_WORKSPACE_SETUP.md` for step‑by‑step instructions on how to create credentials, share resources with the service account, and configure environment variables.  In the sandbox environment these integrations are simulated via local CSV files and log messages.

## Deployment

This project can run anywhere Node.js is available.  For production deployment:

1. Copy the repository to your server.
2. Create a `.env` file based on `.env.example` and set your secrets.
3. Start the server with `node server.js` (or using a process manager like `pm2`).
4. Ensure port 80/443 traffic is proxied to the Node process (via Nginx or your hosting provider).
5. Configure HTTPS and domain names as appropriate.

See `DEPLOYMENT.md` for more detailed guidance on production, environment variables and troubleshooting.

## License

This project is provided without a formal licence for demonstration purposes.  You are free to adapt and reuse the code within your own projects.
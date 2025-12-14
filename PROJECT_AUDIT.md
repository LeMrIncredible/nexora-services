# Project Audit

This document captures the current state of the Nexora project as of the initial unpack and serves as a checklist for completion.  It identifies all existing pages, navigation items, buttons, forms, and automations, and notes any missing pieces or work left to do.  It will evolve as you make changes.

## 1. Pages and Routes

| Page/Route | Purpose | Notes |
| --- | --- | --- |
| `/index.html` (Home) | Main landing page.  Introduces Nexora and the core value proposition for local service businesses.  Includes sections: Hero, Reality (problem), Automations overview, Websites overview, How We Help, Final Call‑to‑Action and Footer. | No pricing displayed.  All CTA buttons should link to the audit form, demo video or external booking link. |
| `/audit.html` | Free audit intake form.  Collects details about the prospective client’s business and returns a list of recommended automations.  After submission the form results are displayed below. | Needs to save submissions to a persistent store (Google Sheets) and email a notification.  Currently only returns recommendations in JSON without persistence. |
| `/automation.html?name=<automation>` | **Missing**.  A detail page for each automation card that explains the automation’s purpose, pain points solved, required inputs, outputs produced, example workflow and integrations.  The plan is to generate this page dynamically based on a query parameter. |
| `/api/audit` | API endpoint (POST).  Accepts audit form data as JSON and returns a JSON list of recommended automation names. | Should store submissions in Google Sheets and send notifications.  Must log each submission. |
| `/api/automation/:name` | API endpoint (GET).  Invokes a specific automation handler defined under `automations/<name>/index.js` and returns its result. | Handlers are currently placeholders and need real implementations.  Should write structured logs for every invocation. |

## 2. Navigation, Links and Buttons

### Navigation bar

* **Home/Logo** – links to `/index.html`.
* **Automations** – in page anchor linking to `#automations` on the home page.
* **Websites** – in page anchor linking to `#websites` on the home page.
* **How We Help** – in page anchor linking to `#help` on the home page.
* **Free Audit** – navigation button linking to `/audit.html`.
* **Demo** – button that opens the demo video modal.

### CTA Buttons

* **Start Your Free Audit / Start Free Audit / Discover Your Stack** – link to `/audit.html`.
* **Watch Demo / Watch how we fix this / Demo** – open demo video modal.
* **Talk Through Your Systems** – links to a Calendly booking page (currently a placeholder).  Must be updated with a real link in production.
* **Automation Cards** – five cards under the “Your Toolset” section.  Each card has a `data‑automation` attribute and currently triggers an API call to `/api/automation/<name>` and displays an alert with the result.  In the completed version these should link to a detail page (`/automation.html?name=<id>`) and also support triggering a test run via the API.
* **Website Demo Previews** – clicking the preview cards currently navigates to `/audit.html`.  This is acceptable because there is no separate website portfolio yet.

### Audit Form

The audit intake form is located on `/audit.html` and contains the following fields:

* `name` – required text field for the user’s name.
* `businessName` – required text field for the business name.
* `email` – required email field.
* `phone` – optional phone number field.
* `serviceType` – select (Plumbing, Landscaping, HVAC, Electrical, Other).
* `city` – optional text field for the service area.
* `teamSize` – select (Just me, 2–4, 5–9, 10+).
* `leadSources` – text field for describing how leads contact the business.
* `tools` – text field for current tools used.
* `bottlenecks` – textarea for describing current bottlenecks.
* `followups` – textarea explaining how the business follows up on leads.
* `notes` – optional textarea for additional notes.

The submit button sends a POST request to `/api/audit` with the form data encoded as JSON.  The current server responds with a JSON payload containing recommended automations.  The results are rendered as a list below the form.

## 3. Automations

The `automations` directory contains five automation folders, each with an `index.js` file and a `README.md`.  These are currently placeholders and need full implementations:

| Automation folder | Purpose (as inferred) |
| --- | --- |
| `lead-capture` | Capture leads from multiple channels (web forms, phone/SMS, social) and send an immediate acknowledgment. |
| `smart-booking` | Provide clients with available time slots, create calendar events and send reminders to reduce no‑shows. |
| `estimate-generator` | Generate quick estimates based on job details submitted on the website. |
| `reputation-followup` | Send review requests after jobs are marked complete and follow up politely. |
| `invoice-tracking` | Generate invoices and send reminder emails/texts until payment is received. |

Each automation must:

1. **Read configuration from environment variables** (client name, contact details, Google credentials, etc.) via a single `.env` file.
2. **Perform its core task** with sensible defaults.  For example, lead capture should write a new row into a Google Sheet or local CSV and send an acknowledgement email.
3. **Log each run** to a dedicated folder under `./logs/<automation_name>/` with the start time, end time, duration, inputs, outputs, and any errors.
4. **Expose a single async function** in `index.js` that can be invoked via the API.
5. **Include a `README.md`** describing its purpose, configuration variables, and how to run or test it.
6. **Provide a `TEST_REPORT.md`** after testing the automation five times.

## 4. Missing Pieces & TODOs

* **Automation Detail Page** – a new page (`automation.html`) needs to be added.  It should read a query parameter to determine which automation to describe.  This page will serve as an informative landing page for each automation, with a link or button to trigger the test run via the API.
* **Logging** – there is currently no shared logging utility.  Create a reusable logging module (e.g., `utils/logger.js`) to write logs to the console and to timestamped files.
* **Environment Configuration** – there is no `.env` or `.env.example`.  Create both.  `.env` should be ignored by version control, `.env.example` should list all required configuration variables with defaults or placeholders.
* **Persistence of Audit Responses** – the audit endpoint currently only returns recommendations.  It must be updated to save submissions to persistent storage (Google Sheets or local file) and to send notification emails if configured.
* **Google Workspace Integration** – automations should interact with Google Sheets, Gmail, Calendar and Drive as appropriate.  Provide a `GOOGLE_WORKSPACE_SETUP.md` document explaining how to configure credentials and OAuth.
* **Testing** – implement test runners for each automation that execute the automation five times and produce a `TEST_REPORT.md`.  Also create a global test script and generate `GLOBAL_TEST_REPORT.md` after three full run‑throughs.
* **Deployment Instructions** – create `DEPLOYMENT.md` with detailed steps for installing dependencies, configuring environment variables, setting up Google credentials, running the server locally and in production, and troubleshooting.

# Google Workspace Setup

This document explains how to enable Nexora’s automations to interact with Google Sheets, Gmail, Calendar and Drive.  These steps are optional; the project will function with local CSV storage and console logging if you choose not to configure Google integrations.

## 1. Create a Google Cloud Project

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **APIs & Services → Dashboard** and enable the following APIs:
   - **Google Sheets API** (to store leads and audit results)
   - **Gmail API** (to send acknowledgement and notification emails)
   - **Google Calendar API** (for booking events and availability)
   - **Google Drive API** (optional for storing generated documents)

## 2. Create a Service Account

1. In the Cloud Console, go to **IAM & Admin → Service Accounts** and click **Create Service Account**.
2. Give it a name (e.g. `nexora-automation`) and click **Create**.
3. Grant it the **Project Editor** role (or a more restrictive role that covers the APIs you enabled).
4. Click **Done**.

### Download the Credentials

1. Find your newly created service account in the list, click its email, then **Keys → Add Key → Create new key**.
2. Choose **JSON** and click **Create**.  Save the downloaded JSON file securely and do not commit it to version control.
3. Set the path to this file in your `.env` as `GOOGLE_SERVICE_ACCOUNT_KEYFILE`.

## 3. Share Resources with the Service Account

Service accounts are separate “users” that need explicit permission to access your Google resources.

### Share a Google Sheet

1. Create a new Google Sheet where you want to store audit submissions and leads, e.g. `Nexora Leads`.
2. Click **Share** and add the service account’s email (found in your JSON file) with **Editor** access.
3. Copy the sheet’s ID from its URL (the long string between `/d/` and `/edit`) and set it as `LEADS_SHEET_ID` in your `.env`.

### Gmail (Sending Emails)

Service accounts cannot send emails directly via Gmail.  You have two options:

1. **Use SMTP with an App Password**:
   - Create a dedicated Gmail account for sending notifications.
   - Enable 2‑factor authentication on that account.
   - Generate an **App Password** via **Google Account → Security → App Passwords**.
   - Set `GMAIL_USER` to the Gmail address and `GMAIL_PASS` to the app password in `.env`.
2. **Use the Gmail API**: You can delegate domain‑wide authority to the service account and use it to send emails.  This requires Google Workspace (not consumer Gmail) and additional setup.  See Google’s documentation on [domain‑wide delegation](https://developers.google.com/admin-sdk/directory/v1/guides/delegation).

### Google Calendar

1. Share your primary calendar with the service account email.  In Google Calendar, click the three dots next to your calendar → **Settings and sharing** → **Share with specific people** → add the service account with **Make changes and manage sharing** permissions.
2. When integrating smart booking, use the Calendar API with your service account credentials to read busy times and create events.

## 4. Update `.env`

Your `.env` should contain entries such as:

```
GOOGLE_SERVICE_ACCOUNT_KEYFILE=/absolute/path/to/your/service-account.json
LEADS_SHEET_ID=your-google-sheet-id
GMAIL_USER=notifications@example.com
GMAIL_PASS=your-app-password
```

Make sure the service account file path is correct and that the sheet ID and email credentials match the resources you created.

## 5. Extend Automations

The sample automations in this project simulate their behaviour with local files and random values.  To connect them to Google services:

1. Use the [googleapis](https://www.npmjs.com/package/googleapis) package to authenticate with the service account using the JSON key.  Because the sandbox cannot install packages from NPM, you should install this dependency in your own environment.
2. For Google Sheets:
   - Use the Sheets API to append rows to `LEADS_SHEET_ID` for leads and audit submissions.
3. For Gmail:
   - Use nodemailer with SMTP (`GMAIL_USER`/`GMAIL_PASS`) or the Gmail API to send emails.
4. For Calendar:
   - Use the Calendar API to check availability and create events.

Remember to handle errors and rate limits gracefully and to log all external API interactions.  Keep your service account JSON file secure and do not expose it publicly.

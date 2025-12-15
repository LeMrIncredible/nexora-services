## Lead Capture & Auto‑Response

This automation centralises all of your incoming leads and acknowledges them immediately.  It is designed for service businesses that receive inquiries via multiple channels (web forms, phone calls, text messages or social media).  With this system in place you never miss an opportunity because everything flows into a single record and your potential customer gets a friendly confirmation right away.

### How it works

1. **Configuration** – Reads settings from environment variables (see `.env.example`).  The only required variable is `CLIENT_NAME`, used to personalise the acknowledgement message.  You can add variables for email servers or SMS gateways when integrating for real.
2. **Capture** – When the automation runs it generates a dummy lead (for demonstration).  In production you would pass the lead details as inputs from your web form or messaging gateway.
3. **Persist** – The lead is appended to `data/leads.csv` in the project root.  The file is created if it doesn’t already exist.  Consider replacing this with a call to Google Sheets or a CRM in the future.
4. **Acknowledgement** – Builds a personalised thank‑you message addressed to the lead and referencing your business name.  You could extend this by sending the message via Gmail or an SMS API.
5. **Logging** – Each invocation is recorded both to the console and to a timestamped log file under `logs/lead-capture/`.  Logs include the start and end time, duration, input summary, output summary and any error details.
6. **Return** – Returns an object with `status`, `name` and `message` fields.  This is consumed by the server when `/api/automation/lead-capture` is called.

### Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `CLIENT_NAME` | ✓ | Name of your business used in the acknowledgement message. |
| `AUTOMATION_LEAD_CAPTURE_ENABLED` | – | Set to `true` or `false` to enable or disable this automation. |

Optional variables for future extensions (email/SMS gateways) are documented in `.env.example`.

### Running

To run the automation manually (useful for development or testing):

```
node automations/lead-capture/index.js
```

Each run will write a new log file to `logs/lead-capture/` and print the result to the console.

### Testing

A test runner is provided at the project root.  Execute it with:

```
node run-tests.js --automation lead-capture
```

The runner will execute the automation five consecutive times.  If a run fails, it will restart the sequence.  After five successful runs it writes a `TEST_REPORT.md` to this folder summarising the test inputs (if any), outputs and log file paths.

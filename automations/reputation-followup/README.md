## Review & Reputation Follow‑Up

The Review & Reputation Follow‑Up automation makes it effortless to collect five‑star reviews from your happy customers.  Strong online reviews boost search rankings and trust, but many customers forget to leave them without a gentle nudge.

### How it works

1. **Configuration** – Reads your business name (`CLIENT_NAME`) from environment variables.  Define `REVIEW_LINK` in your `.env` to set your actual Google review URL.  If `REVIEW_LINK` is missing, a placeholder is used.
2. **Trigger** – In a real system this would be triggered when you mark a job complete.  The demo simply runs whenever the automation is invoked.
3. **Compose request** – Builds a personalised review request using the business name and review link.  You could extend this to send via Gmail or an SMS API.
4. **Logging** – Writes detailed logs to `logs/reputation-followup/` and prints to console.
5. **Return** – Returns an object containing the message sent.  The message can be delivered by the API server to the caller.

### Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `CLIENT_NAME` | ✓ | Name of your business used in the review request. |
| `REVIEW_LINK` | – | Your Google review link.  If omitted, a placeholder is used. |
| `AUTOMATION_REPUTATION_FOLLOWUP_ENABLED` | – | Enable or disable this automation. |

### Running

Run manually with:

```bash
node automations/reputation-followup/index.js
```

Logs will be created under `logs/reputation-followup/`.

### Testing

Use the test runner to execute five consecutive runs:

```bash
node run-tests.js --automation reputation-followup
```

The summary is written to `TEST_REPORT.md` in this folder.

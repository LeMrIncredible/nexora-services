## Invoice Tracking & Reminders

The Invoice Tracking & Reminders automation takes the awkwardness out of chasing unpaid invoices.  It generates invoices when jobs are completed and follows up at sensible intervals until payment arrives.

### How it works

1. **Configuration** – Reads `CLIENT_NAME` from the environment.  You can define billing settings such as default due dates or payment links in your own variables when extending this automation.
2. **Generate** – Creates a random invoice ID and amount due for demonstration.  In production you would pull job details and pricing from your order management system.
## Invoice Tracking & Reminders

The Invoice Tracking & Reminders automation takes the awkwardness out of chasing unpaid invoices.  It generates invoices when jobs are completed and follows up at sensible intervals until payment arrives.

### How it works

1. **Configuration** – Reads `CLIENT_NAME` from the environment.  You can define billing settings such as default due dates or payment links in your own variables when extending this automation.
2. **Generate** – Creates a random invoice ID and amount due for demonstration.  In production you would pull job details and pricing from your order management system.
3. **Notify** – Constructs a message indicating the invoice has been created and that reminders will be sent every three days until payment.  Extend this to integrate with your accounting software and send real emails or SMS messages.
4. **Logging** – Logs start/end times, duration and summary information to `logs/invoice-tracking/` and console.
5. **Return** – Returns an object summarising the invoice creation.

### Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `CLIENT_NAME` | ✓ | Name of your business used in messages. |
| `AUTOMATION_INVOICE_TRACKING_ENABLED` | – | Enable or disable this automation. |

You may also need additional variables for your accounting integration, payment links or reminder intervals.

### Running

Run manually with:

```bash
node automations/invoice-tracking/index.js
```

Logs will appear in `logs/invoice-tracking/`.  Replace the random invoice logic with real data when integrating.

### Testing

Invoke the test runner for five consecutive runs:

```bash
node run-tests.js --automation invoice-tracking
```

The results are stored in `TEST_REPORT.md` in this folder.
3. **Notify** – Constructs a message indicating the invoice has been created and that reminders will be sent every three days until payment.  Extend this to integrate with your accounting software and send real emails or SMS messages.
4. **Logging** – Logs start/end times, duration and summary information to `logs/invoice-tracking/` and console.
5. **Return** – Returns an object summarising the invoice creation.

### Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `CLIENT_NAME` | ✓ | Name of your business used in messages. |
| `AUTOMATION_INVOICE_TRACKING_ENABLED` | – | Enable or disable this automation. |

You may also need additional variables for your accounting integration, payment links or reminder intervals.

### Running

Run manually with:

```bash
node automations/invoice-tracking/index.js
```

Logs will appear in `logs/invoice-tracking/`.  Replace the random invoice logic with real data when integrating.

### Testing

Invoke the test runner for five consecutive runs:

```bash
node run-tests.js --automation invoice-tracking
```

The results are stored in `TEST_REPORT.md` in this folder.

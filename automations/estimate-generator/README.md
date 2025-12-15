## Quick Estimate Generator

The Quick Estimate Generator automation takes the pain out of quoting.  It accepts job details, applies your pricing logic and produces a professional estimate in seconds.  This not only saves hours of manual work but also delights your prospects with prompt responses.

### How it works

1. **Configuration** – Reads basic details like `CLIENT_NAME` from environment variables.  You can define additional variables for labour rates, materials mark‑ups or template file paths when extending this automation.
2. **Calculate** – This demo calculates a simple estimate by multiplying a base cost by a random labour multiplier.  Replace this with your actual pricing rules or integrate with a costing database.
3. **Draft** – Prepares a message summarising the estimated total and instructing you to review it.  A full implementation might generate a PDF or Google Doc and attach it to an email.
4. **Logging** – Logs the start and end times, duration, inputs and outputs to `logs/estimate-generator/` and to the console.
5. **Return** – Returns an object describing the estimate and success status.

### Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `CLIENT_NAME` | ✓ | Name of your business used in the estimate message. |
| `AUTOMATION_ESTIMATE_GENERATOR_ENABLED` | – | Enable or disable this automation. |

### Running

Run the automation manually with:

```bash
node automations/estimate-generator/index.js
```

Logs will appear in `logs/estimate-generator/`.  Replace the random estimate logic with your pricing to make this useful in production.

### Testing

Invoke the test runner with:

```bash
node run-tests.js --automation estimate-generator
```

The runner executes five consecutive runs and creates `TEST_REPORT.md` summarising the outcomes.

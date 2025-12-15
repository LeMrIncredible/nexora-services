# Smart Booking & Reminders

Automates booking and reminder flows so you never miss an appointment.

## How it works

1. When this automation is invoked, it picks an available slot within the next seven days at 10:00 AM.
2. It generates a friendly confirmation message including the chosen date and time.
3. It logs the run via `logAutomationRun`, recording the client name and scheduled date.
4. It returns the confirmation message to the caller.

## Configuration Variables

| Variable | Description |
|---------|-------------|
| `CLIENT_NAME` | Name of your business used in communications. |
| `AUTOMATION_SMART_BOOKING_ENABLED` | Set to `true` to enable this automation. |

## Running

Call the API endpoint `/api/automation/smart-booking` with a JSON body containing a `clientName` field, e.g. `{ "clientName": "Twice Precise Laser Co." }`. The automation will schedule a time, log the run, and return a success message.

## Testing

See `TEST_REPORT.md` for five sample runs and their outcomes. Each test should return a confirmation with a future date and time.

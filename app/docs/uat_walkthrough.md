# User Acceptance Testing (UAT) Walkthrough

This document describes the steps to validate that Nexora V1 meets the functional and non‑functional requirements outlined in the specification.

## 1. Role‑based access control

1. **Admin access:**
   - Log in as an admin user.
   - Verify that the **Admin Dashboard** is accessible and that the navigation bar displays admin‑specific options (Clients link).
2. **Client access:**
   - Log in as a client user associated with a specific client.
   - Confirm that the user is redirected to `/dashboard` (client dashboard) and sees client‑specific navigation links (Dashboard, Leads, Jobs, Logs, Settings).
   - Attempt to access `/admin` or `/admin/clients`.  The system should redirect to the login page with a message indicating insufficient permissions.

## 2. Multi‑tenant isolation

1. Create two clients (Client A and Client B) via the admin console.
2. Add one client user to each client.
3. Log in as Client A’s user and create a job and view leads.
4. Log in as Client B’s user and verify that Client A’s job and leads are not visible.
5. Attempt to manually access Client A’s pages by modifying the URL (e.g. `/jobs/1` if the job ID is 1).  The system should return a 404 error or redirect to the login page.

## 3. Automation enable/disable behavior

1. Navigate to a client’s detail page in the admin console.
2. Toggle the **Daily Digest** automation off.
3. Wait for the scheduled digest time (01:00 UTC) or trigger a manual scheduling by toggling it back on and verifying that an email is logged (check logs for “Daily digest sent”).
4. Toggle the automation on and off again and verify that the job scheduling updates accordingly (no duplicate jobs).  Inspect the scheduler using the `schedule_jobs` function or check application logs.

## 4. Dashboard layout persistence per client

1. Log in as a client user.
2. Navigate to **Settings** and hide the KPI cards and Activity Feed modules.
3. Return to the dashboard and confirm that the KPI and Activity Feed sections are no longer displayed.
4. Log out and log back in.  Verify that the layout preferences persist.
5. Log in as a user of another client and confirm that their dashboard layout is unaffected.

## 5. Public lead form abuse resistance (basic)

1. Access a client’s public lead form at `/lead/<client_slug>`.
2. Submit the form with valid data and verify that the lead is created and a notification email is logged.
3. Submit the form with missing required fields and verify that validation errors are displayed.
4. Attempt to submit malicious scripts or HTML in the form fields.  The system should escape inputs and store them safely (inputs are not rendered without sanitization).

## 6. Mobile usability

1. Resize the browser window or open the application on a mobile device emulator.
2. Verify that the navigation bar collapses into a hamburger menu and that pages remain readable and usable.
3. Submit forms and navigate between pages to ensure there are no layout issues on small screens.

## 7. Error visibility for admins

1. Force an error condition (e.g. intentionally break an automation function or supply invalid data that triggers an exception in a view).
2. Check the **Error logs** count on the Admin Dashboard and confirm that errors are recorded in `LogEntry` with `entry_type='error'`.
3. Review the error messages and timestamps in the **Logs** section of the affected client’s detail page.

## 8. Google Workspace connection status (stub)

1. Navigate to a client’s detail page.  Note that integration credentials are stubbed in V1 and not visible in the UI.
2. For V1.1, Google OAuth integration should be implemented.  See the roadmap in `docs/design.md` for more information.

## Conclusion

Once all tests pass without critical issues, Nexora V1 can be considered ready for launch.  Address any discovered bugs or usability problems before deployment.

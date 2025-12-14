#!/usr/bin/env node
/*
 * Test Runner for Nexora Automations and Global Flow
 *
 * This script can execute each automation multiple times to ensure
 * reliability and record the outcomes in a test report.  It can also
 * perform a global end‑to‑end test by spinning up the server, posting
 * audit submissions and verifying that rows are added to the audit CSV
 * and automations run successfully.
 *
 * Usage:
 *   node run-tests.js --automation lead-capture
 *   node run-tests.js --all
 *   node run-tests.js --global
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

// List of automation identifiers corresponding to folder names
const automationNames = ['lead-capture', 'smart-booking', 'estimate-generator', 'reputation-followup', 'invoice-tracking'];

/**
 * Run a single automation multiple times.  Generates a test report
 * summarising the inputs, outputs and log files for each run.  If any
 * invocation throws an error or returns a status of 'error', the
 * sequence stops and the report notes the failure.
 *
 * @param {string} name Automation folder name
 * @param {number} times Number of successful runs required (default 5)
 */
async function runAutomationTests(name, times = 5) {
  const automationPath = path.join(__dirname, 'automations', name, 'index.js');
  const reportPath = path.join(__dirname, 'automations', name, 'TEST_REPORT.md');
  const results = [];
  let successCount = 0;
  let attempt = 0;
  let failed = false;
  while (successCount < times && !failed) {
    attempt++;
    try {
      const automation = require(automationPath);
      const output = await automation();
      results.push({ attempt, status: output.status, output });
      if (output.status === 'success') {
        successCount++;
      } else {
        failed = true;
      }
    } catch (err) {
      results.push({ attempt, status: 'error', error: err.message });
      failed = true;
    }
  }
  // Write test report
  const lines = [];
  const dateStr = new Date().toISOString();
  const humanName = name
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
  lines.push(`# Test Report – ${humanName}`);
  lines.push('');
  lines.push(`Date: ${dateStr}`);
  lines.push('');
  results.forEach((res) => {
    lines.push(`### Run ${res.attempt}`);
    lines.push(`Status: ${res.status}`);
    if (res.output) {
      lines.push('Output:');
      lines.push('```json');
      lines.push(JSON.stringify(res.output, null, 2));
      lines.push('```');
    }
    if (res.error) {
      lines.push(`Error: ${res.error}`);
    }
    lines.push('');
  });
  lines.push('---');
  if (failed) {
    lines.push('**Result:** Failure. One or more runs did not return a success status.');
  } else {
    lines.push(`**Result:** Success. ${times} consecutive runs completed successfully.`);
  }
  // List the most recent log files (optional)
  const logDir = path.join(__dirname, 'logs', name);
  if (fs.existsSync(logDir)) {
    const logFiles = fs.readdirSync(logDir).sort().slice(-times);
    lines.push('');
    lines.push('Recent Log Files:');
    logFiles.forEach((file) => {
      lines.push(`- ${path.join('logs', name, file)}`);
    });
  }
  fs.writeFileSync(reportPath, lines.join('\n'), 'utf8');
  console.log(`Finished tests for ${name}. Report written to ${reportPath}`);
}

/**
 * Perform a global test by starting the server, submitting audit forms
 * and running recommended automations.  The audit CSV is inspected to
 * ensure rows are appended.  A summary report is written to
 * `GLOBAL_TEST_REPORT.md`.
 *
 * @param {number} times Number of times to perform the full flow (default 3)
 */
async function runGlobalTests(times = 3) {
  const reportPath = path.join(__dirname, 'GLOBAL_TEST_REPORT.md');
  const lines = [];
  const dateStr = new Date().toISOString();
  lines.push('# Global Test Report');
  lines.push('');
  lines.push(`Date: ${dateStr}`);
  lines.push('');
  // Spawn the server as a child process
  const serverProcess = spawn('node', ['server.js'], { cwd: __dirname, env: { ...process.env, PORT: process.env.PORT || '4000' } });
  const port = process.env.PORT || '4000';
  await new Promise((resolve) => setTimeout(resolve, 2000)); // wait for server to start
  for (let i = 1; i <= times; i++) {
    lines.push(`## Global Run ${i}`);
    try {
      // Read current number of rows in audit CSV
      const auditCsv = path.join(__dirname, 'data', 'audit_results.csv');
      let beforeLines = 0;
      if (fs.existsSync(auditCsv)) {
        beforeLines = fs.readFileSync(auditCsv, 'utf8').split(/\r?\n/).filter(Boolean).length;
      }
      // Submit an audit form via HTTP POST
      const auditPayload = {
        name: `Test User ${i}`,
        businessName: `Test Biz ${i}`,
        email: `test${i}@example.com`,
        phone: '',
        serviceType: 'Plumbing',
        city: 'Test City',
        teamSize: '2-4',
        leadSources: 'phone; text',
        tools: 'None',
        bottlenecks: 'schedule; invoice',
        followups: 'we call back',
        notes: ''
      };
      const auditResponse = await httpPost({ port, path: '/api/audit', data: auditPayload });
      lines.push('Audit submission response:');
      lines.push('```json');
      lines.push(JSON.stringify(auditResponse, null, 2));
      lines.push('```');
      // Verify new row appended
      let afterLines = beforeLines;
      if (fs.existsSync(auditCsv)) {
        afterLines = fs.readFileSync(auditCsv, 'utf8').split(/\r?\n/).filter(Boolean).length;
      }
      const rowAdded = afterLines === beforeLines + 1;
      lines.push(`Row added to audit CSV: ${rowAdded ? 'Yes' : 'No'}`);
      // Run recommended automations
      if (Array.isArray(auditResponse.recommendations)) {
        for (const rec of auditResponse.recommendations) {
          const id = recToId(rec);
          if (!id) continue;
          const autoResponse = await httpGet({ port, path: `/api/automation/${id}` });
          lines.push(`Automation result for ${id}:`);
          lines.push('```json');
          lines.push(JSON.stringify(autoResponse, null, 2));
          lines.push('```');
        }
      }
    } catch (err) {
      lines.push(`Error during run ${i}: ${err.message}`);
    }
    lines.push('');
  }
  // Shut down server
  serverProcess.kill();
  lines.push('---');
  lines.push('Global tests completed.');
  fs.writeFileSync(reportPath, lines.join('\n'), 'utf8');
  console.log(`Global test report written to ${reportPath}`);
}

// Helper function to convert recommendation text back to automation id
function recToId(rec) {
  switch (rec) {
    case 'Lead Capture & Auto‑Response':
      return 'lead-capture';
    case 'Smart Booking & Reminders':
      return 'smart-booking';
    case 'Quick Estimate Generator':
      return 'estimate-generator';
    case 'Review & Reputation Follow‑Up':
      return 'reputation-followup';
    case 'Invoice Tracking & Reminders':
      return 'invoice-tracking';
    default:
      return null;
  }
}

// Perform HTTP POST request
function httpPost({ port, path: p, data }) {
  return new Promise((resolve, reject) => {
    const json = JSON.stringify(data);
    const options = {
      hostname: 'localhost',
      port,
      path: p,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(json)
      }
    };
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body);
          resolve(parsed);
        } catch (err) {
          resolve({});
        }
      });
    });
    req.on('error', (err) => reject(err));
    req.write(json);
    req.end();
  });
}

// Perform HTTP GET request
function httpGet({ port, path: p }) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port,
      path: p,
      method: 'GET'
    };
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body);
          resolve(parsed);
        } catch (err) {
          resolve({});
        }
      });
    });
    req.on('error', (err) => reject(err));
    req.end();
  });
}

// Parse command line arguments
const args = process.argv.slice(2);
if (args.includes('--global')) {
  runGlobalTests().catch((err) => {
    console.error(err);
    process.exit(1);
  });
} else if (args.includes('--automation')) {
  const idx = args.indexOf('--automation');
  const name = args[idx + 1];
  if (!name || !automationNames.includes(name)) {
    console.error('Please provide a valid automation name after --automation');
    process.exit(1);
  }
  runAutomationTests(name).catch((err) => {
    console.error(err);
    process.exit(1);
  });
} else {
  // Run all automations by default
  (async () => {
    for (const name of automationNames) {
      await runAutomationTests(name);
    }
  })().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
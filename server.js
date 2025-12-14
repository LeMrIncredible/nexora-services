const http = require('http');
const fs = require('fs');
const path = require('path');

// Load environment variables from a .env file if present.  We implement
// a simple parser to avoid external dependencies.
function loadEnv() {
  const envPath = path.join(__dirname, '.env');
  if (!fs.existsSync(envPath)) return;
  const content = fs.readFileSync(envPath, 'utf8');
  content.split(/\r?\n/).forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return;
    const eqIndex = trimmed.indexOf('=');
    if (eqIndex === -1) return;
    const key = trimmed.substring(0, eqIndex).trim();
    const value = trimmed.substring(eqIndex + 1).trim();
    if (!process.env.hasOwnProperty(key)) {
      process.env[key] = value;
    }
  });
}

// Invoke loadEnv as early as possible.
loadEnv();

const { ensureDirectory, logAutomationRun } = require('./utils/logger');

/**
 * Simple static file server with an API endpoint.
 *
 * Because the sandbox has no network access and cannot install
 * dependencies from npm, this server uses only built‑in Node.js
 * modules. It serves files from the `public` directory and handles
 * POST requests to `/api/audit` by returning a JSON payload with a
 * list of recommended automations based on the form values.
 */

const publicDir = path.join(__dirname, 'public');

// Directory for storing audit submissions (CSV) and other data
const dataDir = path.join(__dirname, 'data');
ensureDirectory(dataDir);
const auditCsvPath = path.join(dataDir, 'audit_results.csv');

// Load automation handlers. Each automation exposes an async function
// returning an object with a message. If you add more automations,
// update this mapping accordingly.
const automations = {
  'lead-capture': require('./automations/lead-capture/index.js'),
  'smart-booking': require('./automations/smart-booking/index.js'),
  'estimate-generator': require('./automations/estimate-generator/index.js'),
  'reputation-followup': require('./automations/reputation-followup/index.js'),
  'invoice-tracking': require('./automations/invoice-tracking/index.js'),
};

/**
 * Determine content type based on file extension.
 * @param {string} filePath
 */
function getContentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  switch (ext) {
    case '.html':
      return 'text/html; charset=utf-8';
    case '.css':
      return 'text/css; charset=utf-8';
    case '.js':
      return 'application/javascript; charset=utf-8';
    case '.json':
      return 'application/json; charset=utf-8';
    case '.png':
      return 'image/png';
    case '.jpg':
    case '.jpeg':
      return 'image/jpeg';
    case '.svg':
      return 'image/svg+xml';
    default:
      return 'text/plain; charset=utf-8';
  }
}

/**
 * Serve a static file from the public directory. If the file cannot be
 * found, fall back to index.html for SPA behaviour.
 *
 * @param {http.ServerResponse} res
 * @param {string} filePath
 */
function serveFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      // fallback to index.html for any missing file
      fs.readFile(path.join(publicDir, 'index.html'), (error, indexData) => {
        if (error) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          return res.end('Not found');
        }
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        return res.end(indexData);
      });
      return;
    }
    const contentType = getContentType(filePath);
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

/**
 * Create an HTTP server.
 */
const server = http.createServer((req, res) => {
  const method = req.method;
  const urlPath = req.url.split('?')[0];

  // Handle API route
  if (method === 'POST' && urlPath === '/api/audit') {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
    });
    req.on('end', () => {
      let data;
      try {
        data = JSON.parse(body);
      } catch (err) {
        // If body is URL encoded, attempt to parse
        data = {};
        body.split('&').forEach((pair) => {
          const [key, value] = pair.split('=');
          data[decodeURIComponent(key)] = decodeURIComponent(value || '');
        });
      }
      // Simple recommendation logic
      const recommendations = [];
      const lower = (val) => (val || '').toString().toLowerCase();
      const leadSources = lower(data.leadSources);
      if (leadSources.includes('phone') || leadSources.includes('text') || leadSources.includes('mix') || leadSources.includes('social')) {
        recommendations.push('Lead Capture & Auto‑Response');
      }
      const bottlenecks = lower(data.bottlenecks);
      if (bottlenecks.includes('schedule') || bottlenecks.includes('booking') || bottlenecks.includes('calendar')) {
        recommendations.push('Smart Booking & Reminders');
      }
      if (bottlenecks.includes('estimate') || bottlenecks.includes('quote')) {
        recommendations.push('Quick Estimate Generator');
      }
      if (bottlenecks.includes('review') || bottlenecks.includes('reputation')) {
        recommendations.push('Review & Reputation Follow‑Up');
      }
      if (bottlenecks.includes('invoice') || bottlenecks.includes('payment') || bottlenecks.includes('collect')) {
        recommendations.push('Invoice Tracking & Reminders');
      }
      if (recommendations.length === 0) {
        recommendations.push('Lead Capture & Auto‑Response');
        recommendations.push('Smart Booking & Reminders');
      }
      const uniqueRecs = Array.from(new Set(recommendations));

      // Persist audit submission to CSV.  Each submission is stored as a
      // row.  If the file does not exist, write a header line first.
      try {
        const header = 'timestamp,name,businessName,email,phone,serviceType,city,teamSize,leadSources,tools,bottlenecks,followups,notes,recommendations,status\n';
        const exists = fs.existsSync(auditCsvPath);
        const row = [
          new Date().toISOString(),
          data.name || '',
          data.businessName || '',
          data.email || '',
          data.phone || '',
          data.serviceType || '',
          data.city || '',
          data.teamSize || '',
          data.leadSources || '',
          data.tools || '',
          data.bottlenecks || '',
          data.followups || '',
          data.notes || '',
          uniqueRecs.join('; '),
          'New',
        ].map((v) => '"' + String(v).replace(/"/g, '""') + '"').join(',') + '\n';
        if (!exists) {
          fs.writeFileSync(auditCsvPath, header + row, 'utf8');
        } else {
          fs.appendFileSync(auditCsvPath, row, 'utf8');
        }
      } catch (err) {
        console.error('Failed to persist audit submission:', err);
      }

      // TODO: optionally send notification emails using Gmail credentials.  This
      // demo does not send emails directly because external network access is
      // disabled in the sandbox environment.  See GOOGLE_WORKSPACE_SETUP.md
      // for guidance on enabling email notifications.

      const responseBody = JSON.stringify({ success: true, recommendations: uniqueRecs });
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(responseBody);
    });
    return;
  }

  // Handle automation execution API. Expects GET requests to
  // `/api/automation/:name`. For example: /api/automation/lead-capture
  if (method === 'GET' && urlPath.startsWith('/api/automation/')) {
    const name = urlPath.replace('/api/automation/', '').trim();
    const handler = automations[name];
    if (handler) {
      // Check feature toggle
      const toggleEnv = 'AUTOMATION_' + name.replace(/-/g, '_').toUpperCase() + '_ENABLED';
      const enabledVal = process.env[toggleEnv];
      if (enabledVal && (enabledVal.toLowerCase() === 'false' || enabledVal === '0')) {
        res.writeHead(403, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ success: false, error: 'Automation disabled' }));
        return;
      }
      (async () => {
        const start = Date.now();
        try {
          const result = await handler();
          const end = Date.now();
          await logAutomationRun(name, start, end, {}, result, null);
          res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify(result));
        } catch (err) {
          const end = Date.now();
          await logAutomationRun(name, start, end, {}, {}, err);
          console.error(err);
          res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ success: false, error: 'Automation error' }));
        }
      })();
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ success: false, error: 'Unknown automation' }));
    }
    return;
  }

  // Serve audit.html at /audit.html
  if (method === 'GET' && urlPath === '/audit.html') {
    return serveFile(res, path.join(publicDir, 'audit.html'));
  }

  // Serve files from public directory
  const filePath = path.join(publicDir, urlPath === '/' ? 'index.html' : urlPath);
  serveFile(res, filePath);
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Nexora server is running on http://localhost:${PORT}`);
});
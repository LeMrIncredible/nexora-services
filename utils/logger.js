const fs = require('fs');
const path = require('path');

/**
 * Ensure that a directory exists.  If it does not, recursively create it.
 *
 * @param {string} dirPath
 */
function ensureDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * Write a log entry for an automation run.  Logs are written to both the
 * console and to a timestamped file under `./logs/<automation>/`.  Each
 * log contains start and end times, the duration in milliseconds, a
 * summary of inputs and outputs, and any error information.
 *
 * @param {string} automationName  The folder/name of the automation.
 * @param {number} startTs         Start time in milliseconds since epoch.
 * @param {number} endTs           End time in milliseconds since epoch.
 * @param {any} inputSummary       An object summarising the inputs (omit sensitive data).
 * @param {any} outputSummary      An object summarising the outputs.
 * @param {Error|null} error       An Error object if the run failed, otherwise null.
 */
async function logAutomationRun(automationName, startTs, endTs, inputSummary, outputSummary, error) {
  const duration = endTs - startTs;
  const timestamp = new Date(startTs).toISOString().replace(/[:.]/g, '-');
  const logDir = path.join(__dirname, '..', 'logs', automationName);
  ensureDirectory(logDir);
  const logFilePath = path.join(logDir, `${timestamp}.log`);
  const logEntry = {
    automation: automationName,
    start: new Date(startTs).toISOString(),
    end: new Date(endTs).toISOString(),
    durationMs: duration,
    input: inputSummary,
    output: outputSummary,
    error: error ? { message: error.message, stack: error.stack } : null,
  };
  const logString = JSON.stringify(logEntry, null, 2);
  try {
    fs.writeFileSync(logFilePath, logString, 'utf8');
  } catch (writeErr) {
    console.error(`Failed to write log for ${automationName}:`, writeErr);
  }
  // Also output to console for immediate visibility
  console.log(`[${automationName}]`, logString);
}

module.exports = { ensureDirectory, logAutomationRun };

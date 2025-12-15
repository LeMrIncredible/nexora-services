const { logAutomationRun } = require('../../utils/logger');

module.exports = async (input) => {
  const start = Date.now();
  const { clientName } = input;
  try {
    // Determine a random appointment date within the next 7 days at 10 AM
    const startDate = new Date();
    const randomOffset = Math.floor(Math.random() * 7) + 1;
    const appointmentDate = new Date(startDate);
    appointmentDate.setDate(startDate.getDate() + randomOffset);
    appointmentDate.setHours(10, 0, 0, 0);

    // Build a user-friendly message
    const dateString = appointmentDate.toDateString();
    const timeString = appointmentDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const message = `Appointment booked for ${clientName} on ${dateString} at ${timeString}.`;

    const result = {
      status: 'success',
      name: 'Smart Booking & Reminders',
      message
    };

    await logAutomationRun(
      'smart-booking',
      start,
      Date.now(),
      { clientName, scheduledDate: appointmentDate },
      result,
      null
    );

    return result;
  } catch (error) {
    const errorResult = {
      status: 'error',
      name: 'Smart Booking & Reminders',
      message: error.message
    };
    await logAutomationRun(
      'smart-booking',
      start,
      Date.now(),
      { clientName },
      null,
      error
    );
    return errorResult;
  }
};

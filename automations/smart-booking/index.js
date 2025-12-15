const { logAutomationRun } = require('../../utils/logger');

module.exports = async (input) => {
  // Extract clientName from input
  const { clientName } = input;
  // Set starting date and choose a random offset between 1-7 days
  const startDate = new Date();
  const randomOffset = Math.floor(Math.random() * 7) + 1;
  const appointmentDate = new Date(startDate);
  appointmentDate.setDate(startDate.getDate() + randomOffset);
  // Schedule at 10:00 AM local time
  appointmentDate.setHours(10, 0, 0, 0);
  // Create a user-friendly message
  const dateString = appointmentDate.toDateString();
  const timeString = appointmentDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const message = `Appointment booked for ${clientName} on ${dateString} at ${timeString}.`;
  // Log the run
  await logAutomationRun('smart-booking', { clientName, scheduledDate: appointmentDate });
  // Return success result
  return { success: true, message };
};

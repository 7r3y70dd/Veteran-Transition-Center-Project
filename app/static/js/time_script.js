// Function to update the date and time every second
function updateDateTime() {
  const datetimeInput = document.getElementById('datetime');

  // Get the current date and time
  const now = new Date();

  // Format it in a readable form (e.g., "YYYY-MM-DD HH:MM:SS")
  const formattedDateTime = now.toISOString().slice(0, 19).replace("T", " ");

  // Update the input field with the current date and time
  datetimeInput.value = formattedDateTime;
}

// Call the update function every second
setInterval(updateDateTime, 1000);

// Initial call to populate the field immediately when the page loads
updateDateTime();
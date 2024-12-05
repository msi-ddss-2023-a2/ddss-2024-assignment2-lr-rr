// Reference to the body element
const body = document.body;

// Function to create a bubble
function createBubble() {
  const bubble = document.createElement("div");
  const size = Math.random() * 50 + 10; // Bubble size between 10px and 60px
  bubble.classList.add("bubble");
  bubble.style.width = `${size}px`;
  bubble.style.height = `${size}px`;
  bubble.style.left = `${Math.random() * window.innerWidth}px`;
  bubble.style.bottom = `-100px`; // Start slightly below the screen
  bubble.style.animationDuration = `${Math.random() * 3 + 4}s`; // Randomize speed for variety

  // Add bubble to the body
  body.appendChild(bubble);

  // Remove bubble after animation to keep DOM clean
  setTimeout(() => bubble.remove(), 7000);
}

// Create bubbles at a regular interval
setInterval(createBubble, 500);

// #########################################################
// #########################################################
// #########################################################
function validateForm(event) {
  // Initialize error messages
  var errorMessages = [];

  // Get form field values
  var title = document.getElementById("title").value;
  var authors = document.getElementById("authors").value;
  var category = document.getElementById("category").value;
  var price = document.getElementById("price").value;
  var book_date = document.getElementById("book_date").value;
  var description = document.getElementById("description").value;
  var keywords = document.getElementById("keywords").value;
  var notes = document.getElementById("notes").value;
  var recommendation = document.getElementById("recommendation").value;

  // Validate fields and collect errors
  if (!title) {
    errorMessages.push("Title is required.");
  }
  if (!authors) {
    errorMessages.push("Authors are required.");
  }
  if (!category) {
    errorMessages.push("Category is required.");
  }
  if (!price || isNaN(price) || parseFloat(price) <= 0) {
    errorMessages.push("Valid price is required.");
  }
  if (!book_date) {
    errorMessages.push("Book date is required.");
  } else {
    // Validate the book date
    var date = new Date(book_date);
    var year = date.getFullYear();
    var month = date.getMonth() + 1; // getMonth returns 0-11
    var day = date.getDate();

    // Check if the date is valid
    if (isNaN(date.getTime())) {
      errorMessages.push("Invalid book date.");
    }

    // Check for valid year (should be a reasonable range, e.g., not in the future)
    var currentYear = new Date().getFullYear();
    if (year < 1900 || year > currentYear) {
      errorMessages.push("Year should be between 1900 and the current year.");
    }

    // Check for valid month (should be between 1 and 12)
    if (month < 1 || month > 12) {
      errorMessages.push("Month must be between 1 and 12.");
    }

    // Check for valid day (e.g., Feb 30 or Apr 31 should be invalid)
    var daysInMonth = new Date(year, month, 0).getDate(); // Get the number of days in the month
    if (day < 1 || day > daysInMonth) {
      errorMessages.push("Day is not valid for the selected month and year.");
    }
  }

  if (!description) {
    errorMessages.push("Description is required.");
  }
  if (!keywords) {
    errorMessages.push("Keywords are required.");
  }
  if (!notes) {
    errorMessages.push("Notes are required.");
  }
  if (!recommendation) {
    errorMessages.push("Recommendation is required.");
  }

  // If there are errors, show an alert and prevent form submission
  if (errorMessages.length > 0) {
    alert("Please fix the following errors:\n" + errorMessages.join("\n"));
    event.preventDefault(); // Prevent form submission
    return false;
  }

  // If no validation errors, prevent form submission and do the AJAX request
  event.preventDefault(); // Prevent the form from submitting

  var formData = new FormData(document.querySelector("form"));

  // Make the AJAX request using fetch
  fetch("/insert_book", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json()) // Expecting JSON response
    .then((data) => {
      if (data.status === "success") {
        alert(data.message); // Show success message in alert
      } else {
        alert(data.message); // Show error message in alert
      }
    })
    .catch((error) => {
      alert("An unexpected error occurred: " + error); // Handle unexpected errors
    });
}

// #########################################################
// #########################################################
// #########################################################

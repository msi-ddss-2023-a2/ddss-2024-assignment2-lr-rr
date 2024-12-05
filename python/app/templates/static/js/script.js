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
// #########################################################s

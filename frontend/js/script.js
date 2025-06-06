document.addEventListener("DOMContentLoaded", () => {
  const reviewText = document.getElementById("reviewText");
  const analyzeButton = document.getElementById("analyzeButton");
  const clearButton = document.getElementById("clearButton");
  const sentimentResult = document.getElementById("sentimentResult");
  const confidenceScore = document.getElementById("confidenceScore");
  const sentimentBox = document.getElementById("sentimentBox");
  const loadingIndicator = document.getElementById("loadingIndicator");
  const confidenceProgressBar = document.getElementById(
    "confidenceProgressBar"
  );
  const sentimentIcon = document.getElementById("sentimentIcon");
  const exampleReviewsList = document.querySelector(".example-reviews ul");

  // Hide result and loading sections on initialization
  sentimentBox.style.display = "none";
  loadingIndicator.style.display = "none";

  // Function to reset result display
  const resetResultDisplay = () => {
    sentimentResult.textContent = "Sentiment will appear here.";
    confidenceScore.textContent = "Confidence Score: -";
    sentimentBox.className = "sentiment-box"; // Reset styling classes
    confidenceProgressBar.style.width = "0%"; // Reset progress bar width
    sentimentIcon.innerHTML = ""; // Clear icon
    sentimentBox.style.display = "flex"; // Ensure result box is visible
    loadingIndicator.style.display = "none"; // Hide loading
    analyzeButton.disabled = false; // Enable analyze button
    clearButton.disabled = false; // Enable clear button
  };

  // Handler for Analyze Sentiment button
  analyzeButton.addEventListener("click", async () => {
    const text = reviewText.value.trim();

    if (text === "") {
      sentimentResult.textContent = "Review text cannot be empty!";
      confidenceScore.textContent = "Confidence Score: -";
      sentimentBox.className = "sentiment-box";
      sentimentBox.style.display = "flex";
      loadingIndicator.style.display = "none";
      confidenceProgressBar.style.width = "0%";
      sentimentIcon.innerHTML = "";
      return;
    }

    // Show loading and hide previous results
    loadingIndicator.style.display = "flex";
    sentimentBox.style.display = "none";
    analyzeButton.disabled = true;
    clearButton.disabled = true;

    // --- PENTING: Perbarui URL API ---
    const apiUrl = "/api/predict_sentiment"; // Ganti dengan path relatif untuk Vercel

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `HTTP error! Status: ${response.status} - ${
            errorData.error || response.statusText
          }`
        );
      }

      const data = await response.json();
      console.log("Data from API:", data);

      sentimentResult.textContent = `Sentiment: ${data.sentiment}`;

      // Set styling class and icon based on sentiment
      sentimentBox.className = "sentiment-box";
      const sentimentLower = data.sentiment.toLowerCase();

      if (sentimentLower === "positive") {
        sentimentBox.classList.add("positive");
        sentimentIcon.innerHTML = '<i class="far fa-smile-beam"></i>'; // Positive icon
      } else if (sentimentLower === "negative") {
        sentimentBox.classList.add("negative");
        sentimentIcon.innerHTML = '<i class="far fa-frown"></i>'; // Negative icon
      } else {
        // Fallback for neutral or undefined categories
        sentimentIcon.innerHTML = '<i class="far fa-meh"></i>'; // Neutral icon
      }

      // Set confidence score and progress bar
      const scorePercentage = (data.sentiment_score * 100).toFixed(2);
      confidenceScore.textContent = `Confidence Score: ${scorePercentage}%`;
      confidenceProgressBar.style.width = `${scorePercentage}%`; // Set progress bar width
    } catch (error) {
      console.error("Error:", error);
      sentimentResult.textContent = "An error occurred during analysis.";
      confidenceScore.textContent = "Confidence Score: -";
      sentimentBox.className = "sentiment-box";
      sentimentBox.style.display = "flex";
      confidenceProgressBar.style.width = "0%";
      sentimentIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>'; // Error icon
    } finally {
      // Hide loading and show results
      loadingIndicator.style.display = "none";
      sentimentBox.style.display = "flex";
      analyzeButton.disabled = false;
      clearButton.disabled = false;
    }
  });

  // Handler for Clear Text button
  clearButton.addEventListener("click", () => {
    reviewText.value = ""; // Clear textarea
    resetResultDisplay(); // Call reset function
  });

  // Handler for clickable example reviews
  if (exampleReviewsList) {
    exampleReviewsList.addEventListener("click", (event) => {
      if (event.target.tagName === "LI" && event.target.dataset.review) {
        reviewText.value = event.target.dataset.review;
        analyzeButton.click(); // Trigger analysis automatically
      }
    });
  }
});

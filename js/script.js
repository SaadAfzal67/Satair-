document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("feedbackOverlay");
  const intentSelect = document.getElementById("feedback-intent");
  const successSelect = document.getElementById("feedback-success");
  const commentField = document.getElementById("feedback-text");

  const noticeEl = document.getElementById("feedbackNotice");

  const STORAGE_KEY = "satair_feedback_entries";
  const SERVER_ENDPOINT = "/api/feedback";

  const formatFeedbackEntry = (feedback) => {
    const date = new Date(feedback.timestamp);
    const header = `---\nDate: ${date.toLocaleString()}\n`;
    const body = `Task: ${feedback.task}\nSuccess: ${feedback.success}\nComment: ${feedback.comment || "(no comment)"}\n`;
    return `${header}${body}`;
  };

  const getStoredEntries = () => {
    return localStorage.getItem(STORAGE_KEY) || "";
  };

  const appendStoredEntry = (entryText) => {
    const existing = getStoredEntries();
    localStorage.setItem(STORAGE_KEY, existing + entryText);
  };


  const saveFeedbackToServer = async (feedback) => {
    try {
      const res = await fetch(SERVER_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(feedback),
      });

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      return true;
    } catch (err) {
      return false;
    }
  };

  const showNotice = (text) => {
    if (!noticeEl) return;
    noticeEl.textContent = text;
  };

  window.openFeedback = () => {
    overlay.style.display = "flex";
    intentSelect.focus();
  };

  window.closeFeedback = (event) => {
    if (event) event.stopPropagation();
    overlay.style.display = "none";
  };

  window.submitFeedback = async () => {
    const feedback = {
      task: intentSelect.value,
      success: successSelect.value,
      comment: commentField.value.trim(),
      timestamp: new Date().toISOString(),
    };

    const entryText = formatFeedbackEntry(feedback);

    const savedToServer = await saveFeedbackToServer(feedback);
    if (savedToServer) {
      showNotice("Thanks for your feedback — saved to disk via the optional backend server.");
      
      appendStoredEntry(entryText);
    } else {
      appendStoredEntry(entryText);
      showNotice(
        "Thanks for your feedback — saved locally in your browser. Start the optional backend server to persist it to feedback/feedback.txt."
      );
    }

    closeFeedback();

    intentSelect.selectedIndex = 0;
    successSelect.selectedIndex = 0;
    commentField.value = "";
  };

  
  const searchInput = document.getElementById("partSearchInput");
  const searchButton = document.getElementById("searchButton");
  const browseAllButton = document.getElementById("browseAllButton");
  const searchResults = document.getElementById("searchResults");

  const searchParts = async (query, limit = null) => {
    try {
      let url = query ? `/api/parts?q=${encodeURIComponent(query)}` : "/api/parts";
      if (limit && !query) {
        url += `?limit=${limit}`;
      }
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Search failed: ${res.status}`);
      }
      const parts = await res.json();
      displayParts(parts);
    } catch (err) {
      console.error("Search error:", err);
      searchResults.innerHTML = "<p>Error loading parts. i need to mak sure the server is running.</p>";
    }
  };

  const displayParts = (parts) => {
    if (parts.length === 0) {
      searchResults.innerHTML = "<p>No parts found.</p>";
      return;
    }

    const html = parts.map(part => `
      <div class="product">
        <img src="https://via.placeholder.com/300x200?text=${encodeURIComponent(part.part_number)}" alt="${part.name}" onerror="this.src='assets/images/part.jpg'">
        <div class="product-info">
          <h3>${part.name}</h3>
          <p><strong>Part Number:</strong> ${part.part_number}</p>
          <p>${part.description}</p>
          <p><em>Category: ${part.category}</em></p>
          <button>Add to cart</button>
        </div>
      </div>
    `).join("");

    searchResults.innerHTML = html;
  };

  searchButton.addEventListener("click", () => {
    const query = searchInput.value.trim();
    if (query) {
      searchParts(query);
    } else {
      searchResults.innerHTML = "<p>Please enter a search term or click 'Browse All Parts'.</p>";
    }
  });

  browseAllButton.addEventListener("click", () => {
    searchParts(""); 
  });

  searchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      searchButton.click();
    }
  });

  
  searchParts("", 3);
});

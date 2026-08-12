document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const defaultActivityOption = '<option value="">-- Select an activity --</option>';

  function showMessage(message, type) {
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = defaultActivityOption;

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = Math.max(
          details.max_participants - details.participants.length,
          0
        );
        const waitlist = details.waitlist || [];
        const availability = spotsLeft > 0
          ? `${spotsLeft} spots left`
          : `Full — ${waitlist.length} on waitlist`;
        const participantsMarkup = details.participants.length
          ? `
            <ul class="participants-list">
              ${details.participants
                .map(
                  (participant) => `
                    <li class="participant-item">
                      <span class="participant-email">${participant}</span>
                      <button
                        type="button"
                        class="participant-remove-btn"
                        data-activity="${encodeURIComponent(name)}"
                        data-email="${encodeURIComponent(participant)}"
                        aria-label="Remove ${participant} from ${name}"
                        title="Unregister participant"
                      >
                        <span aria-hidden="true" class="delete-icon">&#128465;</span>
                      </button>
                    </li>
                  `
                )
                .join("")}
            </ul>
          `
          : '<p class="empty-participants">No participants yet</p>';
        const waitlistMarkup = waitlist.length
          ? `
            <ul class="participants-list">
              ${waitlist
                .map(
                  (student) => `
                    <li class="participant-item">
                      <span class="participant-email">${student}</span>
                      <button
                        type="button"
                        class="participant-remove-btn"
                        data-activity="${encodeURIComponent(name)}"
                        data-email="${encodeURIComponent(student)}"
                        aria-label="Remove ${student} from the waitlist for ${name}"
                        title="Leave waitlist"
                      >
                        <span aria-hidden="true" class="delete-icon">&#128465;</span>
                      </button>
                    </li>
                  `
                )
                .join("")}
            </ul>
          `
          : '<p class="empty-participants">Waitlist is empty</p>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${availability}</p>
          <div class="participants-section">
            <p><strong>Participants</strong></p>
            ${participantsMarkup}
          </div>
          <div class="waitlist-section">
            <p><strong>Waitlist</strong></p>
            ${waitlistMarkup}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(
          result.message,
          result.status === "waitlisted" ? "waitlisted" : "success"
        );
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  activitiesList.addEventListener("click", async (event) => {
    const removeButton = event.target.closest(".participant-remove-btn");
    if (!removeButton) {
      return;
    }

    const encodedActivity = removeButton.dataset.activity;
    const encodedEmail = removeButton.dataset.email;

    if (!encodedActivity || !encodedEmail) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodedActivity}/participants/${encodedEmail}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister participant. Please try again.", "error");
      console.error("Error unregistering participant:", error);
    }
  });

  // Initialize app
  fetchActivities();
});

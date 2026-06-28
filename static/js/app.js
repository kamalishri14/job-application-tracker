// Job Trail — handles inline status changes without a full page reload.
document.addEventListener("DOMContentLoaded", () => {
    const selects = document.querySelectorAll(".status-select");

    selects.forEach((select) => {
        // remember the previous value in case the request fails
        select.dataset.previous = select.value;

        select.addEventListener("change", async (event) => {
            const appId = select.dataset.appId;
            const newStatus = select.value;

            // optimistic UI: swap the colour class immediately
            updateStatusClass(select, newStatus);

            try {
                const response = await fetch(`/api/applications/${appId}/status`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status: newStatus }),
                });

                if (!response.ok) throw new Error("Request failed");

                const data = await response.json();
                select.dataset.previous = data.status;
                flashRow(select.closest("tr"));
            } catch (err) {
                // revert on failure
                select.value = select.dataset.previous;
                updateStatusClass(select, select.dataset.previous);
                alert("Could not update status. Please check your connection and try again.");
            }
        });
    });

    function updateStatusClass(select, status) {
        select.classList.remove(
            "status-applied",
            "status-interview",
            "status-offer",
            "status-rejected"
        );
        select.classList.add(`status-${status.toLowerCase()}`);
    }

    function flashRow(row) {
        if (!row) return;
        row.style.transition = "background-color 0.3s ease";
        row.style.backgroundColor = "#f0dccb";
        setTimeout(() => {
            row.style.backgroundColor = "";
        }, 600);
    }
});

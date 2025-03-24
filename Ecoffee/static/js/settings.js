document.addEventListener('DOMContentLoaded', function() {
    const editButton = document.getElementById("edit-button");
    const userForm = document.getElementById("user-details-form");
    //select inputs
    const inputs = document.querySelectorAll(".user-settings input");

    editButton.addEventListener("click", function() {
        inputs.forEach(input => {
            if (input.type !== "hidden") {
                input.disabled = !input.disabled;
            }
        });

        if(editButton.textContent === "Edit") {
            editButton.textContent = "Save";
            editButton.classList.add("save-mode");
        } else {
            editButton.textContent = "Edit";
            editButton.classList.remove("save-mode");
            // Submit the form when Save is clicked
            userForm.submit();
        }
    });
})

  
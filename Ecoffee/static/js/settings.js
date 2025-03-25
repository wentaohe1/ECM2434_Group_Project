document.addEventListener('DOMContentLoaded', function() {
    const editButton = document.getElementById("edit-button");
    //select inputs
    const inputs = document.querySelectorAll(".user-settings input");

    editButton.addEventListener("click", function() {
        inputs.forEach(input => {
            input.disabled = !input.disabled;
        });

        if(editButton.textContent === "Edit") {
            editButton.textContent = "Save";
            editButton.textContent = "Save";
            editButton.type = "submit"; 
            editButton.name = "user_form_submit";
        } else {
            editButton.textContent = "Edit";
            editButton.type = "button";
            editButton.removeAttribute("name");
        }
    });
})

  
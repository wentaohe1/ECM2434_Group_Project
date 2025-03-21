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
        } else {
            editButton.textContent = "Edit";
        }
    });
})
//profile picture update button
document.getElementById('id_profile_image').onchange = function(e) {
    document.getElementById('profpic').src = URL.createObjectURL(e.target.files[0]);
};
  
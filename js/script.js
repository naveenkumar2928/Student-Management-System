// Confirm before deleting a student
function confirmDelete() {
    return confirm("Are you sure you want to delete this student?");
}


// Automatically hide alert messages
setTimeout(function () {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {
        alert.style.display = "none";
    });
}, 3000);
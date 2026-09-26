// Scholarship Management Portal

console.log("Scholarship Management Portal loaded");

// Confirm before submitting forms
const forms = document.querySelectorAll("form");

forms.forEach(function(form) {

    form.addEventListener("submit", function(event) {

        const confirmSubmit = confirm(
            "Are you sure you want to submit?"
        );

        if (!confirmSubmit) {
            event.preventDefault();
        }

    });

});
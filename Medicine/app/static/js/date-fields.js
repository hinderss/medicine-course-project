document.addEventListener('DOMContentLoaded', function() {
    const inputFields = document.querySelectorAll('.date-field');
    console.log("started");

    inputFields.forEach(function(inputField) {
        console.log(inputField);
        inputField.type = 'text';

        inputField.addEventListener('focus', function() {
            inputField.type = 'date';
        });

        inputField.addEventListener('blur', function() {
            if (inputField.value == '') {
                inputField.type = 'text';
            }
        });
    });
});

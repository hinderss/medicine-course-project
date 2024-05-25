document.addEventListener('DOMContentLoaded', function() {
    const byAddressButton = document.getElementById('registrationAddressEqualLivivngAddress');
    const registrationAddressSection = document.querySelectorAll('.registrationAddressSection');

    var sourceFields = {
        region: document.querySelector('input[name="region"]'),
        city: document.querySelector('input[name="city"]'),
        street: document.querySelector('input[name="street"]'),
        house: document.querySelector('input[name="house"]'),
        building: document.querySelector('input[name="building"]'),
        entrance: document.querySelector('input[name="entrance"]'),
        apartment: document.querySelector('input[name="apartment"]')
    };

    var targetFields = {
        region: document.querySelector('input[name="registration_region"]'),
        city: document.querySelector('input[name="registration_city"]'),
        street: document.querySelector('input[name="registration_street"]'),
        house: document.querySelector('input[name="registration_house"]'),
        building: document.querySelector('input[name="registration_building"]'),
        entrance: document.querySelector('input[name="registration_entrance"]'),
        apartment: document.querySelector('input[name="registration_apartment"]')
    };

    function updateRegistrationFields() {
        Object.keys(sourceFields).forEach(field => {
            targetFields[field].value = sourceFields[field].value;
        });
    }

    function hideRegistrationAddressSection() {
        registrationAddressSection.forEach(section => {
            if (byAddressButton.checked) {
                section.style.display = 'none';
                updateRegistrationFields();
            } else {
                section.style.display = 'flex';
            }
        });
    }

    if (Object.keys(sourceFields).every(field => sourceFields[field].value === targetFields[field].value)) {
        byAddressButton.checked = true;
        hideRegistrationAddressSection();
    }

    byAddressButton.addEventListener('change', function() {
        hideRegistrationAddressSection();
    });
});

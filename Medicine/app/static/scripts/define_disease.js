document.addEventListener("DOMContentLoaded", function() {

    var popUp = document.getElementById("popUp");
    var btn = document.getElementById("diagnosticsButton");
    var span = document.getElementsByClassName("closeDiagnosticPopUp")[0];

    btn.onclick = function() {
        popUp.style.display = "block";
    }

    span.onclick = function() {
        popUp.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == popUp) {
            popUp.style.display = "none";
        }
    }
});

function submitSymptoms() {
    let symptoms = [];
    $('input[name="symptom"]:checked').each(function() {
        symptoms.push($(this).val());
    });

    $.ajax({
        url: '/diagnose',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ symptoms: symptoms }),
        success: function(response) {
            $('#results').empty();
            if (response.length > 0) {
                response.forEach(function(disease) {
                    $('#results').append('<p>Возможное заболевание: ' + disease.name + '<br>Рекомендуется обратиться к врачу: ' + disease.doctor + '</p>');
                });
            } else {
                $('#results').append('<p>Нет совпадений для указанных симптомов.</p>');
            }
        }
    });
}

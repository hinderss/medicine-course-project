//получение специальностей врачей
document.addEventListener("DOMContentLoaded", function() {
    // Создаем новый объект XMLHttpRequest
    var xhr = new XMLHttpRequest();

    // Открываем новый запрос GET к указанному URL-адресу
    xhr.open("GET", "/practice_profiles", true);

    // Отправляем запрос
    xhr.send();

    // Устанавливаем обработчик события "load" для запроса
    xhr.onload = function() {
        // Парсим полученный ответ в формате JSON
        var specialties = JSON.parse(xhr.responseText);

        // Получаем элемент specialtySelectionSelector
        var specialtySelection = document.getElementById("specialtySelectionSelector");

        // Перебираем каждую специальность и создаем кнопку для нее
        specialties.practice_profiles.forEach(function(specialty) {
            var button = document.createElement("button");
            button.classList.add("button");
            button.setAttribute("type", "button");
            button.setAttribute("onclick", "selectSpecialty('" + specialty + "')");
            button.textContent = specialty;
            specialtySelection.appendChild(button);
        });
    };
});

function selectSpecialty(specialty) {
    // Отправляем AJAX-запрос для получения списка врачей по выбранному направлению
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/doctors?specialty=" + specialty, true);
    xhr.send();

    xhr.onload = function() {
        if (xhr.status === 200) {
            var doctors = JSON.parse(xhr.responseText);

            // Заполняем список врачей
            var doctorLinks = $("#doctorLinks");
            doctorLinks.empty();

            doctors.forEach(function (doctor) {
                var doctorLink = $("<a>", {
                    id: specialty, // Use the specialty as the ID
                    class: "marginTop20px",
                    click: function () {
                        showDoctorDetails(doctor);
                    }
                });

                // Создаем контейнер с изображением, именем и фамилией
                var container = $("<div>", {
                    class: "container row"
                });

                container.append($("<img>", {
                    src: "/uploads/" + doctor.photo_path,
                    id: "appointementDoctorPhoto"
                }));

                var detailsContainer = $("<div>");
                detailsContainer.append($("<h4>", {
                    class: "appointementDoctorData white thin",
                    id: "doctorName",
                    text: doctor.firstname
                }));
                detailsContainer.append($("<h4>", {
                    class: "appointementDoctorData white thin",
                    id: "doctorSurname",
                    text: doctor.surname
                }));

                container.append(detailsContainer);
                doctorLink.append(container);
                doctorLinks.append(doctorLink);
            });

            // Переключаем видимость элементов
            $("#specialtySelection").addClass("hidden");
            $("#doctorList").removeClass("hidden");
            $("#goBackBtn").removeClass("hidden");
        } else {
            console.error("Ошибка при получении списка врачей");
        }
    };
}

function showDoctorDetails(doctor) {
    // Показываем подробную информацию о враче
    document.getElementById("doctorDetails").classList.remove("hidden");
    document.getElementById("doctorFirstnameAppointement").textContent = doctor.firstname;
    document.getElementById("doctorSurnameAppointement").textContent = doctor.surname;
    console.log(doctor.photo_path);
    
    // Создаем элемент изображения
    var img = document.createElement("img");
    img.src = "/uploads/" + doctor.photo_path;
    img.id = "appointementDoctorPhoto";

    // Очищаем содержимое контейнера перед добавлением нового изображения
    document.getElementById("appointementDoctorPhotoApp").innerHTML = '';
    
    // Добавляем изображение в контейнер
    document.getElementById("appointementDoctorPhotoApp").appendChild(img);

    // Дополнительный код для отображения деталей врача

    // Скрываем список врачей
    document.getElementById("doctorList").classList.add("hidden");
    document.getElementById("timePickerContainer").classList.remove("hidden");
    document.getElementById("appointementTextArea").classList.remove("hidden");
    document.getElementById("submitAppointment").classList.remove("hidden");
    document.getElementById("goBackBtn").classList.remove("hidden");

    document.getElementById("appointementTextArea").value = "";
    var form = document.getElementById('createAppointment');
    var dateInput = form.querySelector('input[name="date"]');
    console.log(form);
    console.log(dateInput);
    console.log(dateInput.value);

    // Делаем запрос для получения списка занятого времени
    fetch('/appointments/get_doctor_time?doctor_id=' + doctor.id + '&date=' + dateInput.value)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Обрабатываем полученные данные
            console.log(data);

            // Получаем ссылку на элемент <select> по его идентификатору
            var selectElement = document.getElementById('appt');
            selectElement.innerHTML = '';
            selectElement.disabled = true;

            // Получаем данные о назначениях
            var appointmentsData = data;

            var doctorId = document.createElement('input');
            doctorId.classList.add("hidden");
            doctorId.name = 'doctor_id'
            doctorId.value = doctor.id;
            form.appendChild(doctorId);
            
            // Извлекаем из данных время назначения и добавляем в <select>
            appointmentsData.appointments.forEach(function(appointment) {
                var appointmentDateTime = new Date(appointment.appointment_date_time);
                var appointmentTime = appointmentDateTime.getUTCHours().toString().padStart(2, '0') + ':' + appointmentDateTime.getUTCMinutes().toString().padStart(2, '0');
                selectElement.disabled = false;
                // Создаем новый элемент <option>
                var optionElement = document.createElement('option');
                optionElement.value = appointmentTime + ':00';
                console.log(optionElement.value);
                optionElement.textContent = appointmentTime;
                // optionElement.disabled = true; // Предполагается, что это время уже занято
                // Добавляем новый элемент <option> в <select>
                selectElement.appendChild(optionElement);
            });
            // Возможно, здесь вы захотите что-то сделать с полученным списком времени
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}

function goBack() {
    // Здесь вы можете добавить код для возврата к выбору врача или специальности
    // В данном примере просто скрываем подробные детали врача
    $("#specialtySelection").removeClass("hidden");
    $("#doctorDetails").addClass("hidden");
    $("#doctorList").addClass("hidden");
    $("#timePickerContainer").addClass("hidden");
    $("#submitAppointment").addClass("hidden");
    $("#appointementTextArea").addClass("hidden");
    $("#goBackBtn").addClass("hidden");
}
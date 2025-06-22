document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("createAppointmentForm").addEventListener("submit", function(event){
        event.preventDefault(); // Предотвращаем отправку формы

        // Получаем данные формы
        var formData = new FormData(this);

        // Отправляем AJAX-запрос
        fetch('/create-appointment', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert('Успешно сохранено.'); // Показываем сообщение об успехе
            } else {
                response.json().then(errors => {
                    let errorMessage = '';
                    for (const field in errors) {
                        errorMessage += `${field}: ${errors[field]}\n`;
                    }
                    alert('Произошла ошибка:\n' + errorMessage);
                    goBack();
                });
            }
        })
        .catch(error => {
            console.error('Произошла ошибка:', error);
        });
        // Затем можно продолжить с отправкой формы
    });

    // Получаем все чекбоксы, которые должны влиять на обязательность полей
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');

    // Перебираем каждый чекбокс
    checkboxes.forEach(function(checkbox) {
        // Добавляем обработчик события на изменение состояния чекбокса
        checkbox.addEventListener('change', function(event) {
            // Если чекбокс отмечен (checked)
            if (this.checked) {
                // Находим все input поля в родительском контейнере чекбокса
                var inputs = this.parentElement.querySelectorAll('input');
                
                // Делаем все найденные input поля обязательными (required)
                inputs.forEach(function(input) {
                    input.required = true;
                });
                
                // Теперь вы можете вызвать отправку формы или что-то еще здесь, если необходимо
                // document.getElementById("submitBtn").click();
            } else {
                // Если чекбокс снят, убираем атрибут required у всех полей ввода
                var inputs = this.parentElement.querySelectorAll('input');
                inputs.forEach(function(input) {
                    input.required = false;
                });
            }
        });
    });
});


// document.addEventListener("DOMContentLoaded", function() {
//     const closeSidebarBtn = document.querySelector("#closeSidebarBtn");
//     const openSidebarBtn =  document.querySelector("#filterIcon");
//     const sidebar = document.querySelector(".sidebar"); 
//     // Показываем или скрываем меню при нажатии на изображение меню
//     openSidebarBtn.addEventListener("click", function() {
//         if (sidebar.style.display === "flex") {
//             sidebar.style.display = "none";
//         } else {
//             sidebar.style.display = "flex";
//         }
//     });

//     // Скрываем меню при нажатии вне его области
//     document.addEventListener("click", function(event) {
//         // Проверяем, что клик произошел не на изображении меню и не внутри самого меню
//         if (event.target !== openSidebarBtn && !sidebar.contains(event.target)) {
//             sidebar.style.display = "none";
//         }
//     });

//     closeSidebarBtn.addEventListener("click", function(event) {
//             sidebar.style.display = "none";
//     });
// });
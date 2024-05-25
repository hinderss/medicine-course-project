document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("createAppointment").addEventListener("submit", function(event){
        event.preventDefault(); // Предотвращаем отправку формы

        // Отправляем запрос на сервер
        var formData = new FormData(this);
        fetch('/createAppointment', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert('Вы успешно записаны на прием!'); // Показываем сообщение об успехе
                goBack();
            } else if (response.status === 401) {
                // Если получен статус 401, перенаправляем на страницу входа
                window.location.href = '/login';
            } else {
                response.text().then(errorMessage => {
                    alert('Произошла ошибка при записи на прием: ' + errorMessage); // Показываем сообщение об ошибке
                });
            }
        })
        .catch(error => {
            console.error('Произошла ошибка:', error);
        });
    });
});
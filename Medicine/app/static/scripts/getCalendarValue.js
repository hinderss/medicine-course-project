document.addEventListener("DOMContentLoaded", function () {
    // Добавляем обработчик событий для родительского элемента, используя делегирование
    document.addEventListener('click', function(event) {
        // Проверяем, была ли нажата кнопка с классом vanilla-calendar-day__btn
        if (event.target.classList.contains('vanilla-calendar-day__btn')) {
            // Получаем значение data-calendar-day
            var selectedDate = event.target.getAttribute('data-calendar-day');

                // Выводим значение в консоль
                // console.log("Выбранная дата:", selectedDate);

                // Далее, вы можете использовать значение selectedDate и подставить его в нужное место в форме
                // Например, для подстановки в поле с именем "date":
            document.querySelector('input[name="date"]').value = selectedDate;
            goBack();
            document.getElementById("specialtySelection").classList.remove("hidden");
        }
    });
});
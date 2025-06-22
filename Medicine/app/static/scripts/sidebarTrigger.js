document.addEventListener("DOMContentLoaded", function() {
    const closeSidebarBtn = document.querySelector("#closeSidebarBtn");
    const openSidebarBtn = document.querySelector("#filterIcon");
    const sidebar = document.querySelector(".sidebar");

    // Показываем или скрываем сайдбар с анимацией
    openSidebarBtn.addEventListener("click", function(event) {
        event.stopPropagation(); // Предотвращаем всплытие, чтобы не сработал document.click
        sidebar.classList.toggle("active");
    });

    // Скрываем сайдбар при нажатии вне его области
    document.addEventListener("click", function(event) {
        if (!sidebar.contains(event.target) && event.target !== openSidebarBtn) {
            sidebar.classList.remove("active");
        }
    });

    // Скрываем сайдбар при нажатии на кнопку закрытия
    closeSidebarBtn.addEventListener("click", function(event) {
        event.stopPropagation(); // Предотвращаем всплытие
        sidebar.classList.remove("active");
    });
});
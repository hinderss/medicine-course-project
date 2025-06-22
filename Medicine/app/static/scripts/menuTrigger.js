document.addEventListener("DOMContentLoaded", function () {
    const menuBtn = document.querySelector("#menuIcon");
    const menu = document.querySelector(".menu");

    // Переключаем класс show
    menuBtn.addEventListener("click", function (e) {
        e.stopPropagation(); // чтобы не срабатывало закрытие при клике
        menu.classList.toggle("show");
    });

    // Закрываем меню при клике вне его
    document.addEventListener("click", function (event) {
        if (!menu.contains(event.target) && event.target !== menuBtn) {
            menu.classList.remove("show");
        }
    });
});

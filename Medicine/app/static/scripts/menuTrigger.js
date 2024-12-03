document.addEventListener("DOMContentLoaded", function() {
    const menuBtn = document.querySelector("#menuIcon"); // Получаем изображение меню
    const menu = document.querySelector(".menu"); // Получаем само меню

    
    // Показываем или скрываем меню при нажатии на изображение меню
    menuBtn.addEventListener("click", function() {
        if (menu.style.display === "block") {
            menu.style.display = "none";
        } else {
            menu.style.display = "block";
        }
    });

    // Скрываем меню при нажатии вне его области
    document.addEventListener("click", function(event) {
        // Проверяем, что клик произошел не на изображении меню и не внутри самого меню
        if (event.target !== menuBtn && !menu.contains(event.target)) {
            menu.style.display = "none";
        }
    });
});
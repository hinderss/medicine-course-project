document.addEventListener("DOMContentLoaded", function() {
    const closeSidebarBtn = document.querySelector("#closeSidebarBtn");
    const openSidebarBtn =  document.querySelector("#filterIcon");
    const sidebar = document.querySelector(".sidebar"); 
    // Показываем или скрываем меню при нажатии на изображение меню
    openSidebarBtn.addEventListener("click", function() {
        if (sidebar.style.display === "flex") {
            sidebar.style.display = "none";
        } else {
            sidebar.style.display = "flex";
        }
    });

    // Скрываем меню при нажатии вне его области
    document.addEventListener("click", function(event) {
        // Проверяем, что клик произошел не на изображении меню и не внутри самого меню
        if (event.target !== openSidebarBtn && !sidebar.contains(event.target)) {
            sidebar.style.display = "none";
        }
    });

    closeSidebarBtn.addEventListener("click", function(event) {
            sidebar.style.display = "none";
    });
});
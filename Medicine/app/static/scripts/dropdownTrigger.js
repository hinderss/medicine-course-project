//Для сортировки
document.addEventListener("DOMContentLoaded", function() {
    const dropdownBtn = document.getElementById("doctorListSortContainer");
    const dropdownImg = document.getElementById("sortDropdownImg");
    const dropdownList = document.getElementById("doctorListSortContainerDropdown");

    dropdownBtn.addEventListener("click", function() {
        if (dropdownList.style.display === "flex") {
            dropdownList.style.display = "none";
            dropdownImg.style.transform = "rotate(0deg)"; // Возвращаем изображение в исходное положение
        } else {
            dropdownList.style.display = "flex";
            dropdownList.style.alignItems = "flex-start";
            dropdownImg.style.transform =  "rotate(180deg)"; // Поворачиваем изображение
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Для специализации врачей
    const dropdownSpecialityImg = document.getElementById("doctorsSpecialtyDropdownImg");
    const dropdownSpecialityList = document.getElementById("doctorsSpecialtyDropdownList");
    const inputSpeciality = document.querySelectorAll("#doctorsSpecialtyDropdownList input[type='radio']");

    dropdownSpecialityImg.addEventListener("click", function() {
        if (dropdownSpecialityList.style.display === "block") {
            dropdownSpecialityList.style.display = "none";
            dropdownSpecialityImg.style.transform = "rotate(180deg)"; // Возвращаем изображение в исходное положение
            inputSpeciality.forEach(input => {
                input.checked = false; // Обнуляем значение input при скрытии dropdown'а
            });
        } else {
            dropdownSpecialityList.style.display = "block";
            dropdownSpecialityImg.style.transform =  "rotate(0deg)"; // Поворачиваем изображение
        }
    });

    // Для опыта
    const experienceImg = document.getElementById("experienceDropdownImg");
    const dropdownExpreienceList = document.getElementById("experienceDropdownList");
    const inputExperience = document.querySelectorAll("#experienceDropdownList input[type='checkbox']");

    experienceImg.addEventListener("click", function() {
        if (dropdownExpreienceList.style.display === "block") {
            dropdownExpreienceList.style.display = "none";
            experienceImg.style.transform = "rotate(180deg)"; // Возвращаем изображение в исходное положение
            inputExperience.forEach(input => {
                input.checked = false; // Обнуляем значение input при скрытии dropdown'а
            });
        } else {
            dropdownExpreienceList.style.display = "block";
            experienceImg.style.transform =  "rotate(0deg)"; // Поворачиваем изображение
        }
    });

    // Для цен
    const priceImg = document.getElementById("pricesDropdownImg");
    const dropdownPriceList = document.getElementById("pricesDropdownList");
    const inputPrices = document.querySelectorAll("#pricesDropdownList input[type='checkbox']");

    priceImg.addEventListener("click", function() {
        if (dropdownPriceList.style.display === "block") {
            dropdownPriceList.style.display = "none";
            priceImg.style.transform = "rotate(180deg)"; // Возвращаем изображение в исходное положение
            inputPrices.forEach(input => {
                input.checked = false; // Обнуляем значение input при скрытии dropdown'а
            });
        } else {
            dropdownPriceList.style.display = "block";
            priceImg.style.transform =  "rotate(0deg)"; // Поворачиваем изображение
        }
    });

    // Для рейтинга
    const ratingImg = document.getElementById("ratingDropdownImg");
    const dropdownRatingList = document.getElementById("ratingDropdownList");
    const inputRating = document.querySelectorAll("#ratingDropdownList input[type='radio']");

    ratingImg.addEventListener("click", function() {
        if (dropdownRatingList.style.display === "block") {
            dropdownRatingList.style.display = "none";
            ratingImg.style.transform = "rotate(180deg)"; // Возвращаем изображение в исходное положение
            inputRating.forEach(input => {
                input.checked = false; // Обнуляем значение input при скрытии dropdown'а
            });
        } else {
            dropdownRatingList.style.display = "block";
            ratingImg.style.transform =  "rotate(0deg)"; // Поворачиваем изображение
        }
    });
});
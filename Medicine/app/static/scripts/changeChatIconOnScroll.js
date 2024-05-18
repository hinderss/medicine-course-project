window.addEventListener('scroll', function () {
    var gptIcon = document.getElementById('gptIcon');
    var scrollPosition = window.scrollY;

    if (scrollPosition > 70) {
        gptIcon.classList.remove('white');
    } else {
        gptIcon.classList.add('white');
    }
});
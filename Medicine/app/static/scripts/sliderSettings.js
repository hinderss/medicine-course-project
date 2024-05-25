document.addEventListener('DOMContentLoaded', function () {
    new Splide('#splide-container', {
        type       : 'carousel',
        perPage    : 1,
        pagination : false,
        focus      : 'center',
        breakpoints: {
        600: {
            perPage: 1,
        },
        800: {
            perPage: 1,
        },
        },
        drag: false,
    }).mount();
});
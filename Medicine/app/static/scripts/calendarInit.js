document.addEventListener("DOMContentLoaded", function() {
    const calendar = new VanillaCalendar('#calendar');
    calendar.init();
    document.getElementById("specialtySelection").classList.add("hidden");
});
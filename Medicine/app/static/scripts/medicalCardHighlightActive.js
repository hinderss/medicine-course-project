document.addEventListener('DOMContentLoaded', function() {
    const sidebarItems = document.querySelectorAll('.sidebar h5');

    sidebarItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove 'active' class from all items
            sidebarItems.forEach(i => i.classList.remove('active'));

            // Add 'active' class to the clicked item
            item.classList.add('active');
        });
    });
});
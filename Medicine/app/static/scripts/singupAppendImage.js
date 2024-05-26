document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('addImageButton').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', function() {
        var fileInput = document.getElementById('fileInput');
        var addImageButton = document.getElementById('addImageButton');

        while (addImageButton.firstChild) {
            addImageButton.removeChild(addImageButton.firstChild);
        }

        var file = fileInput.files[0];
        var image = document.createElement('img');
        image.src = URL.createObjectURL(file);
        image.style.width = '100%';
        image.style.height = '100%';
        image.style.objectFit = 'cover';
        addImageButton.appendChild(image);
    });

    document.getElementById('submitBtn').addEventListener('click', function() {
        document.getElementById('signupForm').submit();
    });
});

document.querySelector('input#id_avatar').onchange = function() {
    var input = this;
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            input.parentElement.querySelector('.img-wrapper img').src = e.target.result;
        }
        reader.readAsDataURL(input.files[0]);
    }
}

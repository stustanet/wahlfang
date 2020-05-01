$("input#id_avatar").on("change", function() {
    var input = this;
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $(input).siblings('.img-wrapper').children("img").attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
})

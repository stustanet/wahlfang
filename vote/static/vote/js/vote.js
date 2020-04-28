$(".vote-list input[type='radio']").change(function() {
    const max = $(".vote-list").data("max-votes-yes");
    var count = $(".vote-list input[type='radio'][value='accept']:checked").length;
    if(count >= max) {
        $(".vote-list input[type='radio'][value='accept']:not(:checked)").prop('disabled', true);
        if(count > max){
            $(this).prop('checked', false);
        }
    } else {
        $(".vote-list input[type='radio'][value='accept']").prop('disabled', (count >= max));
    }
    $(".vote-list tfoot .yes").text((max-count) + " remaining");
});

document.querySelectorAll(".vote-list input[type='radio']").forEach(function(input) {
    input.onchange = function() {
        var voteList = document.querySelector('.vote-list');
        var max = voteList.dataset.maxVotesYes;
        var count = voteList.querySelectorAll("input[type='radio'][value='accept']:checked").length;
        if(count >= max) {
            voteList.querySelectorAll("input[type='radio'][value='accept']:not(:checked)").forEach(function(input) {
                input.disabled = true;
            });
            if(count > max){
                this.checked = false;
            }
        } else {
            voteList.querySelectorAll("input[type='radio'][value='accept']").forEach(function(input) {
                input.disabled = (count >= max);
            });
        }
        voteList.querySelector("tfoot .yes").innerText = (max-count) + " remaining";
    }
});

document.querySelectorAll("#all-yes").forEach(function(btn) {
    btn.parentNode.classList.remove('d-none');
    btn.onclick = function() {
        var voteList = document.querySelector('.vote-list');
        voteList.querySelectorAll("input[type='radio'][value='accept']").forEach(function(input) {
            input.checked = true;
            input.onchange();
        });
    }
});

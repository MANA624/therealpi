function useFreebie(){
    $.ajax({
        type: "POST",
        url: "_submit_freebie",
        traditional: true
    }).done(function(data){
        console.log($("#freebies").html($("#freebies").html()-1));
        completed();
        createAlert("success", "Success!", data)
    }).fail(function(data){
        createAlert("danger", "Oops!", data.responseText)
    });
}

function completed(){
        $("#description").html("You've successfully completed the challenge for the day!");
        $("#submit-form-div").hide();
        $("#submit-button").hide();
        $("#submit-freebie").hide();
        $("#title").html("Congrats!");
        $("#completed").html(Number($("#completed").html())+1);
    }

$(document).ready(function(){
    $("#submit-challenge-form").submit(function(event){
        var form = $('#submit-challenge-form');
        if(form[0].checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "phrase": $("#phrase").val(),
                    "token": $("#token").val()
                },
                type: "POST",
                url: "_submit_challenge",
                traditional: true
            }).done(function(data){
                // $("#submit-challenge-form")[0].reset();
                completed();
                createAlert("success", "Success!", data);
            }).fail(function(data){
                if(data.status == 418){
                    console.log($("#tries").html($("#tries").html()-1));
                }
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });

    $(".toggle-accordion").on("click", function() {
        var accordionId = $(this).attr("accordion-id"),
        numPanelOpen = $(accordionId + ' .collapse.in').length;

        $(this).toggleClass("active");


        if (numPanelOpen == 0) {
            openAllPanels(accordionId);
        } else {
            closeAllPanels(accordionId);
        }
    });


    openAllPanels = function(aId) {
        console.log("setAllPanelOpen");
        $(aId + ' .panel-collapse:not(".in")').collapse('show');
    };
    closeAllPanels = function(aId) {
        console.log("setAllPanelclose");
        $(aId + ' .panel-collapse.in').collapse('hide');
    };
});
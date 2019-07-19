function useFreebie(){
    $.ajax({
        data: {
            "day": $("#day-select").val()
        },
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
        $("#not-completed").addClass("hidden");
        $("#has-completed").removeClass("hidden");
        $("#num-completed").html(Number($("#num-completed").html())+1);
    }

$(document).ready(function(){
    $("#day-select").val("1");

    $("#submit-challenge-form").submit(function(event){
        var form = $('#submit-challenge-form');
        if(form[0].checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "phrase": $("#phrase").val(),
                    "token": $("#token").val(),
                    "day": $("#day-select").val()
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

    $("#show-pass-form").submit(function(event){
        var form = document.getElementById('show-pass-form');
        if(form.checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "pass": $("#sharon_pass").val(),
                },
                type: "POST",
                url: "_show_pass"
            }).done(function(data){
                // window.location = "/admin";
                $("#reveal_pass").text("My password is: " + data);
            }).fail(function(data){
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

    $("#day-select").change(function(){
        // console.log($("#day-select").val());

        $.ajax({
            data: {
                "day": $("#day-select").val()
            },
            type: "POST",
            url: "_get_challenge",
            traditional: true
        }).done(function(data){
            $("#top-description").html(data.description);
            if(data.completed){
                $("#not-completed").addClass("hidden");
                $("#has-completed").removeClass("hidden");
            }
            else{
                $("#not-completed").removeClass("hidden");
                $("#has-completed").addClass("hidden");
            }
            $("#tries").html(data.tries);
        }).fail(function(data){
            createAlert("danger", "Oops!", data.responseText)
        });
        event.preventDefault();
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
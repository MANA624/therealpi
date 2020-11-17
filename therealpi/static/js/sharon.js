$(document).ready(function() {
    // Create the datepicker
    $('#twenty-op').datepicker({
        uiLibrary: 'bootstrap4'
    });
    $('#start-dating').datepicker({
        uiLibrary: 'bootstrap4'
    });
    $('#pearl').datepicker({
        uiLibrary: 'bootstrap4'
    });

    var finishing_video = false;
    // Handle the video that plays
    function timeListen(){
        if(this.currentTime > this.duration-30 && !finishing_video){
            $.ajax({
                traditional: true,
                data: {
                    "challenge": '7',
                },
                type: "POST",
                url: "_submit_challenge"
            }).done(function(data){
                finishing_video = true;
                console.log("did it!")
            }).fail(function(data){
                console.log(data.responseText);
            });
        }
    }
    var video = document.getElementById("final-video");
    if(video) {
        video.addEventListener("timeupdate", timeListen, false);
    }

    $("#arrived-in-newport-btn").click(function (){
        $.ajax({
            data: {
                "msg": "Your lovely lady has arrived",
                "recipient": "matt"
            },
            type: "POST",
            url: "_send_text"
        }).done(function (data) {
            // $("#her-text-form")[0].reset();
            createAlert("success", "Hang tight!", "You will be contacted shortly")
        }).fail(function (data) {
            createAlert("danger", "Oops!", "Something went wrong. Please notify somebody ASAP")
        });
    });

    $(".cipher-submit-btn").click(function (){
        var btn_id = $(this).attr("id");
        var cipher_val = $("#text"+btn_id).val();

        $.ajax({
            traditional: true,
            data: {
                "challenge": btn_id,
                "cipher": cipher_val
            },
            type: "POST",
            url: "_submit_challenge"
        }).done(function(data){
            createAlert("success", "Congrats!", data);

            // If the update is a success, and Sharon is on level 5, send the text message
            if(btn_id == '5') {
                $.ajax({
                    data: {
                        "msg": "Hello! New information awaits you at your web page!",
                        "recipient": "sharon"  // TODO: change to "sharon"
                    },
                    type: "POST",
                    url: "_send_text"
                }).done(function (data) {
                    $("#her-text-form")[0].reset();
                    createAlert("success", "Success!", data)
                }).fail(function (data) {
                    createAlert("danger", "Oops!", data.responseText)
                });
            }
        }).fail(function(data){
            createAlert("danger", "Error!", data.responseText)
        });
    })

    $("#reset-challenges").click(function (){
        $.ajax({
            traditional: true,
            data: {},
            type: "POST",
            url: "_reset_challenges"
        }).done(function(data){
            createAlert("success", "Congrats!", data);
        }).fail(function(data){
            createAlert("danger", "Error!", data.responseText)
        });
    });


    $(document).on('submit', "#sharon-quiz-form", function(event){
        var form = document.getElementById('add-event-form');

        var date = $("#start-dating").val(),
            twenty_op = $("#twenty-op").val(),
            pearl = $("#pearl").val(),
            color1 = $("#color1").val(),
            color2 = $("#color2").val(),
            aisle = $("#aisle").val(),
            isle = $("#isle").val(),
            buttons = $("#buttons").val();
        $.ajax({
            traditional: true,
            data: {
                "challenge": '3',
                "date": date,
                "twenty_op": twenty_op,
                "pearl": pearl,
                "color1": color1,
                "color2": color2,
                "aisle": aisle,
                "isle": isle,
                "buttons": buttons,
            },
            type: "POST",
            url: "_submit_challenge"
        }).done(function(data){
            createAlert("success", "Congrats!", data);
        }).fail(function(data){
            createAlert("danger", "Error!", data.responseText)
        });
        event.preventDefault();
    });

});
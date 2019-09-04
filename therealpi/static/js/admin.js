function reset_challenges(){
    $.ajax({
        type: "POST",
        url: "_reset_challenges",
        traditional: true
    }).done(function(data){
        createAlert("success", "Success!", data)
    }).fail(function(data){
        createAlert("danger", "Oops!", data.responseText)
    });
}

function switch_proxy(direction){
    $.ajax({
        data: {
            "dir": direction
        },
        type: "POST",
        url: "_proxy_switch",
        traditional: true
    }).done(function(data){
        createAlert("success", "Success!", data)
    }).fail(function(data){
        createAlert("danger", "Oops!", data.responseText)
    });
}

$(document).ready(function(){

    $("#create-user-form").submit(function(event){
        $("#add-user-error-text").html("");
        var form = document.getElementById('create-user-form');
        if(form.checkValidity() == false){
            return false
        }
        else if($("#pass").val() !== $("#confirm-pass").val()){
            $("#add-user-error-text").html("Passwords do not match!");
            return false;
        }
        else{
            var privileges = [''];
            if($("#roommate-checkbox").is(":checked")){
                privileges.push("roommate")
            }
            if($("#employer-checkbox").is(":checked")){
                privileges.push("employer")
            }
            if($("#admin-checkbox").is(":checked")){
                privileges.push("admin")
            }
            $.ajax({
                data: {
                    "username": $("#user").val(),
                    "password": $("#pass").val(),
                    "other": privileges
                },
                type: "POST",
                url: "_create_user",
                traditional: true
            }).done(function(data){
                // window.location = "/admin";
                $("#create-user-form")[0].reset();
                createAlert("success", "Success!", data)
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });

    $("#create-job-form").submit(function(event){
        var form = $('#create-job-form');
        if(form[0].checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "heading": $("#heading").val(),
                    "dates_worked": $("#dates").val(),
                    "job_title": $("#title").val(),
                    "job_description": $("#description").val()
                },
                type: "POST",
                url: "_create_challenge"
            }).done(function(data){
                // window.location = "/admin";
                $("#create-job-form")[0].reset();
                createAlert("success", "Success!", data)
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });

    $("#create-challenge-form").submit(function(event){
        var form = $('#create-challenge-form');
        if(form[0].checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "day": $("#day").val(),
                    "passcode": $("#passcode").val(),
                    "description": $("#challenge-description").val()
                },
                type: "POST",
                url: "_create_challenge"
            }).done(function(data){
                // window.location = "/admin";
                $("#create-challenge-form")[0].reset();
                createAlert("success", "Success!", data)
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });

    $("#create-prize-form").submit(function(event){
        var form = $('#create-prize-form');
        if(form[0].checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "tokens": $("#tokens").val(),
                    "description": $("#prize-description").val()
                },
                type: "POST",
                url: "_create_prize"
            }).done(function(data){
                // window.location = "/admin";
                $("#create-challenge-form")[0].reset();
                createAlert("success", "Success!", data)
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });
});
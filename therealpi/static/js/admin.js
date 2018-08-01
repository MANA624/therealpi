$(document).ready(function(){
    $("#create-user-form").submit(function(event){
        var form = document.getElementById('create-user-form');
        if($("#pass").val() !== $("#confirm-pass").val()){
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
                dataType: "json",
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
        var form = document.getElementById('create-user-form');
        if(false){
            return false;
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
                url: "_create_job"
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
});
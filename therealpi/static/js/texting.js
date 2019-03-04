function reset_challenges(){
    $.ajax({
        type: "POST",
        url: "_call_self",
        traditional: true
    }).done(function(data){
        createAlert("success", "Success!", data)
    }).fail(function(data){
        createAlert("danger", "Oops!", data.responseText)
    });
}

$(document).ready(function(){

    $("#self-text-form").submit(function(event){
        var form = document.getElementById('self-text-form');
        console.log("Here");
        if(form.checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "msg": $("#self_body").val(),
                    "recipient": "matt"
                },
                type: "POST",
                url: "_send_text"
            }).done(function(data){
                // window.location = "/admin";
                $("#self-text-form")[0].reset();
                createAlert("success", "Success!", data)
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });

    $("#her-text-form").submit(function(event){
        var form = document.getElementById('her-text-form');
        console.log("Here");
        if(form.checkValidity() == false){
            return false
        }
        else{
            $.ajax({
                data: {
                    "msg": $("#her_body").val(),
                    "recipient": "sharon"
                },
                type: "POST",
                url: "_send_text"
            }).done(function(data){
                // window.location = "/admin";
                $("#her-text-form")[0].reset();
                createAlert("success", "Success!", data)
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });

});
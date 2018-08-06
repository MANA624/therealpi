function validateEmail(email) {
    var re = /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
    return re.test(String(email).toLowerCase());
}


$(document).ready(function(){
    $("#send-email-form").submit(function(event){
        $("#send-email-error-text").html("");
        var form = $('#send-email-form');
        if(form[0].checkValidity() == false){
            return false
        }
        else if(!validateEmail($("#your-email").val())){
            // console.log(validateEmail($("#your-email")));
            $("#send-email-error-text").html("Not a valid email address!");
            return false;
        }
        else{
            $.ajax({
                data: {
                    "name": $("#your-name").val(),
                    "email": $("#your-email").val(),
                    "subject": $("#subject").val(),
                    "message": $("#email-content").val()
                },
                type: "POST",
                url: "_send_email"
            }).done(function(data){
                // window.location = "/admin";
                $("#send-email-form")[0].reset();
                createAlert("success", "Success!", data)
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();

        }
    });
});
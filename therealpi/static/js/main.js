$( document ).ready(function() {
    $("#submit-login").click(function(){
        $("#login-form").submit();
    });

    $(".modal-form").keypress(function (e) {
        if(e.which == 13){
            $("#login-form").submit();
            return false;
        }
    });

    $("#login-form").on('submit', function(event) {
        if($("#login-username").val() == "" || $("#login-pass").val() == ""){
            $("#login-error-message").html("One or more empty fields!");
            return false;
        }
        $.ajax({
           data: {
               username : $("#login-username").val(),
               password : $("#login-pass").val()
           },
            type: "POST",
            url: "_check_login"

        }).done(function(data){
            window.location = "/";
        }).fail(function(data){
            $("#login-error-message").html(data.responseText)
        });
        event.preventDefault();
    });
});

var createAlert = function(type, title, message){
    // html = '<div class="alert alert-success alert-dismissible fade show" hidden><button type="button" class="close" data-dismiss="alert">&times;</button><strong>Success!</strong> This alert box could indicate a successful or positive action. </div>';
    d = document.createElement('div');
    $(d).addClass("alert alert-" + type + " alert-dismissible fade show")
        .html('<button type="button" class="close" data-dismiss="alert">&times;</button><strong>' + title + '</strong> ' + message)
        .hide()
        .appendTo($("#alert-box"));

    $(d).slideDown("medium");
};

// createAlert("success", "Yay!", "This is a successful and really dope message, yo");
// createAlert("danger", "eeehhh...", "Look out, yo!");

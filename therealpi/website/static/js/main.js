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
            alert("One or more empty fields!");
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
            if(data.error){
                alert(data.error);
            }
            else{
                window.location = "/";
            }
        });
        event.preventDefault();
    });
});

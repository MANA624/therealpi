$(document).ready(function(){
    $("#create-user-form").submit(function(){
        var form = document.getElementById('create-user-form');
        if(form.checkValidity() == false){
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
                if(data.error){
                    alert(data.error);
                }
                else{
                    window.location = "/admin";
                }
            });
            event.preventDefault();

        }
    });
});
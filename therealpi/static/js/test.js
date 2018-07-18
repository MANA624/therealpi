$(document).ready(function () {

  /* BEGIN REGION: CALENDAR */

    

  /* END REGION: CALENDAR */
  /* BEGIN REGION: FORM*/
    // Code for the date picker
    $('#datepicker').datepicker({
        uiLibrary: 'bootstrap4'
    });

    $(document).on('submit', "#add-event-form", function(event){
        var form = document.getElementById('add-event-form');

        if(form.checkValidity() == false || $("#datepicker").val() == ""){
            return false;
        }
        else if($("#datepicker").val() === ""){

        }
        else{
            $.ajax({
                data: {
                    "Title": $("#title").val(),
                    "Special Reminders": $("#special").val(),
                    "Date": $("#datepicker").val(),
                    "Hour": $("#hour").val(),
                    "Minute": $("#minute").val()
                },
                type: "POST",
                url: "_add_event"
            }).done(function(data){
                $('#add-event-form')[0].reset();
                  createAlert("success", "Success!", data);
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();
        }
    });
});
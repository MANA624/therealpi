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
        if($("#datepicker").val() == ""){
            $("#add-event-error-text").html("You must pick a date!");
        }
        else{
            var title = $("#title").val(),
                special = $("#special").val(),
                date = $("#datepicker").val(),
                hour = $("#hour").val(),
                minute = $("#minute").val(),
                send_text = $("#send-text").is(":checked");
            $.ajax({
                data: {
                    "title": title,
                    "more_info": special,
                    "date": date,
                    "hour": hour,
                    "minute": minute,
                    "send_text": send_text
                },
                dataType: 'json',
                type: "POST",
                url: "_add_event"
            }).done(function(data){
                $('#add-event-form')[0].reset();
                createAlert("success", "Success!", data.message);
                var eventData = {
                    'title': data.event["title"],
                    'start': date.event["start"]
                };
                $('#calendar').fullCalendar('renderEvent', eventData, true);
            }).fail(function(data){
                createAlert("danger", "Oops!", data.responseText)
            });
            event.preventDefault();
        }
    });
});
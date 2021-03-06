$(document).ready(function() {
    var toDollars = function(num){
        return (Math.ceil(num*100) / 100).toFixed(2)
    };

    $(document).on('submit', "#cost-form", function (event) {
        var total = Number($("#rent").val()) +
            Number($("#water").val()) +
            Number($("#trash").val()) +
            Number($("#util").val());

        $("#price").html(total);

        var ryanTotal = total / 4,
            aaronTotal = total / 4,
            mattTotal = total / 4,
            michaelTotal = total / 4,
            ryanLess = Number($("#ryan-amount").val()),
            aaronLess = Number($("#aaron-amount").val()),
            mattLess = Number($("#matt-amount").val()),
            michaelLess = Number($("#michael-amount").val());

        ryanTotal += -ryanLess*3/4 + aaronLess/4 + mattLess/4 + michaelLess/4;
        aaronTotal += ryanLess/4 - aaronLess*3/4 + mattLess/4 + michaelLess/4;
        mattTotal += ryanLess/4 + aaronLess/4 - mattLess*3/4 + michaelLess/4;
        michaelTotal += ryanLess/4 + aaronLess/4 + mattLess/4 - michaelLess*3/4;

        $("#ryan-price").html(toDollars(ryanTotal));
        $("#aaron-price").html(toDollars(aaronTotal));
        $("#matt-price").html(toDollars(mattTotal));
        $("#michael-price").html(toDollars(michaelTotal));
        event.preventDefault();
    });

    $("#save").on('click', function(){
        var rent1 = $("#rent").val(),
            rent2 = $("#water").val(),
            rent3 = $("#trash").val(),
            rent4 = $("#util").val(),
            ryan1 = $("#ryan-amount").val(),
            ryan2 = $("#ryan-reason").val(),
            aaron1 = $("#aaron-amount").val(),
            aaron2 = $("#aaron-reason").val(),
            matt1 = $("#matt-amount").val(),
            matt2 = $("#matt-reason").val(),
            michael1 = $("#michael-amount").val(),
            michael2 = $("#michael-reason").val();
        $.ajax({
            traditional: true,
            data: {
                "rent": [rent1, rent2, rent3, rent4],
                "ryan": [ryan1, ryan2],
                "aaron": [aaron1, aaron2],
                "matt": [matt1, matt2],
                "michael": [michael1, michael2]
            },
            type: "POST",
            url: "_update_roommate"
        }).done(function(data){
            createAlert("success", "Congrats!", data);
        }).fail(function(data){
            createAlert("danger", "Error!", data.responseText)
        });

    })
});
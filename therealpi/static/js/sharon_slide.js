$(document).ready(function() {
    // Must swap tiles into one of the presents.
    // swapTiles("cell11", "cell12");
    // setTimeout(() => {  swapTiles("cell11", "cell13"); }, 2000);
    sequence = sequence.split(" ");
    // console.log(sequence)
    for(var curr_tile=0; curr_tile<25; curr_tile++){
        compareName = "tile" + sequence[curr_tile];
        console.log(compareName);
        for(var search_tile=curr_tile+1; search_tile<25; search_tile++){
            var cell = document.getElementById("cell"+numToRC(search_tile));
            var tile = cell.className;

            if(tile == compareName){
                // console.log(search_tile);
                swapTiles("cell" + numToRC(curr_tile), "cell" + numToRC(search_tile));

                break;
            }
        }
        // return;

    }

    function numToRC(num){
        return String(Math.floor(num/5)+1) + String((num % 5)+1);
    }
});

function swapTiles(cell1,cell2) {
    var temp = document.getElementById(cell1).className;
    document.getElementById(cell1).className = document.getElementById(cell2).className;
    document.getElementById(cell2).className = temp;

    // Check if she beat the game
    if(checkFinished()){
        $.ajax({
            traditional: true,
            type: "POST",
            data: {
                "challenge": 1
            },
            url: "_submit_challenge"
        }).done(function(data){
            createAlert("success", "Congrats!", data);
        }).fail(function(data){
            createAlert("danger", "Error!", data.responseText)
        });
    }
}

function shuffle() {
    //Use nested loops to access each cell of the 4x4 grid
    for (var row=1;row<=5;row++) { //For each row of the 4x4 grid
        for (var column=1;column<=5;column++) { //For each column in this row

            var row2=Math.floor(Math.random()*5 + 1); //Pick a random row from 1 to 4
            var column2=Math.floor(Math.random()*5 + 1); //Pick a random column from 1 to 4

            swapTiles("cell"+row+column,"cell"+row2+column2); //Swap the look & feel of both cells
        }
    }
}

function clickTile(row,column) {
    var cell = document.getElementById("cell"+row+column);
    var tile = cell.className;
    if (tile!="tile25") {
        //Checking if white tile on the right
        if (column<5) {
            if ( document.getElementById("cell"+row+(column+1)).className=="tile25") {
                swapTiles("cell"+row+column,"cell"+row+(column+1));
                return;
            }
        }
        //Checking if white tile on the left
        if (column>1) {
            if ( document.getElementById("cell"+row+(column-1)).className=="tile25") {
                swapTiles("cell"+row+column,"cell"+row+(column-1));
                return;
            }
        }
        //Checking if white tile is above
        if (row>1) {
            if ( document.getElementById("cell"+(row-1)+column).className=="tile25") {
                swapTiles("cell"+row+column,"cell"+(row-1)+column);
                return;
            }
        }
        //Checking if white tile is below
        if (row<5) {
            if ( document.getElementById("cell"+(row+1)+column).className=="tile25") {
                swapTiles("cell"+row+column,"cell"+(row+1)+column);
                return;
            }
        }
    }

}

function checkFinished(){
    var counter = 1
    var numDigits = 1;
    for(var i=1; i<=5; i++){
        for(var j=1; j<=5; j++){
            var cell = document.getElementById("cell"+i+j);
            var tile = cell.className;
            if(tile.substr(4, numDigits) != String(counter)){
                return false;
            }
            counter++;
            if(counter == 10){
                numDigits++;
            }
        }
    }
    return true;
}

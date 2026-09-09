let board = [1,2,3,4,5,6,7,8,0];

shuffle();

draw();

function shuffle(){

    for(let i=0;i<200;i++){

        let neighbors = getNeighbors();

        let move = neighbors[Math.floor(Math.random()*neighbors.length)];

        swap(move);

    }

}

function draw(){

    let div=document.getElementById("board");

    div.innerHTML="";

    board.forEach((value,index)=>{

        let tile=document.createElement("div");

        tile.className="tile";

        if(value===0){

            tile.classList.add("empty");

            tile.innerHTML="";

        }

        else{

            tile.innerHTML=value;

        }

        tile.onclick=function(){

            clickTile(index);

        }

        div.appendChild(tile);

    });

}

function clickTile(index){

    let empty=board.indexOf(0);

    let possible=getAdjacent(index);

    if(possible.includes(empty)){

        [board[index],board[empty]]=[board[empty],board[index]];

        draw();

        checkWin();

    }

}

function getAdjacent(index){

    let arr=[];

    let row=Math.floor(index/3);

    let col=index%3;

    if(row>0) arr.push(index-3);

    if(row<2) arr.push(index+3);

    if(col>0) arr.push(index-1);

    if(col<2) arr.push(index+1);

    return arr;

}

function getNeighbors(){

    let empty=board.indexOf(0);

    return getAdjacent(empty);

}

function swap(index){

    let empty=board.indexOf(0);

    [board[index],board[empty]]=[board[empty],board[index]];

}

function checkWin(){

    let win=[1,2,3,4,5,6,7,8,0];

    for(let i=0;i<9;i++){

        if(board[i]!=win[i])

            return;

    }

    document.getElementById("board").style.display="none";

    document.getElementById("winner").style.display="block";

}
<script>
window.onload = function(){

    const music = document.getElementById("bgMusic");

    music.play().catch(function(error){
        console.log("Autoplay blocked:", error);
    });

};
</script>

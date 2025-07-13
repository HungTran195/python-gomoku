'use strict';
const socket = io().connect();
const greetingCard = $('#greeting-card');
const greetingContent = $('#greeting-content');
const gameBoard = document.getElementById("game-board");

const REMATCH_REQUEST_COMMAND = 'request';
const REMATCH_ACCEPT_COMMAND = 'accept';
const REMATCH_START_COMMAND = 'start_rematch';

const GAME_TYPE_SINGLE='single';
const GAME_TYPE_PVP='pvp';

const initialState = {
    gameID: 0,
    gameType: '',
    playerIndex: 0,
    playerName: '',
    opponentName: '',
    isTurn: true,
    score: [0, 0],
    lastMoveIndex: [],
};

const state = initialState;

const showGreetingCard = () =>{
    greetingCard.removeClass('hidden');
} 

const hideGreetingCard =() =>{
    greetingCard.addClass('hidden');
};

const displayLoadingCard = (extra_context='') =>{
    const markup = `
        <div class=" greeting-wrapper p-3 w-100">
            <div class="fs-3 text-warning text-center">
                ${extra_context ?? `
                    <p>
                    ${extra_context}
                    </p>
                `}
                <p>
                    Waiting for the response
                </p>
                <div class="spinner-grow text-light loader" role="status"></div>
            </div>
        </div>
    `;
    greetingContent.empty().append(markup);
    showGreetingCard();
}

const removeColorOfLastMove = () =>{
    $(`#cell-${state.lastMoveIndex[0]}-${state.lastMoveIndex[1]}`).removeClass('latest-index');
};

const resetBoard =() =>{
    for(let node of $('.winning-index')){
        node.removeChild(node.firstChild);
    };

    for(let node of $('.opponent-node')){
        node.classList.add('node');
        node.classList.remove('opponent-node', 'winning-index', 'latest-index');
    };

    for(let node of $('.my-node')){
        node.classList.add('node');
        node.classList.remove('my-node', 'winning-index', 'latest-index');
    };
};

$('#start-form').submit( (event) =>{
    event.preventDefault();
    const gameType= $('#start-form input[name=game-type]:checked').val();
    const playerName= $('#start-form input[name=player-name]').val();
    hideGreetingCard();
    resetBoard();

    state.gameType = gameType;
    state.playerName = playerName;
    if(gameType === GAME_TYPE_PVP && $('#start-form input[name=join-game-btn]').is(':checked')){
        // Join an active game
        state.gameID = parseInt($('#start-form input[name=active-game-id]').val());
        state.playerIndex = 2;
        joinGame();
    }
    else{
        // Create new game
        state.gameID = parseInt($('#game-id').text())
        state.playerIndex = 1;

        initGame();
    }
});

$('#start-form input[name=game-type]').on('change', ()=>{
    if($('#start-form input[name=game-type]:checked').val() === 'single'){
        $('#game-info-wrapper').addClass('opacity-50');
        $('#join-game input').val('');
        $('#join-game input').prop("disabled", true);
    }
    else {
        $('#game-info-wrapper').removeClass('opacity-50');
        $('#join-game input').prop("disabled", false);
        
    }
});
$('#start-form input[name=join-game-btn]').on('change', ()=>{
    if($('#start-form input[name=join-game-btn]').is(':checked')){
        $('#game-info').addClass('hidden');
        $('#join-game').removeClass('hidden');
        $('#join-game input').prop("required", true);
    }
    else{
        $('#game-info').removeClass('hidden');
        $('#join-game').addClass('hidden');
        $('#join-game input').prop("required", false);
    }
});

$('#invited-form').submit( (event) =>{
    event.preventDefault();
    const playerName= $('#invited-form input[name=player-name]').val();
    state.playerName = playerName;
    joinGame();
    $('#invited-form')[0].reset();
});

const addGameBoardHandler =()=>{
    $('#game-board').on('click',(event)=>{
        const target = event.target.id;
        if (state.isTurn & target.includes("cell")){
            if(event.target.classList.contains('node')){
                // Get move index from ID. Example: cell-4-5 => move index: [4,5]
                const moveIndex = [ parseInt(target.split('-')[1]),  parseInt(target.split('-')[2])]; 
                sendMove(moveIndex);
                updateBoard(moveIndex);
                state.isTurn = false;
                updateTurnStatus();
            }
        };
    });
};

const rematch =() =>{
    requestRematch();
    $('#game-over-banner').addClass('hidden');
};

const gameOver = (data) =>{
    if(data.winning_line){
        const isWinner = data.winner === state.playerIndex ? true : false
        displayWinningLine(data.winning_line);
        updateScore(isWinner);
        setTimeout(() => {
            if(isWinner) {
                $('#result').empty().append(`
                    <span><i class="fas fa-trophy px-1"></i></span>
                    You Won
                    <span><i class="fas fa-trophy px-1"></i></span>
                `);
            }

            else {
                $('#result').empty().append(`
                    <span><i class="fas fa-sad-tear px-1"></i></span>
                    You Lost
                    <span><i class="fas fa-sad-tear px-1"></i></span>
                `)
            };

            $('#game-over-banner').removeClass('hidden');
        }, 1000);
    }
    else{
        // game tie
        setTimeout(() => {
            $('#result').empty().append(`
                <span><i class="fas fa-smile-beam px-1"></i></i></span>
                Game Tie
                <span><i class="fas fa-smile-beam px-1"></i></i></span>
            `)

            $('#game-over-banner').removeClass('hidden');
        }, 1000);
    }
};

const updateBoard = (moveIndex)=>{
    removeColorOfLastMove();

    if (!(moveIndex[0] === state.lastMoveIndex[0]
            && moveIndex[1] === state.lastMoveIndex[1])){
        state.lastMoveIndex = moveIndex;
        const cellID = `#cell-${moveIndex[0]}-${moveIndex[1]}`;
        if(state.isTurn){
            $(cellID).addClass('my-node latest-index');
        }
        else $(cellID).addClass('opponent-node latest-index');;
        
        $(cellID).removeClass('node');
    }
};

const updateTurnStatus = ()=>{
    if(state.isTurn) {
        document.getElementById('turn-status').childNodes[1].textContent= 'Your Turn';
        $('#turn-status').addClass('my-turn');
        $('#turn-status').removeClass('opponent-turn');

    }
    else {
        document.getElementById('turn-status').childNodes[1].textContent= 'Thinking...';
        $('#turn-status').addClass('opponent-turn');
        $('#turn-status').removeClass('my-turn');
    }
};

const updateScore = (isWinner) =>{
    if(isWinner){
        state.score[0] ++;
        $('#score-0').text(state.score[0]);
    }
    else{
        state.score[1] ++;
        $('#score-1').text(state.score[1]);
    };
};

const displayWinningLine= (winningLine) =>{
    for (let moveIndex of winningLine){
        $(`#cell-${moveIndex[0]}-${moveIndex[1]}`).addClass('winning-index')
        $(`#cell-${moveIndex[0]}-${moveIndex[1]}`).prepend('<i class="fas fa-star"></i>');
    }
};

const initSinglePlayerGame = () =>{
    $('#turn-status').removeClass('opacity-25');
    updateTurnStatus(true)
    const markup = `
        <div class="d-flex justify-container-center align-items-center fs-4">
            <div class="d-flex justify-container-center align-items-center">
                <p>${state.playerName}</p>
                <p id="score-0" class="ps-2 text-primary">0</p>
            </div>
            <p class="px-2 text-primary">-</p>
            <div class="d-flex justify-container-center align-items-center">
                <p id="score-1" class="pe-2 text-primary" >0</p>
                <p>Computer</p>
            </div>
        </div>
    `;
    $('#score').empty().append(markup);
};

const initPvPGame = (data) =>{
    if(state.playerIndex == 1){
        state.opponentName = data.player_names.player_2;
    }
    else{
        state.opponentName = data.player_names.player_1;
    }
    $('#turn-status').removeClass('opacity-25');
    if(data.turn === state.playerIndex){
        state.isTurn = true;
    }
    else state.isTurn = false;
    updateTurnStatus(state.isTurn)
    const markup = `
        <div class="d-flex justify-container-center align-items-center fs-4">
            <div class="d-flex justify-container-center align-items-center">
                <p id="player-name" >${state.playerName}</p>
                <p id="score-0" class="ps-2 text-primary">0</p>
            </div>
            <p class="px-2 text-primary">-</p>
            <div class="d-flex justify-container-center align-items-center">
                <p id="score-1" class="pe-2 text-primary" >0</p>
                <p id="opponent-name" >${state.opponentName}</p>
            </div>
        </div>
    `;
    $('#score').empty().append(markup);
};

const startGame = ()=>{
    addGameBoardHandler();
    hideGreetingCard();
}

const endGame = ()=>{
    const markup = `
        <div class=" greeting-wrapper p-3 w-100">
            <div class="fs-5 text-warning text-center">
                <p>
                    Your friend just left!
                </p>
                <a href="/" >
                    <button class="btn border-radius-8 btn-danger">New Game</button>
                </a>
            </div>
        </div>
    `;
    greetingContent.empty().append(markup);
    showGreetingCard();
};

/*
 * Emit socket IO messages
 */
const initGame= ()=>{
    const data = {
        gameID: state.gameID,
        gameType: state.gameType,
        playerName: state.playerName,
    }
    socket.emit('init_game', data);
    
    displayLoadingCard(`Game ID: ${state.gameID}`)
}

const joinGame =() =>{
    const data = {
        gameID: state.gameID,
        playerName: state.playerName,
    }
    socket.emit('join_current_game', data);
}

const sendMove=(moveIndex) => {
    const data = {
        gameID: state.gameID,
        moveIndex: moveIndex,
    };
    socket.emit('move', data);
};

const requestRematch = () =>{
    const data = {
        gameID: state.gameID,
        command: REMATCH_REQUEST_COMMAND,
    };
    socket.emit('rematch', data);
    displayLoadingCard();
};

const acceptRematch =   () =>{
    const data = {
        gameID: state.gameID,
        command: REMATCH_ACCEPT_COMMAND,
    };
    socket.emit('rematch', data);
}

/*
 * Socket IO messages handler
 * Handle all incoming messages from socketIO
 */

socket.on('start_game', (data) =>{
    if(data.status === 'success'){
        if(state.gameType === GAME_TYPE_SINGLE){
            initSinglePlayerGame();
        }
        else{
            initPvPGame(data);
        };
        startGame();
    } 
});


socket.on('move', function (data) {
    if(!state.your_turn && data.status === 'success'){
        updateBoard(data.move_index);
        state.isTurn = !state.isTurn;
        updateTurnStatus();
        if(data.game_over){
            gameOver(data);   
        }
    }
});

socket.on('rematch', (data) =>{
    $('#game-over-banner').addClass('hidden');
    const command = data.command;
    if (state.gameType === GAME_TYPE_SINGLE){
        $('#game-over-banner').addClass('hidden');
        state.isTurn=data.your_turn;
        state.lastMoveIndex = [];
        updateTurnStatus();
        resetBoard();
        state.isTurn = 1;
        hideGreetingCard();

    }
    else {
        if (command === REMATCH_REQUEST_COMMAND){
            // Received rematch request from opponent
            const markup = `
                <div class="greeting-wrapper p-3 w-100">
                    <div class="fs-3 text-warning text-center">
                        <p>
                            Your friend is challenging for a rematch
                        </p>
                        <div class="text-center">
                            <button onClick="acceptRematch()" class="btn border-radius-8 btn-primary">Let's go</button>
                        </div>
                    </div>
                </div>
            `;
            greetingContent.empty().append(markup);
            showGreetingCard();
        }
    
        else if (command === REMATCH_START_COMMAND){
            // A rematch is initiated, proceed for a new game
            $('#game-over-banner').addClass('hidden');
            if(data.player_turn === state.playerIndex){
                state.isTurn = true;
            }
            else state.isTurn = false;
            state.lastMoveIndex = [];
            updateTurnStatus();
            resetBoard();
            hideGreetingCard();
        }
    }
});

socket.on('end_game', (data)=>{
    endGame();
});

socket.on('error', (data)=>{
    const markup = `
        <div class=" greeting-wrapper p-3 w-100">
            <div class="fs-3 text-warning text-center">
                <p>
                    ${data.error_msg}
                </p>
                <a href="/" class="btn btn-danger pe-auto" >Restart</a>
            </div>
        </div>
    `;
    greetingContent.empty().append(markup);
    showGreetingCard();
});

socket.on("connect_error", () => {
});

const init= () =>{
    showGreetingCard();
    $('#game-over-banner').addClass('hidden');

};

// Copy game ID to clipboard
const copyGameId = () => {
    const gameId = document.getElementById('game-id').textContent.trim();
    const copyBtn = event.target.closest('button');
    const originalText = copyBtn.innerHTML;
    
    // Try modern clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(gameId).then(() => {
            // Show feedback to user
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            copyBtn.classList.remove('btn-outline-secondary');
            copyBtn.classList.add('btn-success');
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-outline-secondary');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy game ID: ', err);
            fallbackCopyTextToClipboard(gameId, copyBtn, originalText);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyTextToClipboard(gameId, copyBtn, originalText);
    }
};

// Fallback copy method for older browsers
const fallbackCopyTextToClipboard = (text, copyBtn, originalText) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            // Show feedback to user
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            copyBtn.classList.remove('btn-outline-secondary');
            copyBtn.classList.add('btn-success');
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-outline-secondary');
            }, 2000);
        } else {
            alert('Failed to copy game ID. Please copy manually: ' + text);
        }
    } catch (err) {
        console.error('Fallback copy failed: ', err);
        alert('Failed to copy game ID. Please copy manually: ' + text);
    }
    
    document.body.removeChild(textArea);
};

init();
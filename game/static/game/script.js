'use strict';
const socket = io.connect();

const board = document.getElementById('board');
const loader = document.querySelector('.loader');

const overlay = document.querySelector('.overlay');
const starting_box = document.getElementById('starting-box');
const btn_start = document.querySelector('.btn-start');
const turn_sign = document.getElementById('turn-sign');
const allCells = document.querySelectorAll('.cell');
const score_opponent = document.getElementById('score2');


let move_index, isturn, player_name = '', is_host;
// Get game id from server
const get_room_url = function () {
    let room_url = document.getElementById('room_url');
    let game_id, turn;
    if (room_url) {
        room_url = room_url.textContent.split('/');
        if (room_url.length > 3) {
            game_id = room_url[room_url.length - 1].toString();
            is_host = 1;
        }
        else {
            game_id = '';
        }
    }
    // In case joined by invited linked, use URL to get game id
    else {
        let current_page = window.location.href;
        current_page = current_page.split('/');
        if (current_page.length > 3) {
            game_id = current_page[current_page.length - 1].toString();
            is_host = 0;
        }
    }
    if (!game_id) {
        alert('There are no available room, please try again later');
    }
    return game_id;
};
const game_id = get_room_url();

// Initialise page with hidden tags
const init = function (mode = '') {
    if (mode === 'init') {
        overlay.classList.remove('hidden');
    }
    if (is_host) {
        starting_box.classList.add('hidden');
    }
    document.querySelector('.new-game-box').classList.add('hidden');
    document.getElementById('replay-request').classList.remove('hidden');
    document.getElementById('wait-for-replay').classList.add('hidden');
    document.getElementById('replay-confirm').classList.add('hidden');
    document.getElementById('result-banner').classList.add('hidden');
    document.getElementById('replay-container').classList.add('hidden');
}
init('init');

const play_with_ai = function () {
    document.getElementById('choose-game-type').classList.add('hidden');
    overlay.classList.add('hidden');
    isturn = 1;
    turn_sign.style.backgroundColor = '#77f077';
    socket.emit('play_with_ai', { game_id: game_id });
}
socket.on('play_with_ai', function (data) {

});

const play_with_human = function () {
    document.getElementById('choose-game-type').classList.add('hidden');
    starting_box.classList.remove('hidden');
}

// Get typed name 
// Send game infor to server and wait for other player to join game
const start_PvP_game = function () {
    player_name = document.getElementById("get-name-box").value;
    if (player_name) {
        if (is_host) {
            let msg = document.getElementById("welcome-msg").textContent;
            msg = msg + player_name + ',';
            document.getElementById("welcome-msg").textContent = msg
            document.querySelector('.new-game-box').classList.remove('hidden');
        }
        document.getElementById('name-box').classList.add('hidden');
        socket.emit('start_PvP_game', { game_id: game_id, player_name: player_name, is_host: is_host });
    }
}
// Incase user hit "Enter" key
// Call start_PvP_game function and continue
document.getElementById('get-name-box').addEventListener('keydown', (e) => {
    if (e.key == 'Enter') {
        start_PvP_game();
    }
})

// Handle received message from server to start game
socket.on('start_PvP_game', function (data) {
    // Display error message if:
    // Room is full or Wrong room id or Room is closed
    if (data.err_msg) {
        document.querySelector('.error').classList.remove('hidden');
        $('#error_msg').append(data.err_msg + '<br>');
    }
    isturn = data.is_turn;

    if (isturn) turn_sign.style.backgroundColor = '#77f077';
    else turn_sign.style.backgroundColor = '#9a9a9a';

    document.getElementById('player1').children[0].textContent = player_name;
    document.getElementById('player2').children[0].textContent = data.opponent;
    document.querySelector('.bottom-bar').classList.remove('hidden');

    overlay.classList.add('hidden');
    starting_box.classList.add('hidden');

});



// Change color of winning nodes
const draw_winning_line = function (line, is_winner) {
    line.forEach(element => {
        document.getElementById(`${element}`).classList.add('winner-nodes');
    });
}

const draw_winner = function (line, is_winner) {
    if (line.length !== 0) {
        draw_winning_line(line, is_winner);
        if (is_winner) {
            document.getElementById('result-banner').classList.remove('hidden');
            document.getElementById('result-banner').children[0].textContent = 'You Win!'
            let score = document.getElementById('score1').children[0].textContent;
            document.getElementById('score1').children[0].textContent = parseInt(score) + 1
        }

        else {
            document.getElementById('result-banner').classList.remove('hidden');
            document.getElementById('result-banner').children[0].textContent = 'You Lose!'

            let score = document.getElementById('score2').children[0].textContent;
            document.getElementById('score2').children[0].textContent = parseInt(score) + 1
        }
    }
    else {
        document.getElementById('result-banner').classList.remove('hidden');
        document.getElementById('result-banner').children[0].textContent = 'Game Draw!'
    }
    window.setTimeout(() => {
        document.getElementById('replay-container').classList.remove('hidden')
    }, 1000);
}

// Process received message from server to display move
const updateMove = function (turn_of_current_move, move_index) {
    let move = document.getElementById(move_index);
    if (move) {
        if (turn_of_current_move) move.textContent = 'X';
        else move.textContent = 'O';
    }
};

// get message from server
socket.on('move', function (data) {
    // $('#log').append('<br>Received: ' + msg.data); 
    console.log(data)
    if ('err_msg' in data) {
        document.querySelector('.error').classList.remove('hidden');
        $('#error_msg').append(data.err_msg + '<br>');
    }
    updateMove(data.turn_of_current_move, data.move_index);
    if (data.is_turn == 2) {
        isturn = 0;
        draw_winner(data.winning_line_index, data.is_winner);

    }
    else isturn = data.is_turn;

    if (isturn) turn_sign.style.backgroundColor = '#77f077';
    else turn_sign.style.backgroundColor = '#9a9a9a';

});

/* Socket listen on "end_game" from server, if one player left game*/
socket.on('end_game', function (data) {
    isturn = data.is_turn;
    document.querySelector('.error').classList.remove('hidden');
    $('#error_msg').append(data.msg + '<br>');
    overlay.classList.toggle('hidden');
})



// This function is used for user to create room 
// and will be update in the future
const update_room = function (data) {
    if (data.status == 'success') {
        room_message.textContent = 'Room is created';
    }
    else {
        room_message.textContent = 'Room name is taken, please pick another one';
    }
}

// The following code are used to handle "Play Again" request

/* Function "request_replay": 
    -- send request to sever
    -- wait for response from server*/
const request_replay = function () {
    socket.emit('request_replay', { game_id: game_id });
    document.getElementById('replay-request').classList.add('hidden');
    document.getElementById('wait-for-replay').classList.remove('hidden');
};

/* Fucntion "accept_replay": 
    -- send "accept" response to severz
    -- wait for server to create a new match */
const accept_replay = function () {
    socket.emit('accept_replay', { game_id: game_id });
    document.getElementById('replay-confirm').classList.add('hidden');
    document.getElementById('wait-for-replay').classList.remove('hidden');
};

const reset_game = function () {
    document.getElementById('replay-confirm').classList.add('hidden');
}

/* Socket listen on request_replay from server:
    -- render replay confirm box and send confirm msg to server */
socket.on('request_replay', function (data) {
    document.getElementById('replay-confirm').classList.remove('hidden');
    document.getElementById('replay-request').classList.add('hidden');

});

/* Socket listen on a msg "replay" from server:
    -- reset play board and start a new game  */
socket.on('replay', function (data) {
    for (const element of allCells) {
        if (element.classList.contains('winner-nodes')) {
            element.classList.remove('winner-nodes')
        }
        element.textContent = '';
    }
    init();


    isturn = data.is_turn;

    if (isturn) turn_sign.style.backgroundColor = '#77f077';
    else turn_sign.style.backgroundColor = '#9a9a9a';

    document.getElementById('replay-container').classList.add('hidden');
});

// Check every game cells to decide 'move' by turn
for (const element of allCells) {
    element.addEventListener('click', () => {
        if (!element.textContent & isturn) {
            let box_id = element.id;
            socket.emit('move', { game_id: game_id, move_index: box_id });
        }
    });
}


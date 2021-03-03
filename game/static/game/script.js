'use strict';
const socket = io.connect();

const allCells = document.querySelectorAll('.cell');
const overlay = document.querySelector('.overlay');
const lobby = document.querySelector('.lobby');
const starting_box = document.getElementById('starting-box');
const loader = document.querySelector('.loader');
const btn_start = document.querySelector('.btn-start');
const board = document.getElementById('board');
const turn_sign = document.getElementById('turn-sign');
let move_index, isturn;

// Get game id from server
const get_room_url = function () {
    let room_url = document.getElementById('room_url');
    let game_id, turn;
    if (room_url) {
        room_url = room_url.textContent.split('/');
        if (room_url.length > 3) {
            game_id = room_url[room_url.length - 1].toString();
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
        }
    }
    return game_id;
};

const game_id = get_room_url();


// Send message to server and wait for other player join game
const start_game = function () {
    btn_start.classList.toggle('hidden');
    loader.classList.toggle('hidden');
    socket.emit('start_game', game_id);
}

// Handle received message from server to start game
socket.on('start_game', function (data) {
    // Display error message if:
    // Room is full or Wrong room id or Room is closed
    if (data.err_msg) {
        board.classList.add('hidden');
        document.querySelector('.error_msg').classList.remove('hidden');
        $('#error_msg').append(data.err_msg + '<br>');
    }
    isturn = data.turn;

    if (isturn) turn_sign.style.backgroundColor = '#77f077';
    else turn_sign.style.backgroundColor = '#9a9a9a';

    overlay.classList.add('hidden');
    starting_box.classList.add('hidden');
    board.classList.remove('hidden');
});

// Change color of winning nodes
const draw_winning_line = function (line, iswinner) {
    console.log('winner');

    document.querySelector('.player-win').classList.remove()
    line.forEach(element => {
        document.getElementById(`${element}`).classList.add('winner');

    });
}

// Process received message from server to display move
const updateMove = function (move_id, move_index) {
    let move = document.getElementById(move_index);
    if (move) {
        if (move_id) move.textContent = 'X';
        else move.textContent = 'O';
    }
};
// get message from server
socket.on('move', function (data) {
    // $('#log').append('<br>Received: ' + msg.data); 
    if ('err_msg' in data) {
        document.querySelector('.error_msg').classList.remove('hidden');
        $('#error_msg').append(data.err_msg + '<br>');
    }
    updateMove(data.move_id, data.move_index);
    if (data.is_winner) {
        isturn = 0;
        draw_winning_line(data.winning_line, 0);
    };
    isturn = data.turn;
    if (isturn) turn_sign.style.backgroundColor = '#77f077';
    else turn_sign.style.backgroundColor = '#9a9a9a';

});

// If one player left game, stop game
socket.on('end_game', function (data) {
    isturn = data.turn;
    document.querySelector('.error_msg').classList.remove('hidden');
    $('#msg').append(data.msg + '<br>');
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


// Check every game cells to decide 'move' by turn
for (const element of allCells) {
    element.addEventListener('click', () => {
        if (!element.textContent & isturn) {
            let box_id = element.id;
            socket.emit('move', { game_id: game_id, move_index: box_id });
        }
    });
}


//  TESITING
// overlay.classList.add('hidden');
// starting_box.classList.add('hidden');
// board.classList.remove('hidden');
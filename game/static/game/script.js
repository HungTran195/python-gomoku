'use strict';
// let turn = true;
const socket = io.connect();

const play_board = document.getElementById('play-board');
const lobby = document.getElementById('lobby');

// Get game id from server
let game_id;
let room_url = document.getElementById('room_url');
if (room_url) {
    room_url = room_url.textContent.split('/');
    if (room_url.length > 3) {
        game_id = room_url[room_url.length - 1].toString();
    }
    else {
        game_id = '';
    }
    console.log(game_id);
}
// In case joined by invited linked, use URL to get game id
else {
    let current_page = window.location.href;
    current_page = current_page.split('/');
    if (current_page.length > 3) {
        game_id = current_page[current_page.length - 1].toString();
    }
    console.log(game_id)

}

let move, move_index, isturn;
let room_name = 'hello';


const allCells = document.querySelectorAll('.cell');

function start_game() {
    play_board.classList.remove('hidden');
    lobby.classList.add('hidden');
    socket.emit('start_game', game_id);
}


socket.on('start_game', function (data) {
    console.log(data);
    if (data.err_msg) {
        play_board.classList.add('hidden');
        document.querySelector('.error_msg').classList.remove('hidden');
        $('#error_msg').append(data.err_msg + '<br>');
    }
});

socket.on('move', function (data) {
    // $('#log').append('<br>Received: ' + msg.data);
    if ('err_msg' in data) {
        document.querySelector('.error_msg').classList.remove('hidden');
        $('#error_msg').append(data.err_msg + '<br>');
    }
    console.log(data);
    updateMove(data.turn, data.move_index);
});



const updateMove = function (turn, move_index) {
    move = document.getElementById(move_index);
    if (move) {
        if (turn) move.textContent = 'X';
        else move.textContent = 'O';
    }
};

const update_room = function (data) {
    if (data.status == 'success') {
        room_message.textContent = 'Room is created';
    }
    else {
        room_message.textContent = 'Room name is taken, please pick another one';
    }
}


for (const element of allCells) {
    element.addEventListener('click', () => {
        if (!element.value) {
            let box_id = element.id;
            socket.emit('move', { game_id: game_id, move_index: box_id });
        }
    });

}


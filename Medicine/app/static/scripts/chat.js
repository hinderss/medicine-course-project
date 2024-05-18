$(document).ready(function() {
    $('#gptIcon').on('click', function() {
        $('.chat').css('display', 'flex');
        $('#gptIcon').css('display', 'none');
    });

    $('#closeChatBtn').on('click', function() {
        $('.chat').css('display', 'none');
        $('#gptIcon').css('display', 'block');
    });
});

var $messages = $('.messages-content'),
i = 0;

function setDate() {
var d = new Date();
$('<div class="timestamp">' + d.getHours() + ':' + d.getMinutes() + '</div>').appendTo($('.message:last'));
}

function insertMessage(msg) {
if ($.trim(msg) == '') {
    return false;
}
$('<div class="message message-personal">' + msg + '</div>').appendTo($messages).addClass('new');
setDate();
$('.message-input').val(null);
scrollChat(); // Прокручиваем при каждом сообщении
setTimeout(function() {
    fakeMessage();
}, 1000 + (Math.random() * 20) * 20);
}

$('.message-submit').click(function() {
insertMessage($('.message-input').val());
});

$(window).on('keydown', function(e) {
if (e.which == 13) {
    insertMessage($('.message-input').val());
    return false;
}
});

var Fake = [
'Hi there, I\'m AI Chat and you?',
'Nice to meet you',
'How are you?',
'It\'s an example of an answer. I can\'t understand you',
'Still can\'t',
':)'
];

function fakeMessage() {
    if ($('.message-input').val() !== '') {
        return false;
    }
    $('<div class="message new">' + Fake[i] + '</div>').appendTo($messages).addClass('new');
    setDate();
    i++;
    scrollChat(); // Прокручиваем при каждом сообщении
}

function scrollChat() {
    var height = $messages[0].scrollHeight;
    $messages.stop().animate({ scrollTop: height }, 'slow');
}

// Initial fake message
$(window).on('load', function() {
setTimeout(function() {
    fakeMessage();
    scrollChat();
}, 100);
});
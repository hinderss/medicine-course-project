document.addEventListener("DOMContentLoaded", function() {
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
        scrollChat();
        
        // Send message to server
        sendMessageToServer(msg);
    }

    function sendMessageToServer(msg) {
        // Replace with your actual server endpoint
        const serverUrl = '/chat';
        
        fetch(serverUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: msg })
        })
        .then(response => response.json())
        .then(data => {
            // Display server response
            $('<div class="message new">' + data.response + '</div>').appendTo($messages).addClass('new');
            setDate();
            scrollChat();
        })
        .catch(error => {
            console.error('Error:', error);
            $('<div class="message new">Sorry, there was an error connecting to the server.</div>').appendTo($messages).addClass('new');
            setDate();
            scrollChat();
        });
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

    function scrollChat() {
        var height = $messages[0].scrollHeight;
        $messages.stop().animate({ scrollTop: height }, 'slow');
    }

    // Initial greeting message
    $(window).on('load', function() {
        setTimeout(function() {
            $('<div class="message new">Hello! How can I help you today?</div>').appendTo($messages).addClass('new');
            setDate();
            scrollChat();
        }, 100);
    });
});

$(document).on('click', function(event) {
    const $chat = $('.chat');
    const $icon = $('#gptIcon');

    if ($chat.css('display') === 'flex' &&
        !$chat.is(event.target) && $chat.has(event.target).length === 0 &&
        !$icon.is(event.target) && $icon.has(event.target).length === 0) {
        $chat.css('display', 'none');
        $icon.css('display', 'block');
    }
});
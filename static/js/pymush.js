 "use strict"

$(function () {
    var wsURL = "ws://" + location.hostname + ":9000";
    var wsConnection = new WebSocket(wsURL);

    wsConnection.onopen = function() {
        console.debug("Connected");

        $("#textEntry").keyup(function(evt) {
            if (evt.keyCode === 13 && !evt.shiftKey) {
                var textBox = $(evt.target);
                var textToSend = textBox.val();

                textBox.val("");

                wsConnection.send(textToSend);
            }
        });
    };

    wsConnection.onmessage = function(msg) {
        var msgDiv = $('<div class="message" />').text(msg.data);
        $("#chat").append(msgDiv);
    };
});
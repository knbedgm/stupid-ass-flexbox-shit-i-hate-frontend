import Letterize from "https://cdn.skypack.dev/letterizejs@2.0.0";
import anime from "https://cdn.skypack.dev/animejs@3.2.1";

$(document).ready(function() {

    function updateDonationText(message, username, bits) {
        $('#message-text').text(message);
        $('#username').text(username[0].toUpperCase() + username.substr(1));
        $('#bits').text(bits);

        // Animate the username and bits using Letterize and Anime libraries
        // Example here: https://wojciechkrakowiak.github.io/letterize/examples/
        const usernameAnimation = new Letterize({targets: "#username, #bits", className: "letter"});
        var animation = anime.timeline({
            targets: usernameAnimation.listAll,
            delay: anime.stagger(50),
            loop: true
        });
        animation
            .add({translateY: -2, scale: 1.03, duration: 1000})
            .add({translateY: 0, scale: 1, duration: 1000});
    }

    var socket = io();

    socket.on('new_message', function(msg, cb) {
        console.log("Got data: " + msg)

        updateDonationText(msg.message, msg.username, msg.bits);

        $("#donation-container").animate({ opacity: 1 }, 150);
        $("#message-container").animate({ opacity: 1 }, 150);

        if (cb)
            cb();
    });

    socket.on('clear_message', function (msg, cb) {
        console.log("Client received clear message instruction!")

        $("#donation-container").animate({ opacity: 0 }, 150);
        $("#message-container").animate({ opacity: 0 }, 150);

        if (cb)
            cb();
    });
    
    // Display some temp data to start off
    updateDonationText("If someone donates it will kill me 😣", "Testerman", "305")
});
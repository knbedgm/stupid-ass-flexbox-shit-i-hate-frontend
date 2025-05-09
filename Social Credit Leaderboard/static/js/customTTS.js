import Letterize from "https://cdn.skypack.dev/letterizejs@2.0.0";
import anime from "https://cdn.skypack.dev/animejs@3.2.1";

$(document).ready(function() {

    var socket = io();

    socket.on('start_openai', function(msg, cb) {
        console.log("Got data: " + msg)

        $("#openai-container").animate({ opacity: 1 }, 500);

        if (cb)
            cb();
    });

    socket.on('top_5', function(msg, cb) {
        // Handle list of top 5 strings with green gradient
        const items = Array.isArray(msg) ? msg : (Array.isArray(msg.text) ? msg.text : []);
        const $container = $("#top5-text");
        $container.empty();
        // Use dark-to-light green gradient (light green at bottom)
        const startColor = { r: 0, g: 150, b: 0 };   // darker green at top
        const endColor = { r: 144, g: 238, b: 144 }; // light green at bottom (#90EE90)
        items.forEach((item, index) => {
            const progress = items.length > 1 ? index / (items.length - 1) : 0;
            const r = Math.round(startColor.r + (endColor.r - startColor.r) * progress);
            const g = Math.round(startColor.g + (endColor.g - startColor.g) * progress);
            const b = Math.round(startColor.b + (endColor.b - startColor.b) * progress);
            const color = `rgb(${r}, ${g}, ${b})`;
            const $itemDiv = $("<div></div>").text(item);
            $container.append($itemDiv);
            const letterizer = new Letterize({ targets: $itemDiv.get(0), className: "openai-letter" });
            // apply computed color to each letter
            letterizer.listAll.forEach(letterEl => { letterEl.style.color = color; });
            const animation = anime.timeline({
                targets: letterizer.listAll,
                delay: anime.stagger(30),
                loop: true
            });
            animation
                .add({ translateY: -2, duration: 1000 })
                .add({ translateY: 0, duration: 1000 });
        });
        if (cb) cb();
    });
      


    // Updates each sentence
    socket.on('bottom_5', function(msg, cb) {
        // Handle list of bottom 5 strings with red gradient
        const items = Array.isArray(msg) ? msg : (Array.isArray(msg.text) ? msg.text : []);
        const $container = $("#bottom5-text");
        $container.empty();
        const startColor = { r: 255, g: 151, b: 151 };  // light red (#FF9797)
        const endColor = { r: 255, g: 0, b: 0 };        // dark red (#FF0000)
        items.forEach((item, index) => {
            const progress = items.length > 1 ? index / (items.length - 1) : 0;
            const r = Math.round(startColor.r + (endColor.r - startColor.r) * progress);
            const g = Math.round(startColor.g + (endColor.g - startColor.g) * progress);
            const b = Math.round(startColor.b + (endColor.b - startColor.b) * progress);
            const color = `rgb(${r}, ${g}, ${b})`;
            const $itemDiv = $("<div></div>").text(item);
            $container.append($itemDiv);
            const letterizer = new Letterize({ targets: $itemDiv.get(0), className: "openai-letter" });
            letterizer.listAll.forEach(letterEl => { letterEl.style.color = color; });
            const animation = anime.timeline({
                targets: letterizer.listAll,
                delay: anime.stagger(30),
                loop: true
            });
            animation
                .add({ translateY: -2, duration: 1000 })
                .add({ translateY: 0, duration: 1000 });
        });
        if (cb) cb();
    });

    socket.on('clear_openai', function (msg, cb) {
        console.log("Client received clear message instruction!")

        $("#openai-container").animate({ opacity: 0 }, 500);

        if (cb)
            cb();
    });
});
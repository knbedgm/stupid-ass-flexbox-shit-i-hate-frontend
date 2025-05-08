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
        $("#top5-text").html(msg.text)

        // Note that openAiAnimation is NOT a const variable
        let openAiAnimation = new Letterize({targets: "#bottom5-text", className: "openai-letter"});

        // Now we've turned every letter into its own span, we group all of the letter spans into "word" elements, so that the word elements can wrap around multiple lines appropriately
        let $openaiText = $('#bottom5-text'); // Get the openai-text container
        let $letters = $openaiText.find('.openai-letter'); // Get all the letter spans inside the openai_text container
        let $newContent = $('<div></div>'); // Create a new jQuery object to hold the new structure
        let $wordSpan = $('<span class="openai-word"></span>'); // Create a new word span to start with
        // Iterate over each letter span to create the word element
        $letters.each(function() {
            const $letter = $(this);
            if ($letter.text().trim() === '') { // Check if the letter is a space
                $newContent.append($wordSpan); // Append the current word span to the new content
                $newContent.append($letter); // Add the space directly to the new content
                $wordSpan = $('<span class="openai-word"></span>'); // Create a new word span for the next word
            } else {
                $wordSpan.append($letter); // If not a space, append the letter to the current word span
            }
        });
        $newContent.append($wordSpan); // Append the last word span to the new content
        $openaiText.empty().append($newContent.contents()); // Clear the openai_text container and append the new content

        // Apply gradient colors at the very end
        const lines = msg.text.split('\n').filter(line => line.trim() !== '');
        const startColor = { r: 255, g: 151, b: 151 };  // #FF9797
        const endColor = { r: 255, g: 0, b: 0 };        // #FF0000
        
        // Get all word spans
        const $wordSpans = $openaiText.find('.openai-word');
        let currentLine = 0;
        let wordsInCurrentLine = 0;
        let totalWordsInLine = 0;
        
        // Count words in each line
        const wordsPerLine = lines.map(line => line.split(/\s+/).length);
        
        $wordSpans.each(function() {
            if (wordsInCurrentLine >= wordsPerLine[currentLine]) {
                currentLine++;
                wordsInCurrentLine = 0;
            }
            
            // Calculate color for this line
            const progress = currentLine / (lines.length - 1);
            const r = Math.round(startColor.r + (endColor.r - startColor.r) * progress);
            const g = Math.round(startColor.g + (endColor.g - startColor.g) * progress);
            const b = Math.round(startColor.b + (endColor.b - startColor.b) * progress);
            
            // Apply color to all letters in this word
            $(this).find('.openai-letter').css('color', `rgb(${r}, ${g}, ${b})`);
            
            wordsInCurrentLine++;
        });

        var animation = anime.timeline({
            targets: openAiAnimation.listAll,
            delay: anime.stagger(30),
            loop: true
        });
        animation
            .add({translateY: -2, duration: 1000})
            .add({translateY: 0, duration: 1000});

        if (cb) cb();
    });
      


    // Updates each sentence
    socket.on('bottom_5', function(msg, cb) {
        $("#bottom5-text").text(msg.text)
        $("#bottom5-text").css('color', '#FF0000'); // Set text to bright red
        
        // Note that openAiAnimation is NOT a const variable
        let openAiAnimation = new Letterize({targets: "#bottom5-text", className: "openai-letter"});

        // Now we've turned every letter into its own span, we group all of the letter spans into "word" elements, so that the word elements can wrap around multiple lines appropriately
        let $openaiText = $('#bottom5-text'); // Get the openai-text container
        let $letters = $openaiText.find('.openai-letter'); // Get all the letter spans inside the openai_text container
        let $newContent = $('<div></div>'); // Create a new jQuery object to hold the new structure
        let $wordSpan = $('<span class="openai-word"></span>'); // Create a new word span to start with
        // Iterate over each letter span to create the word element
        $letters.each(function() {
            const $letter = $(this);
            if ($letter.text().trim() === '') { // Check if the letter is a space
                $newContent.append($wordSpan); // Append the current word span to the new content
                $newContent.append($letter); // Add the space directly to the new content
                $wordSpan = $('<span class="openai-word"></span>'); // Create a new word span for the next word
            } else if ($letter.text().trim() === '@')
            {
                // We want to FORCE A NEW line element
                $newContent.append($('<div></div>'));
            } else {
                $wordSpan.append($letter); // If not a space, append the letter to the current word span
            }
        });
        $newContent.append($wordSpan); // Append the last word span to the new content
        $openaiText.empty().append($newContent.contents()); // Clear the openai_text container and append the new content

        // Apply gradient colors at the very end
        const startColor = { r: 255, g: 151, b: 151 };  // #FF9797
        const endColor = { r: 255, g: 0, b: 0 };        // #FF0000
        
        var animation = anime.timeline({
            targets: openAiAnimation.listAll,
            delay: anime.stagger(30),
            loop: true
        });
        animation
            .add({translateY: -2, duration: 1000})
            .add({translateY: 0, duration: 1000});

        if (cb)
            cb();
    });

    socket.on('clear_openai', function (msg, cb) {
        console.log("Client received clear message instruction!")

        $("#openai-container").animate({ opacity: 0 }, 500);

        if (cb)
            cb();
    });
});
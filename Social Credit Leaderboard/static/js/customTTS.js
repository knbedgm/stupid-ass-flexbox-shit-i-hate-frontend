import Letterize from "https://cdn.skypack.dev/letterizejs@2.0.0";
import anime from "https://cdn.skypack.dev/animejs@3.2.1";

$(document).ready(function () {
	var socket = io();

	socket.on("start_openai", function (msg, cb) {
		console.log("Got data: " + msg);

		$("#openai-container").animate({ opacity: 1 }, 500);

		if (cb) cb();
	});

	socket.on("top_5", function (msg, cb) {
		doTheTextStuff(msg, "#top5-text", {
			startColor: { r: 0, g: 255, b: 0 }, // #00FF00
			endColor: { r: 151, g: 255, b: 151 }, // #97FF97
		});
		if (cb) cb();
	});

	socket.on("bottom_5", function (msg, cb) {
		doTheTextStuff(msg, "#bottom5-text", {
			startColor: { r: 255, g: 151, b: 151 }, // #FF9797
			endColor: { r: 255, g: 0, b: 0 }, // #FF0000
		});

		if (cb) cb();
	});

	// Updates each sentence
	function doTheTextStuff(msg, section, colors) {
		let main = $(section);
		main.html("");
		msg.split("\n").map((line) => {
			main.append($(`<div class="line openai-word">${line}</div>`));
		});

		// Note that openAiAnimation is NOT a const variable
		let openAiAnimation = new Letterize({
			targets: section,
			className: "openai-letter",
		});

		// Apply gradient colors at the very end
		const startColor = colors.startColor;
		const endColor = colors.endColor;

		const lines = main.find(".openai-word");
		let currentLine = 0;

		lines.each(function () {
			// Calculate color for this line
			const progress = currentLine / (lines.length - 1);
			const r = Math.round(
				startColor.r + (endColor.r - startColor.r) * progress
			);
			const g = Math.round(
				startColor.g + (endColor.g - startColor.g) * progress
			);
			const b = Math.round(
				startColor.b + (endColor.b - startColor.b) * progress
			);

			// Apply color to all letters in this word
			$(this)
				.find(".openai-letter")
				.css("color", `rgb(${r}, ${g}, ${b})`);

			currentLine++;
		});

		// var animation = anime.timeline({
		// 	targets: openAiAnimation.listAll,
		// 	delay: anime.stagger(30),
		// 	loop: true,
		// });
		// animation
		// 	.add({ translateY: -2, duration: 1000 })
		// 	.add({ translateY: 0, duration: 1000 });
		// window.ani = animation;
		doTheAnimation();
		// debugger;
	}

	let animation = null;

	function doTheAnimation() {
		if (animation) {
			animation.pause();
			animation = null;
		}

		let letters = Array.from($(".openai-letter"));
		// debugger;
		animation = anime.timeline({
			targets: letters,
			delay: anime.stagger(30),
			loop: true,
		});
		animation
			.add({ translateY: -2, duration: 1000 })
			.add({ translateY: 0, duration: 1000 });
		window.ani = animation;
	}


    // Me testing cause python dont work
	// doTheTextStuff(
	// 	"top1 100\ntop2 90\ntop3 80\ntop4 70\ntop5 60",
	// 	"#top5-text",
	// 	{
	// 		startColor: { r: 0, g: 255, b: 0 }, // #00FF00
	// 		endColor: { r: 151, g: 255, b: 151 }, // #97FF97
	// 	}
	// );
	// doTheTextStuff(
	// 	"bottom1 -60\nbottom2 -70\nbottom3 -80\nbottom4 -90\nbottom5 -100",
	// 	"#bottom5-text",
	// 	{
	// 		startColor: { r: 255, g: 151, b: 151 }, // #FF9797
	// 		endColor: { r: 255, g: 0, b: 0 }, // #FF0000
	// 	}
	// );

	socket.on("clear_openai", function (msg, cb) {
		console.log("Client received clear message instruction!");

		$("#openai-container").animate({ opacity: 0 }, 500);

		if (cb) cb();
	});
});

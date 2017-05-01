$(document).ready(function(){

	console.log("Now we're inside the notecards-deck-list-jquery's ready().");
	bindDeleteDecks();
	
	$(".deck-form").on("submit", function(event){
		event.preventDefault();
		console.log(".deck-form submitted.");

		var deckName = $(this).find("#id_title").val()

		$.ajax({
			url: "/deck/create/",
			context: this,
			data: {deck_name: deckName},
			type: 'POST',
			success: function(data){
				// should this be a function or not?
				//logResult(data.success, data.message);;
				console.log(data.success ? "Success: " + data.message : "Failure: " + data.message)

				// this isn't working yet, reset "hidden_initially" and try again
				//$(".deck-container").append(data.deck_html).show(200);
				$(".deck-container").append(data.deck_html);
				bindDeleteDecks();
			}
		});
	});
});

function bindDeleteDecks(){
	$(".ajax-delete-deck-link").unbind("click", deckDeleteEvent);
	$(".ajax-delete-deck-link").bind("click", deckDeleteEvent);
}

function deckDeleteEvent(event){
	event.preventDefault();

	var deckPk = event.target.id.split("-")[3];
	console.log("Deck pk: " + deckPk);

	$.ajax({
		url: "/deck/" + deckPk + "/delete/",
		data: {pk: deckPk},
		type: 'POST',
		success: function(data){
			console.log(data.success ? "Success: " + data.message : "Failure: " + data.message);
			$("#deck-"+deckPk).fadeOut(200, function(){ $(this).remove();});
		}
	});
}
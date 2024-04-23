window.onload = async function() {
	id = window.location.href.split("id=")[1];
	
	if (id === undefined) {
		window.location.replace("http://localhost:8080/games");
		return;
	}
	
	const req = new XMLHttpRequest();
	req.open("GET", "/api/game?id=" + id, false);
	req.setRequestHeader("Content-type", "application/json");
	req.send();
	const response = JSON.parse(req.responseText);
	console.log(response);

	let position = 0;
		
	const board = new Board(false)
	board.display();
	board.setBoard(response.positions[position]);

	const infobox = new InfoBox();

	// TODO: Reformat time such that it used : instead of - 

	infobox.addInfoField("starting-fen", "Starting FEN: " + response.fen);
	infobox.addInfoField("date", "Starting date: " + response.date);
	infobox.addInfoField("time", "Starting time: " + response.time.replaceAll("-", ":"));
	infobox.addInfoField("result", "Result: " + response.result);
	infobox.addInfoField("position", "Position: " + (position + 1));

	function updateBoard() {
		board.setBoard(response.positions[position]);
		infobox.updateInfoField("starting-fen", "Starting FEN: " + response.fen);
		infobox.updateInfoField("date", "Starting date: " + response.date);
		infobox.updateInfoField("time", "Starting time: " + response.time.replaceAll("-", ":"));
		infobox.updateInfoField("result", "Result: " + response.result);
		infobox.updateInfoField("position", "Position: " + (position + 1));
	}

	const buttons = new Buttons();
	buttons.addButton("left", "<", function() {
		if(position != 0) {
			position -= 1;
			updateBoard();
		}
	});
	buttons.addButton("right", ">", function() {
		if (position != response.positions.length - 1) {
			position += 1;
			updateBoard();
		}
	});
}

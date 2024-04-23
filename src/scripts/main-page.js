window.onload = async function() {
	const infobox = new InfoBox();	
	const board = new Board(true, infobox, true);
	board.display();
	
	infobox.addInfoField("move", "Move: ");
	infobox.addInfoField("castling", "Castling: ");
	infobox.addInfoField("en-passent-target", "En Passent target: ");
	infobox.addInfoField("fullmoves", "Fullmoves: ");
	infobox.addInfoField("halfmoves", "Halfmoves: ");
	
	board.updateBoard("/api/board");

	const buttons = new Buttons();
	buttons.addButton("draw", "Draw", function() {
		const requestData = {
			"to": "-",
			"from": "-",
			"result": 2
		};

		const req = new XMLHttpRequest();
		req.open("POST", "/api/board", true);
		req.setRequestHeader("Content-type", "application/json");
		req.onload = () => {
			board.updateBoard("/api/board");
		};
		req.send(JSON.stringify(requestData));
	});
	buttons.addButton("resign", "Resign", function() {
		const requestData = {
			"to": "-",
			"from": "-",
			"result": 1
		};

		const req = new XMLHttpRequest();
		req.open("POST", "/api/board", true);
		req.setRequestHeader("Content-type", "application/json");
		req.onload = () => {
			board.updateBoard("/api/board");
		};
		req.send(JSON.stringify(requestData));
	});
}

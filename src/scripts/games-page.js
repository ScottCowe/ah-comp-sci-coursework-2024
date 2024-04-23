window.onload = async function() {
	const req = new XMLHttpRequest();
	req.open("GET", "/api/games", false);
	req.send();
	
	const response = JSON.parse(req.responseText);
	
	console.log(response);
	
	const games = new Games();
	
	const numberRows = Math.ceil(response.games.length / 4);
	
	for (let i = 0; i < numberRows; i++) {
		games.addRow(i);
	}
	
	let numInCurrentRow = 0;
	let currentRow = 0;
	
	for (let i = response.games.length - 1; i > -1; i--) {
		if (numInCurrentRow == 4) {
			currentRow += 1;
			numInCurrentRow = 0;
		}
		
		games.addGame(response.games[i], currentRow);
		numInCurrentRow += 1;
	}
}

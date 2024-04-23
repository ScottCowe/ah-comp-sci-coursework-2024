class Games {
	constructor() {
		this.gamesContainer = document.getElementById("games-container");
	}
	
	addGame(datetime, rowIndex) {
		let elem = document.createElement("a");
		elem.id = datetime;
		elem.classList.add("game-link");
		elem.href = "/game?id=" + datetime;
		document.getElementById("row-" + rowIndex).appendChild(elem);
		
		// Add fields and append
		const datetimeSplit = datetime.split("-");
		const date = datetimeSplit[0] + "/" + datetimeSplit[1] + "/" + datetimeSplit[2];
		const time = datetimeSplit[3] + ":" + datetimeSplit[4] + ":" + datetimeSplit[5];
		
		let dateElem = document.createElement("p");
		dateElem.innerHTML = date;
		
		let timeElem = document.createElement("p");
		timeElem.innerHTML = time;
		
		elem.appendChild(dateElem);
		elem.appendChild(timeElem);
	}
	
	addRow(index) {
		let elem = document.createElement("div");
		elem.id = "row-" + index;
		elem.classList.add("games-row");
		this.gamesContainer.appendChild(elem);
	}
}

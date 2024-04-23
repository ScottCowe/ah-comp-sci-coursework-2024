class Square {
	constructor(row, col) {
		this.row = row;
		this.col = col;
		this.index = 8 * (7 - row) + col;
		this.piece = "";
	}

	set(piece) {
		this.piece = piece;
		const svgColor = piece == piece.toUpperCase() ? "l" : "d";
		const svgPiece = piece.toLowerCase();
		const svgTag = "<img src='/" + svgColor + svgPiece + ".svg'>";
		const empty = piece == "";
		document.getElementsByClassName("square")[this.index].innerHTML = empty ? "" : svgTag;
	}

	setClicked(clicked) {
		if (clicked) {
			document.getElementsByClassName("square")[this.index].classList.add("clicked");
		} else {
			document.getElementsByClassName("square")[this.index].classList.remove("clicked");
		}
	}

	setHighlighted(highlighted) {
		if (highlighted) {
			document.getElementsByClassName("square")[this.index].classList.add("highlighted");
		} else {
			document.getElementsByClassName("square")[this.index].classList.remove("highlighted");
		}
	}

	getAlgebraic() {
		return String.fromCharCode(97 + this.col) + String(this.row + 1);
	}

	getRow() {
		return this.row;
	}

	getCol() {
		return this.col;
	}

	isOccupied() {
		return this.piece != "";
	}
}

class Board {
	constructor(dynamic, infobox, showbox) {
		// 0, 0 is top left
		// This square is actually 7, 0 (a8)
		this.squares = [];
		this.clickedSquare = undefined;
		this.dynamic = dynamic
		this.infobox = infobox;
		this.showbox = showbox;
	}

	display() {
		const boardContainer = document.getElementById("board-container");

		for (let i = 0; i < 8; i++) {
			let boardRow = document.createElement("div");
			boardRow.classList.add("board-row");
			boardContainer.appendChild(boardRow);
			
			this.squares[i] = []

			for (let j = 0; j < 8; j++) {
				let square = document.createElement("div");
				square.id = 8 * i + j
				square.classList.add("square");

				this.squares[i][j] = new Square(7 - i, j);

				const jOffset = i % 2 ? j + 1 : j;
				const isWhiteSquare = jOffset % 2 == 0;
				square.classList.add(isWhiteSquare ? "white-square" : "black-square");

				boardRow.appendChild(square);

				square.addEventListener("click", () => { this.onSquareClicked(this.squares[i][j]); });
			}
		}
	}
	
	setSquare(row, col, to) {
		this.squares[row][col].set(to);
	}

	setBoard(board) {
		for (let i = 0; i < 8; i++) {
			for (let j = 0; j < 8; j++) {
				this.setSquare(i, j, board[i][j]);
			}
		}
	}

	onSquareClicked(square) {
		if (!this.dynamic) {
			return false;
		}

		if (!square.isOccupied() && this.clickedSquare == undefined) {
			return;
		}

		if (this.clickedSquare == undefined) {
      			square.setClicked(true);
      			this.clickedSquare = square;
      			return;
    	}
		
		const fromSquare = this.clickedSquare;
		const toSquare = square;

		this.clickedSquare.setClicked(false);
		this.clickedSquare = undefined;

		const requestData = {
			"to": toSquare.getAlgebraic(),
			"from": fromSquare.getAlgebraic(),
			"result": 0
		};
		
		const req = new XMLHttpRequest();
		req.open("POST", "/api/board", true);
		req.setRequestHeader("Content-type", "application/json");
		req.onload = () => {
			this.updateBoard("/api/board")
		}
		req.send(JSON.stringify(requestData));
	}

	updateBoard(endpoint) {
		const req = new XMLHttpRequest();
		req.open("GET", endpoint, false);
		req.send();
		const response = JSON.parse(req.responseText);
		this.setBoard(response.board);
		
		if (this.showbox) {
			this.infobox.updateInfoField("move", "Move: " + response.whitesMove);
			this.infobox.updateInfoField("castling", "Castling: " + response.castling);
			this.infobox.updateInfoField("en-passent-target", "En Passent target: " + response.enPassentTarget);
			this.infobox.updateInfoField("fullmoves", "Fullmoves: " + response.fullmoves);
			this.infobox.updateInfoField("halfmoves", "Halfmoves: " + response.halfmoves);
		}
	}
}

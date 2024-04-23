class Buttons {
	constructor() {
		this.buttonContainer = document.getElementById("buttons");
	}

	addButton(id, text, action) {
		let elem = document.createElement("div");
		elem.id = id;
		elem.classList.add("button");
		elem.innerHTML = text;
		this.buttonContainer.appendChild(elem);
		elem.addEventListener("click", () => { action() });
	}
}

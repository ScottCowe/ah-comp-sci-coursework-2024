class InfoBox {
	constructor() {
		this.infoBox = document.getElementById("info");
	}
	
	addInfoField(id, innerHTML) {
		let elem = document.createElement("p");
		elem.id = id;
		elem.classList.add("infofield");	
		elem.innerHTML = innerHTML;
		this.infoBox.appendChild(elem);
	}
	
	updateInfoField(id, innerHTML) {
		let elem = document.getElementById(id);
		elem.innerHTML = innerHTML
	}
}

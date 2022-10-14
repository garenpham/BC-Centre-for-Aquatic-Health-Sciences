function highlight() {
	var pageurl = location.href;
	var dnl = document.getElementsByTagName("a");
	var itemDropdown = document.getElementById("itemDropdown");
	var dropdownNav = document.getElementById("dropdownNav");

	for (i = 0; i < dnl.length; i++) {
		var x = dnl.item(i);
		if (x.href == pageurl) {
			if (
				!/Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)
			) {
				// what you want to run in desktop
				x.style.fontWeight = "bold";
				x.style.color = "white";
				itemDropdown.setAttribute("style", "text-align: end !important");
			} else {
				// mobile
				x.style.color = "white";
				itemDropdown.setAttribute("style", "text-align: center !important");
				dropdownNav.setAttribute("style", "display: block !important");
			}
		}
	}
}

window.onload = highlight;

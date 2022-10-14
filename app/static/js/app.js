function highlight() {
	var pageurl = location.href;
	var dnl = document.getElementsByTagName("a");
	for (i = 0; i < dnl.length; i++) {
		var x = dnl.item(i);
		if (x.href == pageurl) {
			if (
				!/Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)
			) {
				// what you want to run in desktop
				x.style.fontWeight = "bold";
				x.style.color = "white";
			} else {
				// mobile
				x.style.color = "white";
			}
		}
	}
}

window.onload = highlight;

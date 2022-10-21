function highlight() {
	var pageurl = location.href;
	var navlinks = document.getElementsByTagName("a");
	var itemDropdown = document.getElementById("itemDropdown");
	var dropdownNav = document.getElementById("dropdownNav");
	var navSmTitle = document.getElementById("navSmTitle");

	for (i = 0; i < navlinks.length; i++) {
		var currentPage = navlinks.item(i);
		if (currentPage.href == pageurl) {
			if (
				!/Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)
			) {
				// what you want to run in desktop
				currentPage.style.fontWeight = "bold";
				currentPage.style.color = "white";
				itemDropdown.setAttribute("style", "text-align: center");
			} else {
				// mobile
				currentPage.style.color = "white";
				itemDropdown.setAttribute("style", "text-align: center ");
				dropdownNav.setAttribute("style", "display: block");
				navSmTitle.innerHTML = currentPage.innerHTML;
			}
		}
	}
}

window.onload = highlight;

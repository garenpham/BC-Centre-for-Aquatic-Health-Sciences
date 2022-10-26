function highlight() {
	var pageurl = location.href;
	var navlinks = document.getElementsByTagName("a");
	var navSmTitle = document.getElementById("navSmTitle");
	var navBg = document.getElementsByClassName("nav-bg");

	for (i = 0; i < navlinks.length; i++) {
		var currentPage = navlinks.item(i);
		if (currentPage.href == pageurl) {
			currentPage.style.color = "white";
			navSmTitle.innerHTML = currentPage.innerHTML;
			navBg.item(i).style.backgroundColor = "black";
			if (
				!/Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)
			) {
				// what you want to run in desktop
				currentPage.style.fontWeight = "bold";
			} else {
				// mobile
			}
		} else {
		}
	}
}

window.onload = highlight;

var navbar_toggler = document.querySelector(".navbar-toggler");
var closeIcon = document.getElementById("closeIcon");
var main = document.querySelector("main");
var body = document.querySelector("body");
var navCollapse = document.querySelector(".navbar-collapse");

navbar_toggler.addEventListener("click", function () {
	closeIcon.classList.toggle("active");
	if (closeIcon.classList.contains("active")) {
		navCollapse.classList.remove("active");
		main.classList.add("active");
		body.classList.add("active");
	} else {
		navCollapse.classList.add("active");
		main.classList.remove("active");
		body.classList.add("active");
	}
});

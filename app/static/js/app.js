function highlight() {
	var pageurl = location.href;
	var navlinks = document.getElementsByTagName("a");
	var navSmTitle = document.getElementById("navSmTitle");
	var navBg = document.getElementsByClassName("nav-bg");
	var nav = document.getElementsByTagName("nav");
	for (i = 0; i < navlinks.length; i++) {
		var currentPage = navlinks.item(i);
		if (
			pageurl.includes(currentPage.href) &&
			!currentPage.innerText.includes("Admin") //exclude admin with the current nav link
		) {
			currentPage.style.color = "white";
			currentPage.style.fontWeight = "bold";
			navSmTitle.innerText = currentPage.innerText;
			navBg.item(i).style.backgroundColor = "black";
			if ($(window).width() < 999) {
				// mobile
				if (pageurl.includes("metadata")) {
					nav[0].setAttribute("style", "margin-bottom: 0 !important");
				}
			} else {
				// what you want to run in desktop
			}
			break;
		}
	}
}

window.onload = function () {
	highlight();
};

var navbar_toggler = document.querySelector(".navbar-toggler");
var closeIcon = document.getElementById("closeIcon");
var main = document.getElementsByTagName("main");
var body = document.getElementsByTagName("body");
var navCollapse = document.querySelector("#navbarNav");

navbar_toggler.addEventListener("click", function () {
	closeIcon.classList.toggle("active");
	if (closeIcon.classList.contains("active")) {
		navCollapse.classList.remove("active");
		main[0].style.filter = "blur(2px)";
		body[0].style.overflow = "hidden";
	} else {
		navCollapse.classList.add("active");
		main[0].style.filter = "blur(0px)";
		body[0].style.overflow = "scroll";
	}
});

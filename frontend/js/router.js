



const urlRoutes = {
	404: {
		template: "/pages/404.html",
		title: "404 | " + urlPageTitle,
		description: "Page not found",
	},
	"/": {
		template: "/index.html",
		title: "Home | " + urlPageTitle,
		description: "This is the home page",
	},
	"/login": {
		template: "/pages/login.html",
		title: "Login | " + urlPageTitle,
		description: "This is the login page",
	},
	"/register": {
		template: "/pages/register.html",
		title: "Register | " + urlPageTitle,
		description: "This is the register page",
	},
};


const urlRoute = (event) => {
	event = event || window.event; 
	event.preventDefault();
	window.history.pushState({}, "", event.target.href);
	urlLocationHandler();
};


const urlLocationHandler = async () => {
	const location = window.location.pathname; 
	if (location.length == 0 ) {
		location = "/";
	}

	const route = urlRoutes[location] || urlRoutes["404"];

	const html = await fetch(route.template).then((response) => response.text());

	document.getElementById("content").innerHTML = html;

	document.title = route.title;

	document
		.querySelector('meta[name="description"]')
		.setAttribute("content", route.description);
};

document.addEventListener("click", (e) => {
    // Tıklanan elemanın href özelliğini kontrol et
    if (e.target.tagName === 'A' && e.target.href) {
        e.preventDefault();
        urlRoute(e); // Event nesnesini urlRoute fonksiyonuna geçir
    }
});


window.onpopstate = urlLocationHandler;

window.route = urlRoute;

urlLocationHandler();
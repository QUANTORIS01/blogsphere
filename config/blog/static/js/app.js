const nav = document.querySelector(".mobile-menu");
const navMenuBtn = document.querySelector(".nav-menu-btn");
const navCloseBtn = document.querySelector(".nav-close-btn");
const navToggleFunc = function () {
    nav.classList.toggle("active");
};
navMenuBtn.addEventListener("click", navToggleFunc);
navCloseBtn.addEventListener("click", navToggleFunc);
const themeBtn = document.querySelectorAll(".theme-btn");

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.remove("light-theme", "dark-theme");
        document.body.classList.add(savedTheme);
        for (let j = 0; j < themeBtn.length; j++) {
            themeBtn[j].classList.remove("light", "dark");
            themeBtn[j].classList.add(savedTheme === "light-theme" ? "light" : "dark");
        }
    }
}

loadTheme();
for (let i = 0; i < themeBtn.length; i++) {
    themeBtn[i].addEventListener("click", function () {
        document.body.classList.toggle("light-theme");
        document.body.classList.toggle("dark-theme");
        const currentTheme = document.body.classList.contains("light-theme") ? "light-theme" : "dark-theme";
        localStorage.setItem('theme', currentTheme);
        for (let j = 0; j < themeBtn.length; j++) {
            themeBtn[j].classList.toggle("light");
            themeBtn[j].classList.toggle("dark");
        }
    });
}

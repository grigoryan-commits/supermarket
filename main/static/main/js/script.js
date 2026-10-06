// Общий скрипт сайта: подключается в базовом шаблоне base.html

// Открытие и закрытие меню на узких экранах
const burger = document.querySelector('.burger');
const nav = document.querySelector('.nav');

if (burger && nav) {
    burger.addEventListener('click', function () {
        nav.classList.toggle('nav--open');
    });
}

// Текущий год в подвале сайта
const year = document.getElementById('year');

if (year) {
    year.textContent = new Date().getFullYear();
}

// Скрипт страницы «Каталог»: фильтр товаров по категории

const buttons = document.querySelectorAll('.filter__btn');
const cards = document.querySelectorAll('.card[data-category]');

buttons.forEach(function (button) {
    button.addEventListener('click', function () {
        const category = button.dataset.category;

        buttons.forEach(function (item) {
            item.classList.remove('filter__btn--active');
        });
        button.classList.add('filter__btn--active');

        cards.forEach(function (card) {
            const show = category === 'all' || card.dataset.category === category;
            card.classList.toggle('hidden', !show);
        });
    });
});

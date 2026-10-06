from django.shortcuts import render

PRODUCTS = [
    {'name': 'Яблоки «Гала»', 'category': 'fruits', 'category_name': 'Овощи и фрукты',
     'price': 139, 'unit': 'кг', 'icon': '🍎', 'text': 'Сладкие красные яблоки, урожай этого года.'},
    {'name': 'Помидоры на ветке', 'category': 'fruits', 'category_name': 'Овощи и фрукты',
     'price': 249, 'unit': 'кг', 'icon': '🍅', 'text': 'Спелые тепличные помидоры.'},
    {'name': 'Молоко 3,2%', 'category': 'dairy', 'category_name': 'Молочные продукты',
     'price': 89, 'unit': 'шт', 'icon': '🥛', 'text': 'Пастеризованное, бутылка 930 мл.'},
    {'name': 'Сыр «Российский»', 'category': 'dairy', 'category_name': 'Молочные продукты',
     'price': 219, 'unit': 'шт', 'icon': '🧀', 'text': 'Полутвёрдый сыр, упаковка 200 г.'},
    {'name': 'Хлеб «Бородинский»', 'category': 'bakery', 'category_name': 'Выпечка',
     'price': 59, 'unit': 'шт', 'icon': '🍞', 'text': 'Ржано-пшеничный, нарезка 400 г.'},
    {'name': 'Круассан сливочный', 'category': 'bakery', 'category_name': 'Выпечка',
     'price': 75, 'unit': 'шт', 'icon': '🥐', 'text': 'Свежая выпечка из собственной пекарни.'},
]


def index(request):
    context = {'title': 'Главная', 'popular': PRODUCTS[::2]}
    return render(request, 'main/index.html', context)


def catalog(request):
    context = {'title': 'Каталог', 'products': PRODUCTS}
    return render(request, 'main/catalog.html', context)


def about(request):
    context = {'title': 'О нас'}
    return render(request, 'main/about.html', context)

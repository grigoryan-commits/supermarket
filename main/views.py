from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect, render

from .forms import CategoryForm, CustomerForm, NutritionForm, OrderForm, ProductForm, SupplierForm
from .models import Category, Customer, Nutrition, Order, Product, Supplier

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


def database(request):
    tables = [
        ('main:categories', 'Категории', Category.objects.count(), 'Справочник категорий товаров'),
        ('main:suppliers', 'Поставщики', Supplier.objects.count(), 'Компании, которые поставляют товары'),
        ('main:products', 'Товары', Product.objects.count(), 'Связь «один ко многим» с категориями и поставщиками'),
        ('main:nutrition', 'Пищевая ценность', Nutrition.objects.count(), 'Связь «один к одному» с товаром'),
        ('main:customers', 'Покупатели', Customer.objects.count(), 'Зарегистрированные покупатели'),
        ('main:orders', 'Заказы', Order.objects.count(), 'Связь «многие ко многим» с товарами'),
    ]
    return render(request, 'main/database.html', {'title': 'База данных', 'tables': tables})


def table_page(request, form_class, template, title, records, success):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, success)
            return redirect(request.path)
        messages.error(request, 'Запись не добавлена: исправьте ошибки в форме.')
    else:
        form = form_class()
    return render(request, template, {'title': title, 'form': form, 'records': records})


def categories(request):
    records = Category.objects.annotate(count=Count('products'))
    return table_page(request, CategoryForm, 'main/categories.html', 'Категории', records,
                      'Категория добавлена.')


def suppliers(request):
    records = Supplier.objects.annotate(count=Count('products'))
    return table_page(request, SupplierForm, 'main/suppliers.html', 'Поставщики', records,
                      'Поставщик добавлен.')


def products(request):
    records = Product.objects.select_related('category', 'supplier')
    return table_page(request, ProductForm, 'main/products.html', 'Товары', records,
                      'Товар добавлен.')


def nutrition(request):
    records = Nutrition.objects.select_related('product')
    return table_page(request, NutritionForm, 'main/nutrition.html', 'Пищевая ценность', records,
                      'Пищевая ценность добавлена.')


def customers(request):
    records = Customer.objects.annotate(count=Count('orders'))
    return table_page(request, CustomerForm, 'main/customers.html', 'Покупатели', records,
                      'Покупатель добавлен.')


def orders(request):
    records = Order.objects.select_related('customer').prefetch_related('products')
    return table_page(request, OrderForm, 'main/orders.html', 'Заказы', records,
                      'Заказ оформлен.')

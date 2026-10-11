from django.db import models


class Category(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField('Название компании', max_length=100)
    inn = models.CharField('ИНН', max_length=12, unique=True)
    phone = models.CharField('Телефон', max_length=12)
    email = models.EmailField('E-mail')

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    UNITS = [('шт', 'штука'), ('кг', 'килограмм'), ('л', 'литр')]

    name = models.CharField('Название', max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products',
                                 verbose_name='Категория')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='products',
                                 verbose_name='Поставщик')
    price = models.DecimalField('Цена, ₽', max_digits=8, decimal_places=2)
    unit = models.CharField('Единица', max_length=2, choices=UNITS, default='шт')
    stock = models.PositiveIntegerField('Остаток на складе', default=0)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return self.name


class Nutrition(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='nutrition',
                                   verbose_name='Товар')
    calories = models.PositiveIntegerField('Калорийность, ккал')
    proteins = models.DecimalField('Белки, г', max_digits=4, decimal_places=1)
    fats = models.DecimalField('Жиры, г', max_digits=4, decimal_places=1)
    carbs = models.DecimalField('Углеводы, г', max_digits=4, decimal_places=1)
    shelf_life = models.PositiveIntegerField('Срок годности, дней')

    class Meta:
        verbose_name = 'Пищевая ценность'
        verbose_name_plural = 'Пищевая ценность'
        ordering = ['product__name']

    def __str__(self):
        return f'Пищевая ценность: {self.product}'


class Customer(models.Model):
    full_name = models.CharField('ФИО', max_length=100)
    phone = models.CharField('Телефон', max_length=12, unique=True)
    email = models.EmailField('E-mail', unique=True)
    birth_date = models.DateField('Дата рождения')

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders',
                                 verbose_name='Покупатель')
    products = models.ManyToManyField(Product, related_name='orders', verbose_name='Товары')
    address = models.CharField('Адрес доставки', max_length=200)
    delivery_date = models.DateField('Дата доставки')
    created = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return f'Заказ №{self.pk}'

    def total(self):
        return sum(product.price for product in self.products.all())

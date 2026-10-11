import re
from datetime import date

from django import forms

from .models import Category, Customer, Nutrition, Order, Product, Supplier

PHONE_RE = re.compile(r'^\+7\d{10}$')


def clean_phone(value):
    phone = re.sub(r'[\s()-]', '', value)
    if phone.startswith('8') and len(phone) == 11:
        phone = '+7' + phone[1:]
    if not PHONE_RE.match(phone):
        raise forms.ValidationError('Телефон должен быть в формате +7XXXXXXXXXX (11 цифр).')
    return phone


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.ModelChoiceField) and not isinstance(field, forms.ModelMultipleChoiceField):
                field.empty_label = '— выберите —'


class PhoneField(forms.CharField):
    def __init__(self, **kwargs):
        super().__init__(label='Телефон', max_length=20, help_text='Например: +7 916 123-45-67', **kwargs)


class CategoryForm(BaseForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 3:
            raise forms.ValidationError('Название должно содержать не менее 3 символов.')
        if not re.fullmatch(r'[А-Яа-яЁё ,-]+', name):
            raise forms.ValidationError('Название может содержать только русские буквы, пробел, запятую и дефис.')
        return name[0].upper() + name[1:]


class SupplierForm(BaseForm):
    phone = PhoneField()

    class Meta:
        model = Supplier
        fields = ['name', 'inn', 'phone', 'email']

    def clean_inn(self):
        inn = self.cleaned_data['inn'].strip()
        if not inn.isdigit():
            raise forms.ValidationError('ИНН должен состоять только из цифр.')
        if len(inn) not in (10, 12):
            raise forms.ValidationError('ИНН организации — 10 цифр, ИП — 12 цифр.')
        return inn

    def clean_phone(self):
        return clean_phone(self.cleaned_data['phone'])


class ProductForm(BaseForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'supplier', 'price', 'unit', 'stock']

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('Название слишком короткое.')
        if name.isdigit():
            raise forms.ValidationError('Название не может состоять из одних цифр.')
        return name

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля.')
        if price > 100000:
            raise forms.ValidationError('Цена не может превышать 100 000 ₽.')
        return price

    def clean(self):
        cleaned = super().clean()
        name = cleaned.get('name')
        category = cleaned.get('category')
        if name and category and any(product.name.lower() == name.lower() for product in category.products.all()):
            raise forms.ValidationError(f'Товар «{name}» уже есть в категории «{category}».')
        return cleaned


class NutritionForm(BaseForm):
    class Meta:
        model = Nutrition
        fields = ['product', 'calories', 'proteins', 'fats', 'carbs', 'shelf_life']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(nutrition__isnull=True)
        self.fields['product'].help_text = 'Показаны только товары без пищевой ценности.'

    def clean_calories(self):
        calories = self.cleaned_data['calories']
        if calories > 900:
            raise forms.ValidationError('В 100 г продукта не может быть больше 900 ккал.')
        return calories

    def clean_shelf_life(self):
        days = self.cleaned_data['shelf_life']
        if days < 1 or days > 3650:
            raise forms.ValidationError('Срок годности — от 1 до 3650 дней.')
        return days

    def clean(self):
        cleaned = super().clean()
        values = [cleaned.get(name) for name in ('proteins', 'fats', 'carbs')]
        if None not in values:
            if any(value < 0 for value in values):
                raise forms.ValidationError('Белки, жиры и углеводы не могут быть отрицательными.')
            if sum(values) > 100:
                raise forms.ValidationError('Сумма белков, жиров и углеводов не может превышать 100 г на 100 г продукта.')
        return cleaned


class CustomerForm(BaseForm):
    phone = PhoneField()

    class Meta:
        model = Customer
        fields = ['full_name', 'phone', 'email', 'birth_date']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}

    def clean_full_name(self):
        full_name = ' '.join(self.cleaned_data['full_name'].split())
        parts = full_name.split(' ')
        if len(parts) < 2:
            raise forms.ValidationError('Введите фамилию и имя через пробел.')
        if not all(re.fullmatch(r'[А-ЯЁ][а-яё-]+', part) for part in parts):
            raise forms.ValidationError('ФИО пишется русскими буквами, каждое слово с заглавной буквы.')
        return full_name

    def clean_phone(self):
        phone = clean_phone(self.cleaned_data['phone'])
        if Customer.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Покупатель с таким телефоном уже зарегистрирован.')
        return phone

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        today = date.today()
        if birth_date > today:
            raise forms.ValidationError('Дата рождения не может быть в будущем.')
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 14:
            raise forms.ValidationError('Регистрация доступна с 14 лет.')
        if age > 120:
            raise forms.ValidationError('Проверьте год рождения.')
        return birth_date


class OrderForm(BaseForm):
    class Meta:
        model = Order
        fields = ['customer', 'products', 'address', 'delivery_date']
        widgets = {
            'products': forms.CheckboxSelectMultiple,
            'delivery_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean_address(self):
        address = self.cleaned_data['address'].strip()
        if len(address) < 10:
            raise forms.ValidationError('Укажите полный адрес: улицу, дом и квартиру.')
        if not any(char.isdigit() for char in address):
            raise forms.ValidationError('В адресе должен быть номер дома.')
        return address

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data['delivery_date']
        days = (delivery_date - date.today()).days
        if days < 0:
            raise forms.ValidationError('Дата доставки не может быть в прошлом.')
        if days > 14:
            raise forms.ValidationError('Доставку можно заказать не более чем на 14 дней вперёд.')
        return delivery_date

    def clean_products(self):
        products = self.cleaned_data['products']
        missing = [product.name for product in products if product.stock == 0]
        if missing:
            raise forms.ValidationError('Нет в наличии: ' + ', '.join(missing) + '.')
        return products

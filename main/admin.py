from django.contrib import admin
from django.db.models import Count

from .models import Category, Customer, Nutrition, Order, Product, Supplier

admin.site.site_header = 'ФрешМаркет — администрирование'
admin.site.site_title = 'ФрешМаркет'
admin.site.index_title = 'Управление данными магазина'


class RuSearchAdmin(admin.ModelAdmin):
    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)
        variants = {search_term, search_term.lower(), search_term.upper(),
                    search_term.capitalize(), search_term.title()}
        ids = set()
        for term in variants:
            qs, _ = super().get_search_results(request, queryset, term)
            ids.update(qs.values_list('pk', flat=True))
        return queryset.filter(pk__in=ids), False


class HasProductsFilter(admin.SimpleListFilter):
    title = 'наличие товаров'
    parameter_name = 'has_products'

    def lookups(self, request, model_admin):
        return [('yes', 'Есть товары'), ('no', 'Нет товаров')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(products__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(products__isnull=True)
        return queryset


class InStockFilter(admin.SimpleListFilter):
    title = 'наличие на складе'
    parameter_name = 'in_stock'

    def lookups(self, request, model_admin):
        return [('yes', 'В наличии'), ('no', 'Нет в наличии')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(stock__gt=0)
        if self.value() == 'no':
            return queryset.filter(stock=0)
        return queryset


@admin.register(Category)
class CategoryAdmin(RuSearchAdmin):
    list_display = ('name', 'description', 'products_count')
    list_filter = (HasProductsFilter,)
    search_fields = ('name', 'description')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_total=Count('products'))

    @admin.display(description='Товаров', ordering='products_total')
    def products_count(self, obj):
        return obj.products_total


@admin.register(Supplier)
class SupplierAdmin(RuSearchAdmin):
    list_display = ('name', 'inn', 'phone', 'email')
    list_filter = ('products__category',)
    search_fields = ('name', 'inn', 'phone', 'email')


@admin.register(Product)
class ProductAdmin(RuSearchAdmin):
    list_display = ('name', 'category', 'supplier', 'price', 'unit', 'stock')
    list_filter = ('category', 'supplier', 'unit', InStockFilter)
    search_fields = ('name', 'category__name', 'supplier__name')
    list_editable = ('price', 'stock')


@admin.register(Nutrition)
class NutritionAdmin(RuSearchAdmin):
    list_display = ('product', 'calories', 'proteins', 'fats', 'carbs', 'shelf_life')
    list_filter = ('product__category',)
    search_fields = ('product__name',)


@admin.register(Customer)
class CustomerAdmin(RuSearchAdmin):
    list_display = ('full_name', 'phone', 'email', 'birth_date')
    list_filter = ('birth_date',)
    search_fields = ('full_name', 'phone', 'email')


@admin.register(Order)
class OrderAdmin(RuSearchAdmin):
    list_display = ('__str__', 'customer', 'delivery_date', 'created', 'total')
    list_filter = ('delivery_date', 'created', 'products__category')
    search_fields = ('customer__full_name', 'customer__phone', 'address')
    filter_horizontal = ('products',)
    date_hierarchy = 'delivery_date'

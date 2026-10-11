from django.contrib import admin

from .models import Category, Customer, Nutrition, Order, Product, Supplier

admin.site.register([Category, Supplier, Product, Nutrition, Customer, Order])

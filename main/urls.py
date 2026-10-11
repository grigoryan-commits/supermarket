from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('about/', views.about, name='about'),
    path('db/', views.database, name='database'),
    path('db/categories/', views.categories, name='categories'),
    path('db/suppliers/', views.suppliers, name='suppliers'),
    path('db/products/', views.products, name='products'),
    path('db/nutrition/', views.nutrition, name='nutrition'),
    path('db/customers/', views.customers, name='customers'),
    path('db/orders/', views.orders, name='orders'),
]

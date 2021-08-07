from django.urls import path
from .views import (
    BaseView, 
    DishesDetailView, 
    CategoryDetailView, CartView, 
    AddToCartView, 
    DeleteFromCartView,
    ChangeQTYView,
    CheckoutView,
    MakeOrderView
)

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('dishes/<str:ct_model>/<str:slug>/', DishesDetailView.as_view(), name='dishes_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add-to-cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name='remove-from-cart'),
    path('change-qty/<str:ct_model>/<str:slug>/', ChangeQTYView.as_view(), name='change-qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make-order')
]

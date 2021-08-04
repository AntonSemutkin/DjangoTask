from django.urls import path
from .views import BaseView, DishesDetailView, CategoryDetailView

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('dishes/<str:ct_model>/<str:slug>/', DishesDetailView.as_view(), name='dishes_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail')
]

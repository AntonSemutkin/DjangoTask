from django.urls import path
from .views import test_view, DishesDetailView

urlpatterns = [
    path('', test_view, name='base'),
    path('dishes/<str:ct_model>/<str:slug>/', DishesDetailView.as_view(), name='dishes_detail')
]

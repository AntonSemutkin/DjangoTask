from django.shortcuts import render
from django.views.generic import DetailView, View
from .models import Soups, MainDishes, Drinks, Category
from .mixins import CategoryDetailMixin

class BaseView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_navigation()
        return render(request, 'base.html', {'categories': categories})

class DishesDetailView(CategoryDetailMixin, DetailView):
    CT_MODEL_MODEL_CLASS = {
        'soups': Soups,
        'maindishes': MainDishes,
        'drinks': Drinks
    }
    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)
        
    context_object_name = 'dishes'
    template_name = 'dishes_detail.html'
    slug_url_kwarg = 'slug'

class CategoryDetailView(CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

from django.shortcuts import render
from django.views.generic import DetailView
from .models import Soups, MainDishes, Drinks

def test_view(request):
    return render(request, 'base.html', {})

class DishesDetailView(DetailView):
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

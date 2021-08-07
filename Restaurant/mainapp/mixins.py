from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from .models import Category, Cart, Customer, Soups, MainDishes, Drinks

class CategoryDetailMixin(SingleObjectMixin):
    CATEGORY_MODEL2DISHES_MODEL = {
        'soups': Soups,
        'maindishes': MainDishes,
        'drinks': Drinks
    }
    def get_context_data(self, **kwargs):
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_MODEL2DISHES_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_navigation()
            context['category_dishes'] = model.objects.all()
            return context
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.get_categories_for_navigation()
        return context
        

class CartMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create( 
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart: 
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anon_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anon_user=True)
        self.cart = cart
        self.cart.save()
        return super().dispatch(request, *args, **kwargs)
    
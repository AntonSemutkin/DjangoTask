from django.db import transaction
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import Soups, MainDishes, Drinks, Category, LatestDishes, Customer, Cart, CartDishes, Dishes
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm
from .utils import recalc_cart


class BaseView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_navigation()
        dishes = LatestDishes.objects.get_dishes_for_main_page('soups', 'maindishes', 'drinks')
        context = {
            'categories': categories,
            'all_dishes': dishes,
            'cart': self.cart
        }
        return render(request, 'base.html', context)

class DishesDetailView(CartMixin, CategoryDetailMixin, DetailView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        return context

class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context

class AddToCartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        ct_model, dishes_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        dishes = content_type.model_class().objects.get(slug=dishes_slug)
        cart_dishes, created = CartDishes.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=dishes.id
        )
        if created:
            self.cart.dishes.add(cart_dishes)
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "?????????? ?????????????? ????????????????")
        return HttpResponseRedirect('/cart/')

class DeleteFromCartView(CartMixin, View):
    def get(self, request, *args, **kwargs): 
        ct_model, dishes_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        dishes = content_type.model_class().objects.get(slug=dishes_slug)
        cart_dishes = CartDishes.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=dishes.id
        )
        self.cart.dishes.remove (cart_dishes)
        cart_dishes.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "?????????? ?????????????? ????????????")
        return HttpResponseRedirect('/cart/')

class ChangeQTYView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        ct_model, dishes_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        dishes = content_type.model_class().objects.get(slug=dishes_slug)
        cart_dishes = CartDishes.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=dishes.id
        )
        qty = int(request.POST.get('qty'))
        cart_dishes.qty = qty
        cart_dishes.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "???????????????????? ???????????? ?????????????? ????????????????")
        return HttpResponseRedirect('/cart/')

class CartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_navigation()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)

class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_navigation()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'checkout.html', context)

class MakeOrderView(CartMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, "?????????? ?????????????? ????????????????")
            return HttpResponseRedirect('/')
        return HttpResponseRedirect("/checkout/")
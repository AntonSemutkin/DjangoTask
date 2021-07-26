from django.contrib import admin
from django import forms
from .models import *

class DrinksCategoryChoiceField(forms.ModelChoiceField):
    pass

class DrinksAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return DrinksCategoryChoiceField(Category.objects.filter(slug='drinks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Category)
admin.site.register(Ingridients)
admin.site.register(Soups)
admin.site.register(Drinks, DrinksAdmin)
admin.site.register(CartDishes)
admin.site.register(Cart)
admin.site.register(Customer)
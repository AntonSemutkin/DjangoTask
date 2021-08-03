from django.contrib import admin
from django.forms import ModelChoiceField
from .models import *


class DrinksAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='drinks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class MainDishesAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='maindishes'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SoupsAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='soups'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Soups, SoupsAdmin)
admin.site.register(MainDishes, MainDishesAdmin)
admin.site.register(Drinks, DrinksAdmin)
admin.site.register(CartDishes)
admin.site.register(Cart)
admin.site.register(Customer)
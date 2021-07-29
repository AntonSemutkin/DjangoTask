from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class LatestDishesManager:
    @staticmethod
    def get_dishes_for_main_page(*args, **kwargs):
        dishes = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_dishes = ct_model.model_class()._base_manager.all().order_by('-id')[:3]
            dishes.extend(model_dishes)
        return dishes

class LatestDishes:
    objects = LatestDishesManager()

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='ИмяКатегории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Ingridients(models.Model):
    title = models.CharField(max_length=255, verbose_name='НазваниеИнгридиента')

    def __str__(self):
        return self.title

class Dishes(models.Model): 
    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='ИмяПродукта')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описаниие', null=True)
    price = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="Цена")

    def __str__(self):
        return self.title

class Soups(Dishes):
    weight = models.CharField(max_length=5, verbose_name='МассаБлюда')
    calorie_content = models.CharField(max_length=255, verbose_name='КалорийностьБлюда')

    def __str__(self):
        return "{} :{}".format(self.category.name, self.title)

class Drinks(Dishes):
    weight = models.CharField(max_length=5, verbose_name='МассаНапитка')
    type = models.CharField(max_length=255, verbose_name='ТипНапитка')
    calorie_content = models.CharField(max_length=255, verbose_name='КалорийностьНапитка')

    def __str__(self):
        return "{} :{}".format(self.category.name, self.title)

class CartDishes(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Пользователь', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_dishes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="ОбщаяЦена")

    def __str__(self):
        return 'Блюдо: {} (для корзины)'.format(self.dishes.title)

class Cart(models.Model):
    owner = models.ForeignKey("Customer", verbose_name='Владелец корзины', on_delete=models.CASCADE)
    dishes = models.ManyToManyField(CartDishes, blank=True, related_name='related_cart')
    total_dishes = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="ОбщаяЦена")

    def __str__(self):
        return str(self.id)

class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


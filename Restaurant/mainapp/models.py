from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]

def get_dishes_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


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

class CategoryManager(models.Manager):
    CATEGORY_NAME_COUNT_NAME = {
        'Супы': 'soups__count',
        'Основное блюдо': 'maindishes__count',
        'Напитки': 'drinks__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_navigation(self):
        models = get_models_for_count('soups', 'maindishes', 'drinks')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='ИмяКатегории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})    

class Dishes(models.Model): 
    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='ИмяПродукта')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описаниие', null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Цена")

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()

class Soups(Dishes):
    ingridients = models.CharField(max_length=255, verbose_name='Состав блюда')
    weight = models.CharField(max_length=5, verbose_name='МассаБлюда')
    calorie_content = models.CharField(max_length=255, verbose_name='КалорийностьБлюда')

    def __str__(self):
        return "{} :{}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_dishes_url(self, 'dishes_detail')

class MainDishes(Dishes):
    ingridients = models.CharField(max_length=255, verbose_name='Состав блюда')
    weight = models.CharField(max_length=5, verbose_name='МассаБлюда')
    calorie_content = models.CharField(max_length=255, verbose_name='КалорийностьБлюда')

    def __str__(self):
        return "{} :{}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_dishes_url(self, 'dishes_detail')

class Drinks(Dishes):
    ingridients = models.CharField(max_length=255, verbose_name='Состав блюда')
    weight = models.CharField(max_length=5, verbose_name='МассаНапитка')
    type = models.CharField(max_length=255, verbose_name='ТипНапитка')
    calorie_content = models.CharField(max_length=255, verbose_name='КалорийностьНапитка')

    def __str__(self):
        return "{} :{}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_dishes_url(self, 'dishes_detail')

class CartDishes(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Пользователь', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_dishes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="ОбщаяЦена")

    def __str__(self):
        return 'Блюдо: {} (для корзины)'.format(self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)



class Cart(models.Model):
    owner = models.ForeignKey("Customer", null=True, verbose_name='Владелец корзины', on_delete=models.CASCADE)
    dishes = models.ManyToManyField(CartDishes, blank=True, related_name='related_cart')
    total_dishes = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="ОбщаяЦена")
    in_order = models.BooleanField(default=False)
    for_anon_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        cart_data = self.dishes.aggregate(models.Sum('final_price'), models.Count('id'))
        if cart_data.get('final_price__sum'):
            self.final_price = cart_data['final_price__sum']
        else:
            self.final_price = 0
        self.total_dishes = cart_data['id__count']
        super().save(*args, **kwargs)

class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='номер телефона')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Адрес')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


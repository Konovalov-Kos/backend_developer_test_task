from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from datetime import datetime, timedelta

from config import settings

class Category(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)
    parent = models.ForeignKey("Category", related_name="pid", on_delete=models.CASCADE, blank=True, null=True)

    PARAMS = Choices(
        ('following', 'following'),
        ('price_to', 'price_to'),
        ('price_from', 'price_from'),
    )

    @property
    def has_childs(self):
        return Category.objects.filter(parent=self).exists()

    @property
    def childs(self):
        return Category.objects.filter(parent=self)

    @property
    def products(self):
        return Product.objects.filter(category=self).order_by('-id')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"http://localhost:8000/products/{self.slug}/"


class Product(TimeStampedModel):
    GRADE_CHOICES = Choices(
        ('base', 'base', _('Base')),
        ('standard', 'standard', _('Standard')),
        ('premium', 'premium', _('Premium')),
    )

    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)
    price = models.DecimalField(_('Price'), decimal_places=2, max_digits=9)
    description = models.TextField(_('Description'), blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    prod_img = models.CharField("Image", max_length=200, default='', null=True, blank=True)

    @property
    def prod_comments(self):
        time_from = datetime.now() - timedelta(hours=24)
        return Comment.objects.filter(created_time__gte=time_from)

    @property
    def prods_category_list(self):
        category = self.category
        mass = []
        while category.parent != None:
            mass.append(category)
            category = category.parent
        mass.append(category)
        mass.reverse()
        return mass

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"http://localhost:8000/products/{self.category.slug}/{self.slug}/"


class Like(TimeStampedModel):
    product = models.ForeignKey(Product, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='likes', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        unique_together = (('product', 'user'), ('product', 'ip'))

    def __str__(self):
        return '{} from {}'.format(self.product, self.user or self.ip)

    def get_absolute_url(self):
        return f"http://localhost:8000/products/{self.product.category.slug}/{self.product.slug}/"


class Comment(TimeStampedModel):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    ip = models.GenericIPAddressField(blank=True, null=True)
    text = models.TextField(_('Comment'))
    created_time = models.DateField(auto_now_add=False)

    def __str__(self):
        return 'comment from {}'.format(self.user or self.ip)

    def get_absolute_url(self):
        return f"http://localhost:8000/products/{self.product.category.slug}/{self.product.slug}/"

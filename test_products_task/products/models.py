from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel

from config import settings


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)

    PARAMS = Choices(
        ('following', 'following'),
        ('price_to', 'price_to'),
        ('price_from', 'price_from'),
    )

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    GRADE_CHOICES = Choices(
        ('base', 'base', _('Base')),
        ('standard', 'standard', _('Standard')),
        ('premium', 'premium', _('Premium')),
    )

    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'))
    price = models.DecimalField(_('Price'), decimal_places=2, max_digits=9)
    description = models.TextField(_('Description'), blank=True)
    category = models.ForeignKey(Category, related_name='products')

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.name


class Like(TimeStampedModel):
    product = models.ForeignKey(Product, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='likes')
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        unique_together = (('product', 'user'), ('product', 'ip'))

    def __str__(self):
        return '{} from {}'.format(self.product, self.user or self.ip)


class Comment(TimeStampedModel):
    product = models.ForeignKey(Product, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='comments')
    ip = models.GenericIPAddressField(blank=True, null=True)
    text = models.TextField(_('Comment'))

    def __str__(self):
        return 'comment from {}'.format(self.user or self.ip)

# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include
from test_products_task.products import views

urlpatterns = [
    url(r'^$', views.CategoryListView.as_view(), name='category_list'),
    url(r'^cart/$', views.CartView.as_view(), name='cart'),
    url(r'^(?P<product_pk>[0-9]+)/like/$', views.LikeToggleView.as_view(), name='like_toggle'),
    url(r'^(?P<product_pk>[0-9]+)/add/to/cart/$', views.AddToCartView.as_view(), name='add_to_cart'),
    url(r'^(?P<category_slug>.+)/(?P<product_slug>.+)/$', views.ProductDetailView.as_view(), name='product_detail'),
    url(r'^(?P<category_slug>.+)/$', views.CategoryDetailView.as_view(), name='category_detail'),
]

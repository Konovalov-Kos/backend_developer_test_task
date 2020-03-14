from datetime import timedelta
from unittest.case import skipUnless

from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import UserModel
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.utils import timezone
from freezegun import freeze_time

from test_products_task.products.models import Category, Product, Like
from test_products_task.products.tests.factories import CategoryFactory, ProductFactory, LikeFactory, CommentFactory
from test_products_task.users.tests.factories import UserFactory

User = get_user_model()


class CategoryListViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryFactory()
        cls.category_2 = CategoryFactory()
        cls.user = UserFactory()
        cls.url = reverse('products:category_list')

    def test_mainpage(self):
        client = Client()
        response = client.get(self.url)
        self.assertEquals(response.status_code, 200)


class CategoryDetailViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryFactory()
        cls.product_1 = ProductFactory(category=cls.category, price=30)
        cls.product_2 = ProductFactory(category=cls.category, price=40)
        cls.product_3 = ProductFactory(category=cls.category, price=50)

        cls.user = UserFactory()
        cls.url = reverse('products:category_detail', args=(cls.category.slug, ))

    def test_detail_page(self):
        client = Client()
        response = client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')

    def test_user_detail_page(self):
        client = Client()
        client._login(self.user, 'django.contrib.auth.backends.ModelBackend')
        response = client.get(self.url)
        self.assertEquals(response.status_code, 200)


class LikeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryFactory()
        cls.product_1 = ProductFactory(category=cls.category, price=30)

        cls.user = UserFactory()
        cls.url_like = reverse('products:product_detail', args=(cls.category.slug, cls.product_1.slug))

    def test_invalid_product(self):
        client = Client()
        response = client.post(self.url_like, {'change_like': 'wrong_product_slug'})
        self.assertEquals(response.status_code, 404)

    def test_anonymous_like_product(self):
        client = Client()
        self.assertEquals(self.product_1.likes.count(), 0)
        response = client.post(self.url_like, {'change_like': self.product_1.slug})
        self.assertEquals(self.product_1.likes.count(), 1)
        self.assertEquals(response.status_code, 302)

    def test_anonymous_dislike_product(self):
        client = Client()
        self.assertEquals(self.product_1.likes.count(), 0)
        response = client.post(self.url_like, {'change_like': self.product_1.slug})
        self.assertEquals(self.product_1.likes.count(), 1)
        self.assertEquals(response.status_code, 302)
        response = client.post(self.url_like, {'change_like': self.product_1.slug})
        self.assertEquals(self.product_1.likes.count(), 0)
        self.assertEquals(response.status_code, 302)

    def test_user_like_product(self):
        client = Client()
        client._login(self.user, 'django.contrib.auth.backends.ModelBackend')
        self.assertEquals(self.product_1.likes.count(), 0)
        response = client.post(self.url_like, {'change_like': self.product_1.slug})
        self.assertEquals(self.product_1.likes.count(), 1)
        self.assertEquals(response.status_code, 302)

    def test_user_dislike_product(self):
        client = Client()
        client._login(self.user, 'django.contrib.auth.backends.ModelBackend')
        self.assertEquals(self.product_1.likes.count(), 0)
        response = client.post(self.url_like, {'change_like': self.product_1.slug})
        self.assertEquals(self.product_1.likes.count(), 1)
        self.assertEquals(response.status_code, 302)
        response = client.post(self.url_like, {'change_like': self.product_1.slug})
        self.assertEquals(self.product_1.likes.count(), 0)
        self.assertEquals(response.status_code, 302)

class CommentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryFactory()
        cls.product_1 = ProductFactory(category=cls.category, price=20)
        cls.user = UserFactory()
        cls.url_comment = reverse('products:product_detail', args=(cls.category.slug, cls.product_1.slug))

    def test_anonymous_comment(self):
        client = Client()
        self.assertEquals(self.product_1.comments.count(), 0)
        response = client.post(
                                self.url_comment,
                                {'username_comment': self.user.username, 'comment_message': 'test_message',
                                 'add_comment': self.product_1.slug}
                               )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.product_1.comments.count(), 1)

    def test_user_comment(self):
        client = Client()
        client._login(self.user, 'django.contrib.auth.backends.ModelBackend')
        self.assertEquals(self.product_1.comments.count(), 0)
        response = client.post(
            self.url_comment,
            {'username_comment': self.user.username, 'comment_message': 'test_message',
             'add_comment': self.product_1.slug}
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.product_1.comments.count(), 1)
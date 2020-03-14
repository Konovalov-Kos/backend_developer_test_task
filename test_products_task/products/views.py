from collections import OrderedDict
from datetime import timedelta

from braces.views import JSONResponseMixin, AjaxResponseMixin
from django.contrib import messages
from django.db.models import Sum, Case, When, IntegerField, Count, F, Q
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, FormView, TemplateView

from test_products_task.common.mixins import ActiveTabMixin
from test_products_task.common.utils import get_ip_from_request
from test_products_task.products.forms import LikeForm
from test_products_task.products.models import Category, Product, Like, Comment
from datetime import datetime
from django.contrib import messages

class MainView(TemplateView):
    template_name = "base.html"

    def get_ordered_grade_info(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grade_info'] = self.get_ordered_grade_info()
        return context


class CategoryDetailView(TemplateView):
    template_name = "products/category_detail.html"
    model = Category
    slug_url_kwarg = 'category_slug'
    PARAM_FOLLOWING = 'following'
    PARAM_PRICE_FROM = 'price_from'
    PARAM_PRICE_TO = 'price_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = get_object_or_404(Category, slug=kwargs["category_slug"])
        if cat.has_childs:
            context['cat'] = cat
        else:
            self.template_name = 'products/product_list.html'
            context['cat'] = cat
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('change_like'):
            change_like(request, request.POST.get('change_like'))
        return redirect(reverse('products:category_detail', kwargs=kwargs))


class ProductDetailView(DetailView):
    model = Product
    slug_url_kwarg = 'product_slug'
    category = None

    def get(self, request, *args, **kwargs):
        category_slug = kwargs['category_slug']
        try:
            self.category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        category_slug = kwargs['category_slug']
        try:
            self.category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404

        if request.POST.get('add_comment'):
            if len(request.POST.get('comment_message')) > 500:
                messages.add_message(request, messages.ERROR, 'Maximum comment length exceeded. (max 500)')
                return HttpResponseRedirect(reverse('products:product_detail', kwargs=kwargs))
            if len(request.POST.get('comment_message').replace(' ', '')) > 0:
                product = get_object_or_404(Product, slug=request.POST.get('add_comment'))
                if product:
                    current_user = request.user
                    if current_user.is_authenticated:
                        Comment.objects.create(user=current_user, name=request.POST.get('username_comment'), product=product, text=request.POST.get('comment_message'), created_time=datetime.now())
                    else:
                        user_ip = get_ip(request)
                        Comment.objects.create(ip=user_ip, name=request.POST.get('username_comment'), product=product, text=request.POST.get('comment_message'), created_time=datetime.now())
            else:
                messages.add_message(request, messages.ERROR, 'Comment length cannot be zero.')
            return HttpResponseRedirect(reverse('products:product_detail', kwargs=kwargs))
        if request.POST.get('change_like'):
            change_like(request, request.POST.get('change_like'))
        return HttpResponseRedirect(reverse('products:product_detail', kwargs=kwargs))


class LikeToggleView(AjaxResponseMixin, JSONResponseMixin, FormView):
    http_method_names = ('post', )
    form_class = LikeForm
    product = None

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        product_id = kwargs['product_pk']
        try:
            self.product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        raise NotImplementedError()


class AddToCartView(AjaxResponseMixin, JSONResponseMixin, FormView):
    http_method_names = ('post',)
    success_url = reverse_lazy('products:cart')

    def post(self, request, *args, **kwargs):
        raise NotImplementedError


class CartView(ActiveTabMixin, TemplateView):
    active_tab = 'cart'
    template_name = 'products/cart.html'

#решил сделать функцию и вызывать ее во вью категорий и продуктов, чтобы не повторять код
def change_like(request, slug):
    prod = get_object_or_404(Product, slug=slug)
    try:
        current_user = request.user
        if current_user.is_authenticated:
            if Like.objects.filter(product=prod, user=request.user).exists():
                Like.objects.filter(product=prod, user=request.user).delete()
            else:
                Like.objects.create(product=prod, user=request.user)
        else:
            user_ip = get_ip(request)
            if Like.objects.filter(product=prod, ip=user_ip).exists():
                Like.objects.filter(product=prod, ip=user_ip).delete()
            else:
                Like.objects.create(product=prod, ip=user_ip)
        return True
    except:
        return False

#также функция получения ip пользователя вынесена чтобы не повторять код
def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#использую функцию для того чтобы ассигнить данные для меню во все темплейты с помощью context_processors
def menu(request):
    return {'Category_0': Category.objects.filter(parent=None)}
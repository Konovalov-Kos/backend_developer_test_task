from django.contrib import admin

from test_products_task.products.models import Category, Product, Like, Comment


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    view_on_site = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    view_on_site = True


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    view_on_site = True

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    view_on_site = True
# Generated by Django 3.0.3 on 2020-03-04 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Slug'),
        ),
    ]

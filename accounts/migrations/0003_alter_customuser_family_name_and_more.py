# Generated by Django 5.1.3 on 2024-11-13 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_customuser_options_customuser_family_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='family_name',
            field=models.CharField(max_length=30, verbose_name='性'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(max_length=30, verbose_name='名前'),
        ),
    ]

# Generated by Django 4.0.7 on 2022-08-21 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_alter_quote_author_delete_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quote',
            name='date',
        ),
        migrations.AlterField(
            model_name='quote',
            name='message',
            field=models.TextField(max_length=100000),
        ),
    ]
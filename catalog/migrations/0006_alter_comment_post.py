# Generated by Django 4.0.7 on 2022-08-22 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_alter_comment_options_alter_quote_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='catalog.quote'),
        ),
    ]

# Generated by Django 4.0.7 on 2022-08-21 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_remove_quote_date_alter_quote_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anonym_name', models.CharField(max_length=100)),
                ('text_comment', models.TextField(max_length=5000)),
                ('quote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.quote')),
            ],
        ),
    ]
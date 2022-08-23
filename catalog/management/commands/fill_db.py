from catalog.models import Quote
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Create faker values to DB. Warning: use 1 time!'

    def add_arguments(self, parser):
        parser.add_argument('number', type=int, choices=range(1, 10000), help='Number of the creating values')

    def handle(self, *args, **options):
        number = options['number']
        obj = []
        quotes = []
        for i in range(number):
            users = User(username=fake.name(),
                         email=fake.email(),
                         password=make_password(str(fake.password())))
            obj.append(users)
        User.objects.bulk_create(obj)
        for i in range(number):
            quote = Quote(
                          message=fake.text(),
                          author_id=User.objects.get(pk=i+1).pk)
            quotes.append(quote)
        Quote.objects.bulk_create(quotes)
        self.stdout.write(self.style.SUCCESS('DB is populated %s values successfully!' % number))

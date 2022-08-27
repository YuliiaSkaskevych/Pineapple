from catalog.models import Quote, Comment
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
        users = []
        quotes = []
        comments = []
        for i in range(number):
            user = User(username=fake.name(),
                        email=fake.email(),
                        password=make_password(str(fake.password())))
            users.append(user)
        User.objects.bulk_create(users)
        for x in range(35):
            for i in range(number):
                quote = Quote(heading=fake.word(),
                              description=fake.text(),
                              message=fake.text(),
                              status='published',
                              author_id=User.objects.get(pk=i + 1).pk)
                quotes.append(quote)
            Quote.objects.bulk_create(quotes)
        for x in range(20):
            for i in range(number):
                comment = Comment(name=fake.name(),
                                  text=fake.text(),
                                  published=True,
                                  post_id=Quote.objects.get(id=i + 1).pk)
                comments.append(comment)
            Comment.objects.bulk_create(comments)
        self.stdout.write(self.style.SUCCESS('DB is populated %s values successfully!' % number))

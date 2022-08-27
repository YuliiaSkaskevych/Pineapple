from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Quote(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    heading = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    message = models.TextField(max_length=100000)
    image = models.ImageField("image", upload_to='static/images', default=None)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    publish = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.heading


class Comment(models.Model):
    post = models.ForeignKey(Quote, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    text = models.CharField(max_length=5000)
    created = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)

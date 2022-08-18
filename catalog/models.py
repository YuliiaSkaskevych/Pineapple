from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    age = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.name


class Quote(models.Model):
    heading = models.CharField(max_length=200, primary_key=True)
    message = models.CharField(max_length=10000000, primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return f'Author: {self.author}'

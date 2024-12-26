from django.db import models


class Joke(models.Model):
    CATEGORY_CHOICES = [
        ('dark', 'Черный юмор'),
        ('jokes300', 'Шутки за 300'),
        ('knockknock', 'Тук-тук шутки'),
        ('army', 'Армейские анекдоты'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    text = models.TextField()

    def __str__(self):
        return f"{self.get_category_display()}: {self.text[:50]}..."



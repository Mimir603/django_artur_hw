from django.shortcuts import render
from .models import Joke


def joke_list(request):
    categories = Joke.CATEGORY_CHOICES
    jokes_by_category = {category[0]: Joke.objects.filter(category=category[0]) for category in categories}
    return render(request, 'jokes/joke_list.html', {'jokes_by_category': jokes_by_category})

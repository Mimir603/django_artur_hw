from django.urls import path

from testapp.views import add, index, get, test_cookie, test_email

app_name = 'testapp'

urlpatterns = [
    path('test_email/', test_email, name='test_email'),
    path('test_cookie/', test_cookie, name='test_cookie'),
    path('add/', add, name='add'),
    path('get/<path:filename>/', get, name='get'),
    path('', index, name='index'),
]

from django.urls import path

from testapp import views
from testapp.views import add, index, get, test_email

app_name = 'testapp'

urlpatterns = [
    path('send-email/', views.send_test_email, name='send_test_email'),
    path('test_email/', test_email, name='test_email'),
    path('add/', add, name='add'),
    path('get/<path:filename>/', get, name='get'),
    path('', index, name='index'),
]
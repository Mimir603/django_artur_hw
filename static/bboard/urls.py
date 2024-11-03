from django.urls import path, re_path

from bboard.models import Bb
from bboard.views import (index, by_rubric, BbCreateView, add_and_save, detail,
                          BbByRubricView, BbDetailView, BbAddView, BbEditView,
                          BbDeleteView, BbIndexView, BbRedirectView, edit,
                          rubrics, search)  # add, add_save

app_name = 'bboard'

urlpatterns = [
    path('rubrics/', rubrics, name='rubrics'),

    path('add/', BbCreateView.as_view(), name='add'),

    # path('update/<int:pk>/', BbEditView.as_view(), name='update'),
    path('update/<int:pk>/', edit, name='update'),

    path('delete/<int:pk>/', BbDeleteView.as_view(), name='delete'),
    path('<int:rubric_id>/', BbByRubricView.as_view(), name='by_rubric'),

    path('detail/<int:pk>/', BbDetailView.as_view(), name='detail'),
    # path('detail/<int:year>/<int:month>/<int:day>/<int:pk>/',
    #      BbDetailView.as_view(), name='detail'),
    path('detail/<int:year>/<int:month>/<int:day>/<int:pk>/',
         BbRedirectView.as_view(), name='old_detail'),

    path('', index, name='index'),
    # path('', BbIndexView.as_view(), name='index'),

    path('search/', search, name='search'),
]

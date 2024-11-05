from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bboard.models import Bb
from bboard.views import (index, by_rubric, BbCreateView, add_and_save, detail,
                          BbByRubricView, BbDetailView, BbAddView, BbEditView,
                          BbDeleteView, BbIndexView, BbRedirectView, edit,
                          rubrics, search, api_rubrics, api_rubric_detail, APIRubrics, APIRubricDetail,
                          APIRubricViewSet, APIBboards, APIBboardViewSet)  # add, add_save

app_name = 'bboard'

router = DefaultRouter()
router.register('rubrics', APIRubricViewSet)

BbRouter = DefaultRouter()
BbRouter.register('rubrics', APIBboardViewSet)

urlpatterns = [
    # path('api/rubrics/<int:pk>/', api_rubric_detail),
    # path('api/rubrics/', api_rubrics),

    # path('api/rubrics/', APIRubrics.as_view()),
    # path('api/rubrics/<int:pk>/', APIRubricDetail.as_view()),

    path('api/', include(router.urls)), #api/rubrics/ выдает GET и POST,
                                        #api/rubrics/<ключ>, выдает GET, PUT и DELETE

    path('api/bb/<int:pk>/', APIBboards.as_view()),
    path('api/bb/<int:pk>/', APIRubricDetail.as_view()),

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

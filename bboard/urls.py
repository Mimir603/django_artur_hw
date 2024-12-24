from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bboard import views
from bboard.models import Bb
from bboard.views import (index, by_rubric, BbCreateView, add_and_save, detail,
                          BbByRubricView, BbDetailView, BbAddView, BbEditView,
                          BbDeleteView, BbIndexView, BbRedirectView, edit,
                          rubrics, search, api_rubrics, api_rubric_detail, APIRubrics, APIRubricDetail,
                          APIRubricViewSet)

app_name = 'bboard'

router = DefaultRouter()
router.register('rubrics', APIRubricViewSet)

# BbRouter = DefaultRouter()
# BbRouter.register('rubrics', APIBboardViewSet)

urlpatterns = [
    path('bb/', views.bb_list, name='bb_list'),
    path('bb/<int:pk>/', views.bb_detail, name='bb_detail'),
    path('bb/<int:pk>/edit/', views.bb_edit, name='bb_edit'),

    path('api/', include(router.urls)), #api/rubrics/ выдает GET и POST,
    #                                     #api/rubrics/<ключ>, выдает GET, PUT и DELETE
    #
    # path('api/bboard/', APIBboards.as_view()),
    # path('api/bboard/<int:pk>/', APIRubricDetail.as_view()),

    path('api/drf-auth/', include('rest_framework.urls')),

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

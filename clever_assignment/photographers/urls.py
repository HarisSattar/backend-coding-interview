from django.urls import path
from .views import PhotographerListView

urlpatterns = [
    path('', PhotographerListView.as_view(), name='photographer-list'),
]
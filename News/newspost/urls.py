from django.urls import path

from .views import IndexView


urlpatterns = [
    path('nwp/', IndexView.as_view(), name='nwp'),
]

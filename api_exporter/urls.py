from django.urls import path

from api_exporter import views
from metrics.views import metrics

urlpatterns = [
    path('', views.index, name='index'),
    path('metrics', metrics),
]
handler404 = "api_exporter.views.view_404"



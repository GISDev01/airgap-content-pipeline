from django.urls import path
from cms.views import DockerImageListView

urlpatterns = [
    path('docker/', DockerImageListView.as_view()),
]
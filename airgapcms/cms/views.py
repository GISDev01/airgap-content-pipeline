from django.shortcuts import render
from django.views.generic import ListView

from .models import DockerImage

# Create your views here.
class DockerImageListView(ListView):

    model = DockerImage
    template_name = 'dockerimage_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['docker_image_list'] = DockerImage.objects.all()
        context['book_docker_image_pulled_list'] = DockerImage.objects.filter(downloaded=True)
        context['book_docker_image_pending_list'] = DockerImage.objects.filter(downloaded=False)
        return context
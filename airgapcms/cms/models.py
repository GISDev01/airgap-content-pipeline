from django.db import models

# Create your models here.
class DockerImage(models.Model):
    def __str__(self):
        return self.image + ":" + self.tag

    image = models.CharField(max_length=200)
    tag = models.CharField(max_length=128)
    downloaded = models.BooleanField(default=False)
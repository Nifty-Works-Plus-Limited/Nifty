from django.db import models


class Parameter(models.Model):
    parameter = models.CharField(max_length=50)
    description = models.TextField()

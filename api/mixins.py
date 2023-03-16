from django.db import models


class ModelTimeStampMixin(models.Model):
    """
    Adds created_at and updated_at columns to a model.
    @args: models ([type]): [description]
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

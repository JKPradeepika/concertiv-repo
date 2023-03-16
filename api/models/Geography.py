from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class Geography(ModelTimeStampMixin, models.Model):
    """
    A city, state, region, country, or continent in which a User is located.
    Geographies form a tree structure in order to facilitate spend reporting on multiple geographic levels.

    Args:
        - name (TextField): The name of the geography
        - parent (ForeignKey): (optional) The parent of this Geography.
    """

    name = models.TextField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Geographies")
        db_table = "geographies"

    def __str__(self) -> str:
        return self.name

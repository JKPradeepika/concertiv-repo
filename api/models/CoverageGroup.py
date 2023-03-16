from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class CoverageGroup(ModelTimeStampMixin, models.Model):
    """
    Args:
        - name (TextField): The name of the coverage group
    """

    name = models.TextField()

    class Meta:
        verbose_name_plural = _("Coverage Groups")
        db_table = "coverages_groups"

    def __str__(self) -> str:
        return self.name

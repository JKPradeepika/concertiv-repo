from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class Department(ModelTimeStampMixin, models.Model):
    """
    Args:
        - name (TextField): The name of the department
    """

    name = models.TextField()

    class Meta:
        verbose_name_plural = _("Departments")
        db_table = "departments"

    def __str__(self) -> str:
        return self.name

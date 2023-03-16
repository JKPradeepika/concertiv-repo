from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class DocumentType(ModelTimeStampMixin, models.Model):
    """
    Args:
        - name (CharField): The name of the document type
    """

    name = models.CharField(max_length=250)

    class Meta:
        verbose_name_plural = _("Document Types")
        db_table = "documents_types"

    def __str__(self) -> str:
        return self.name

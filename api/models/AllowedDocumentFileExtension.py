from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin


class AllowedDocumentFileExtension(ModelTimeStampMixin, models.Model):
    """
    Dynamic listing of allowed file extensions for documents.
    To be managed via admin console.
    """

    name = models.TextField()

    class Meta:
        verbose_name_plural = _("Allowed Document File Extensions")
        db_table = "allowed_document_file_extensions"

    def __str__(self) -> str:
        return self.name

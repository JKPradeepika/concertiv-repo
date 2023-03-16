from django.db import models
from django.utils.translation import gettext_lazy as _

from api.helpers import derive_subdir_path_based_on_fk_fields
from api.mixins import ModelTimeStampMixin
from api.models.Buyer import Buyer
from api.models.Contract import Contract
from api.models.Product import Product
from api.models.Supplier import Supplier
from api.models.DocumentType import DocumentType


class Document(ModelTimeStampMixin, models.Model):
    """
    Args:
        - name (CharField): The name of the document
        - type (ForeignKey): The type of the document
        - date (DateField): The date of the document (default to now)
        - notes (TextField): Notes about the document
        - file (FileField): file (linked with s3 through django-storages library)
        # FK Fields (Buyer, Supplier, Contract, Product)
    """

    name = models.CharField(max_length=250)
    type = models.ForeignKey(DocumentType, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=derive_subdir_path_based_on_fk_fields, blank=True, null=True)

    buyer = models.ForeignKey(Buyer, blank=True, null=True, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, blank=True, null=True, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, blank=True, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Documents")
        db_table = "documents"

    def __str__(self) -> str:
        return self.name

    def download_url(self):
        return self.file.url

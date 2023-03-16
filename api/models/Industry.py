from django.db import models
from django.utils.translation import gettext_lazy as _

from api.constants import DOMAIN_MARKET_DATA, DOMAINS
from api.mixins import ModelTimeStampMixin


class Industry(ModelTimeStampMixin, models.Model):
    """
    Fields whose type changed from Profiler:
    - vertical (FK) -> domain (TextField)

    Args:
        - name (TextField): The name of the industry
        - domain (TextField): The domain to which the industry belongs
    """

    name = models.TextField()
    domain = models.SmallIntegerField(choices=DOMAINS, default=DOMAIN_MARKET_DATA)

    class Meta:
        verbose_name_plural = _("Industries")
        db_table = "industries"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_domain_display()})"

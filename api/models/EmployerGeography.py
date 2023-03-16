from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.Employer import Employer
from api.models.Geography import Geography


class EmployerGeography(ModelTimeStampMixin, models.Model):
    """
    EmployerGeographies in Komodo just represent a ManyToMany relationship between employers and geographies.
    The name can be overridden.

    EmployerGeography represent geographies specific to a certain employer.
    For spend reporting purposes, a geography FK can be provided which associates a
    employer-specific geography with a global geography.

    Fields dropped from Profiler:
    - users_count
    - geography_restrictions_count

    Args:
        - name (TextField): The name of the geography
        - employer (ForeignKey): The Employer to which this EmployerGeography belongs
        - geography (ForeignKey): (optional) The global Geography to which this EmployerGeography
            corresponds. Used for reporting across Employers.
        - parent (ForeignKey): (optional) The parent of this EmployerGeography. Used for reporting on different
            geographic levels (continents vs. countries vs. cities, etc...).
    """

    name = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Employers Geographies")
        db_table = "employers_geographies"

    def __str__(self) -> str:
        return self.name

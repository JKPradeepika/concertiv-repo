from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import ModelTimeStampMixin
from api.models.CoverageGroup import CoverageGroup
from api.models.Employer import Employer


class EmployerCoverageGroup(ModelTimeStampMixin, models.Model):
    """
    EmployerCoverageGroups in Komodo just represent a ManyToMany relationship between employers and coverage groups.
    The name can be overridden.

    EmployerCoverageGroups in Profiler represent coverage groups specific to a certain employer.
    For spend reporting purposes, a coverage_group FK can be provided which associates a
    employer-specific coverage group with a global coverage group.

    Args:
        - name (TextField): The name of the coverage group
        - employer (ForeignKey): The Employer to which this EmployerCoverageGroup belongs
        - coverage_group (ForeignKey): (optional) The global CoverageGroup to which this EmployerCoverageGroup
            corresponds. Used for reporting across Employers.
    """

    name = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    coverage_group = models.ForeignKey(CoverageGroup, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Employers Coverages Groups")
        db_table = "employers_coverages_groups"

    def __str__(self) -> str:
        return self.name

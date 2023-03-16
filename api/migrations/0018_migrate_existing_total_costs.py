# Generated by Django 4.1.3 on 2023-01-19 19:23

from django.db import migrations
from api.models import LicensePeriod


def forward_func(*args, **kwargs) -> None:
    """
    Note that this uses a current model rather than a historical model,
    going against Django's advice here:
    https://docs.djangoproject.com/en/4.1/topics/migrations/#historical-models

    However, this migration has been tested both in a fresh database install
    and in rolling forward and rolling back, and no errors have been observed
    (this was the reasoning Django provided for why not to do this).

    The reason for going against this advice was because it allows significant
    code reuse - the calculated total price field is calculated the same way in
    this migration as it is calculated on the fly.
    """
    license_periods = LicensePeriod.objects.only(
        "type",
        "price",
        "price_currency",
        "incremental_user_price",
        "incremental_user_price_currency",
        "max_users",
        "subscription",
        "start_date",
        "end_date",
    ).all()
    for lp in license_periods:
        lp.save()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_contract_calculated_total_price_and_more"),
    ]

    operations = [
        migrations.RunPython(forward_func, migrations.RunPython.noop, elidable=True)
    ]

# Generated by Django 4.1.3 on 2023-01-24 00:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0021_unique_restrictions_per_subscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="reseller_supplier",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="api.supplier"),
        ),
    ]

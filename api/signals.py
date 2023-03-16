from contextlib import suppress
from typing import Any, Optional, Union

import boto3
from django.db.models import QuerySet, Sum
from django.db.models.signals import post_delete, post_save
from django.core.mail import EmailMessage
from django.dispatch import receiver
from djmoney.money import Money
import uuid

from api.models import Contract, EmployeeLicense, LicensePeriod, Subscription, Document, User
from komodo_backend.settings import (
    AWS_S3_REGION_NAME,
    AWS_S3_ACCESS_KEY_ID,
    AWS_S3_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
)
from komodo_backend.settings import config


@receiver(post_save, sender=EmployeeLicense)
def notify_license_periods_of_employee_license_count_update(
    sender: EmployeeLicense, instance: EmployeeLicense, created: bool, **kwargs: dict[str, Any]
) -> None:
    subscription = get_subscription_from_model_object_if_exists(instance)
    if subscription:
        update_all_license_period_calculated_total_prices(subscription)


@receiver(post_delete, sender=EmployeeLicense)
def notify_license_periods_of_deleted_employee_license(
    sender: EmployeeLicense, instance: EmployeeLicense, **kwargs: dict[str, Any]
) -> None:
    subscription = get_subscription_from_model_object_if_exists(instance)
    if subscription:
        update_all_license_period_calculated_total_prices(subscription)


@receiver(post_save, sender=LicensePeriod)
def notify_subscription_and_contract_of_license_period_change(
    sender: LicensePeriod, instance: LicensePeriod, created: bool, **kwargs: dict[str, Any]
) -> None:
    subscription = get_subscription_from_model_object_if_exists(instance)
    if not subscription:
        return
    update_read_only_subscription_data(subscription)

    if not subscription.contract:
        return
    update_read_only_contract_data(subscription.contract)


@receiver(post_delete, sender=LicensePeriod)
def notify_subscription_and_contract_of_license_period_deletion(
    sender: LicensePeriod, instance: LicensePeriod, **kwargs: dict[str, Any]
) -> None:
    subscription = get_subscription_from_model_object_if_exists(instance)
    if not subscription:
        return
    update_read_only_subscription_data(subscription)

    if not subscription.contract:
        return
    update_read_only_contract_data(subscription.contract)


@receiver(post_delete, sender=Subscription)
def notify_contract_of_subscription_deletion(sender: Subscription, instance: Subscription, **kwargs) -> None:
    try:
        update_read_only_contract_data(instance.contract)
    except Exception as ex:
        print(ex.__str__())
        # This exception captures multiple errors like before checking as well as others in data migration process
        return


def update_all_license_period_calculated_total_prices(subscription: Subscription) -> QuerySet[LicensePeriod]:
    """
    Recalculates total price of ALL subscription's associated license periods.
    """
    license_periods = LicensePeriod.objects.filter(subscription=subscription)
    for lp in license_periods:
        lp.save()  # save() method recalculates calculated_total_price and stores it
    return license_periods


def update_read_only_subscription_data(subscription: Subscription) -> None:
    update_subscription_start_and_end_dates(subscription)
    sub_lps = LicensePeriod.objects.filter(subscription=subscription)
    with suppress(TypeError):
        subscription.calculated_total_price = calculate_total_price_of_all_license_periods(sub_lps)
        subscription.proposal_price = calculate_total_proposal_price(sub_lps)
    subscription.save()


def update_read_only_contract_data(contract: Contract) -> None:
    contract_subscriptions = Subscription.objects.filter(contract=contract)
    update_contract_start_and_end_dates(contract, contract_subscriptions)
    contract_lps = LicensePeriod.objects.filter(subscription__in=contract_subscriptions)
    with suppress(TypeError):
        contract.calculated_total_price = calculate_total_price_of_all_license_periods(contract_lps)
        contract.proposal_price = calculate_total_proposal_price(contract_lps)
    contract.save()


def calculate_total_price_of_all_license_periods(license_periods: QuerySet[LicensePeriod]) -> Money:
    return license_periods.aggregate(sum=Sum("calculated_total_price"))["sum"]


def calculate_total_proposal_price(license_periods: QuerySet[LicensePeriod]) -> Optional[Money]:
    if license_periods.filter(proposal_price__isnull=True).exists():
        return None
    return license_periods.aggregate(sum=Sum("proposal_price"))["sum"]


def update_subscription_start_and_end_dates(subscription: Subscription) -> Subscription:
    license_periods = LicensePeriod.objects.filter(subscription=subscription)
    earliest_lp, latest_lp = None, None
    with suppress(LicensePeriod.DoesNotExist):
        earliest_lp = license_periods.earliest("start_date")
    with suppress(LicensePeriod.DoesNotExist):
        latest_lp = license_periods.latest("end_date")

    subscription.start_date = earliest_lp.start_date if earliest_lp else None
    subscription.end_date = latest_lp.end_date if latest_lp else None
    subscription.save()
    return subscription


def update_contract_start_and_end_dates(contract: Contract, subscriptions: QuerySet[Subscription]) -> Contract:
    license_periods = LicensePeriod.objects.filter(subscription__in=subscriptions)
    earliest_lp, latest_lp = None, None
    with suppress(LicensePeriod.DoesNotExist):
        earliest_lp = license_periods.earliest("start_date")
    with suppress(LicensePeriod.DoesNotExist):
        latest_lp = license_periods.latest("end_date")

    contract.start_date = earliest_lp.start_date if earliest_lp else None
    contract.end_date = latest_lp.end_date if latest_lp else None
    contract.save()
    return contract


def get_subscription_from_model_object_if_exists(
    model_obj: Union[EmployeeLicense, LicensePeriod]
) -> Optional[Subscription]:
    """Catches error resulting from a deleted subscription being referenced on a deleted LicensePeriod."""
    try:
        return model_obj.subscription
    except Subscription.DoesNotExist:
        return


@receiver(post_delete, sender=Document)
def delete_document_in_s3_bucket(instance: Document, **kwargs) -> None:
    try:
        s3 = boto3.resource(
            "s3",
            region_name=AWS_S3_REGION_NAME,
            aws_access_key_id=AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_S3_SECRET_ACCESS_KEY,
        )
        s3.Object(AWS_STORAGE_BUCKET_NAME, instance.file.__str__()).delete()
    except Exception as ex:
        print(ex.__str__())


@receiver(post_save, sender=User)
def create_user(sender, instance: User, created: bool, **kwargs):
    if created:
        temp_pwd = uuid.uuid4().hex[:6]
        user = User.objects.filter(email=instance.email).first()
        if user is not None:
            user.set_password(temp_pwd)
            user.save()
        subject = "C360 - Account Creation"
        from_email = config["EMAIL_HOST_USER"]
        to_email = [instance.email]
        html_content = (
            "<p>Hi {0}, <br><br>Here's your password for Concertiv 360 platform <b><i>{1}</i></b><br><br>"
            "Regards,<br>Concertiv Admin Team</p>".format(instance.get_first_name(), temp_pwd)
        )
        email = EmailMessage(subject, html_content, from_email, to_email)
        email.content_subtype = "html"
        email.send(fail_silently=False)

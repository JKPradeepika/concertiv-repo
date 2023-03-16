import datetime
from typing import Dict, List, Optional, OrderedDict

from django.db.models import Model, QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.models.LicensePeriod import LicensePeriod


OBJECT_DOES_NOT_EXIST_ERROR_MESSAGE = _('Invalid pk "%(id)d" - object does not exist.')
OBJECT_DOES_NOT_EXIST_ERROR_CODE = "does_not_exist"

INVALID_LICENSE_PERIOD_START_DATE_ERROR_DETAIL = serializers.ErrorDetail(
    _("Start date must be one day after previous license period end date."),
    code=serializers.ValidationError.default_code,
)
INVALID_LICENSE_PERIOD_END_DATE_NEXT_START_ERROR_DETAIL = serializers.ErrorDetail(
    _("End date must be one day before next license period start date."),
    code=serializers.ValidationError.default_code,
)
INVALID_LICENSE_PERIOD_END_DATE_NOT_AFTER_START_ERROR_DETAIL = serializers.ErrorDetail(
    _("End date must be after license period start date."),
    code=serializers.ValidationError.default_code,
)


def get_nested_instance(model_class: Model, field_name: str, id: int, queryset: Optional[QuerySet] = None) -> Model:
    if queryset is None:
        queryset = model_class.objects.all()
    try:
        return queryset.get(id=id)
    except model_class.DoesNotExist as e:
        raise serializers.ValidationError(
            {field_name: OBJECT_DOES_NOT_EXIST_ERROR_MESSAGE % {"id": id}},
            code=OBJECT_DOES_NOT_EXIST_ERROR_CODE,
        ) from e


class ContiguousLicensePeriodDateValidator:
    """
    Validates that license period dates on a subscription remain contiguous (no overlaps or gaps);
    all next license periods start one day after previous end dates.
    As part of this validation, also ensures first license period has a start date.
    """

    requires_context = True

    def __init__(self, id_key: str):
        self.id_key = id_key

    def __call__(self, data: OrderedDict, szer: serializers.Serializer):
        if self.is_delete_subscription_request(data) or not data.get("licenses_periods"):
            return

        all_lp_dates = []
        if data.get(self.id_key):
            all_lp_dates.extend(self.get_stored_license_period_dates_list(data[self.id_key]))

        sorted_lp_dates = self.sort_requested_license_periods_by_date(data["licenses_periods"], all_lp_dates)
        self.validate_first_start_date_non_null(data, sorted_lp_dates, szer)
        self.validate_contiguous_dates(data, sorted_lp_dates)

    def is_delete_subscription_request(self, data: OrderedDict) -> bool:
        return data.get(self.id_key) and data.get("delete")

    def sort_requested_license_periods_by_date(
        self, license_periods_data: List[Dict], stored_lp_dates: List[Dict]
    ) -> List[Dict]:
        """
        Accepts:
            - licenses_periods list from request
            - array of stored lp dates

        Splices any existing lp dates with requested changes (additions, deletions, updates) for validation.
        Dicts are sorted by start_date; any null start dates are added to the end and sorted by end_date.

        If an existing lp date is updated in the request, updates that dict with the index of the dictionary
        in the request and the new start_date/end_date data.
        If an existing lp is deleted, updates that dict with a "skip" key set to True.

        Returns a list of dicts with keys:
            start_date      can be null if new lp
            end_date
            instance        null if new lp
            data            null if existing lp
            index           index of licenses_periods list in data; null if exists and not updated
            skip            null if not deleted
        """
        null_lp_dates = []
        all_lp_dates = []
        all_lp_dates.extend(stored_lp_dates)

        for i, request_lp in enumerate(license_periods_data):
            if not request_lp.get("licensePeriodId"):
                self.append_new_license_period_to_all_or_null_list(request_lp, i, all_lp_dates, null_lp_dates)
                continue
            self.update_existing_license_period_in_all_list(license_periods_data, request_lp, i, all_lp_dates)

        sorted_staged_license_periods = sorted(all_lp_dates, key=lambda x: x["start_date"])
        sorted_staged_license_periods.extend(sorted(null_lp_dates, key=lambda x: x["end_date"]))
        return sorted_staged_license_periods

    def update_existing_license_period_in_all_list(
        self, lp_data: List[OrderedDict], raw_lp_data: Dict, index: int, all_list: List[Dict]
    ) -> None:
        all_list_index = self.find_matching_index_of_all_license_period_dates(all_list, raw_lp_data["licensePeriodId"])
        if not all_list_index:
            field_errors = self._init_field_errors_dict({"licenses_periods": lp_data})
            field_errors["licensePeriods"][index]["licensePeriodId"] = [
                serializers.ErrorDetail(
                    string=OBJECT_DOES_NOT_EXIST_ERROR_MESSAGE % {"id": raw_lp_data["licensePeriodId"]},
                    code=OBJECT_DOES_NOT_EXIST_ERROR_CODE,
                )
            ]
        if "start_date" in raw_lp_data:
            all_list[all_list_index]["start_date"] = raw_lp_data["start_date"]
        if "end_date" in raw_lp_data:
            all_list[all_list_index]["end_date"] = raw_lp_data["end_date"]
        if raw_lp_data.get("delete"):
            all_list[all_list_index]["skip"] = True
        all_list[all_list_index]["index"] = index

    def append_new_license_period_to_all_or_null_list(
        self, raw_lp_data: Dict, index: int, all_list: List[Dict], null_list: List[Dict]
    ) -> None:
        staged_dict = {
            "start_date": raw_lp_data.get("start_date"),
            "end_date": raw_lp_data.get("end_date"),
            "data": raw_lp_data,
            "index": index,
        }
        if not raw_lp_data.get("start_date"):
            null_list.append(staged_dict)
        else:
            all_list.append(staged_dict)

    def get_stored_license_period_dates_list(self, subscription_id: int) -> List[Dict]:
        return self.get_stored_license_period_dates_list_from_queryset(
            self.query_existing_license_periods(subscription_id)
        )

    def query_existing_license_periods(self, subscription_id: int) -> QuerySet:
        return LicensePeriod.objects.filter(subscription_id=subscription_id).order_by("start_date")

    def get_stored_license_period_dates_list_from_queryset(self, queryset: QuerySet[LicensePeriod]) -> List[Dict]:
        return [{"start_date": x.start_date, "end_date": x.end_date, "instance": x} for x in queryset]

    @staticmethod
    def find_matching_index_of_all_license_period_dates(
        all_license_period_dates: List[Dict], license_period_id: int
    ) -> Optional[int]:
        for i in range(len(all_license_period_dates)):
            if (
                "instance" in all_license_period_dates[i]
                and all_license_period_dates[i]["instance"].id == license_period_id
            ):
                return i

    def validate_contiguous_dates(self, data: OrderedDict, sorted_lps: List[Dict]) -> None:
        """
        If a start_date is null, sets it to the day after the previous end date.
        Otherwise, if it is set, raises ValidationError.
        Skips validating the first in the list and any deleted license periods.
        """
        field_errors = {}

        last_lp_dict = None
        for lp_dict in sorted_lps:
            if lp_dict.get("skip"):
                continue

            if last_lp_dict:
                field_errors = self.validate_contiguous_license_period(data, field_errors, lp_dict, last_lp_dict)

            field_errors = self.validate_end_date_after_start_date(data, field_errors, lp_dict)
            last_lp_dict = lp_dict

        if field_errors:
            raise serializers.ValidationError(field_errors)

    def validate_end_date_after_start_date(self, data: OrderedDict, field_errors: Dict, lp_dict: Dict) -> Dict:
        if lp_dict["start_date"] >= lp_dict["end_date"] and "index" in lp_dict:
            if not field_errors:
                field_errors = self._init_field_errors_dict(data)
            self.set_field_errors_for_license_period(
                field_errors,
                lp_dict["index"],
                "endDate",
                INVALID_LICENSE_PERIOD_END_DATE_NOT_AFTER_START_ERROR_DETAIL,
            )
        return field_errors

    def validate_contiguous_license_period(
        self, data: OrderedDict, field_errors: Dict, lp_dict: Dict, last_lp_dict: Dict
    ) -> Dict:
        valid_date = last_lp_dict["end_date"] + datetime.timedelta(days=1)

        if lp_dict.get("start_date") is None or lp_dict["start_date"] == valid_date:
            lp_dict["start_date"] = valid_date
            data["licenses_periods"][lp_dict["index"]]["start_date"] = valid_date
            return field_errors

        field_errors = self.set_field_errors_for_noncontiguous_license_period(data, field_errors, lp_dict, last_lp_dict)
        return field_errors

    def set_field_errors_for_noncontiguous_license_period(
        self, data: OrderedDict, field_errors: Dict, lp_dict: Dict, last_lp_dict: Dict
    ) -> Dict:
        if not field_errors:
            field_errors = self._init_field_errors_dict(data)
        if "index" in lp_dict:
            self.set_field_errors_for_license_period(
                field_errors, lp_dict["index"], "startDate", INVALID_LICENSE_PERIOD_START_DATE_ERROR_DETAIL
            )
        elif "index" in last_lp_dict:
            self.set_field_errors_for_license_period(
                field_errors, lp_dict["index"], "endDate", INVALID_LICENSE_PERIOD_END_DATE_NEXT_START_ERROR_DETAIL
            )
        return field_errors

    def set_field_errors_for_license_period(
        self, field_errors: Dict, index: int, key: str, error_detail=serializers.ErrorDetail
    ) -> None:
        field_errors["licensePeriods"][index] = {key: [error_detail]}

    @staticmethod
    def _init_field_errors_dict(data: OrderedDict) -> Dict:
        return {"licensePeriods": [{} for _ in range(len(data.get("licenses_periods", [])))]}

    def validate_first_start_date_non_null(
        self, data: OrderedDict, sorted_lps: List[Dict], szer: serializers.Serializer
    ) -> None:
        if not sorted_lps[0].get("start_date"):
            field_errors = self._init_field_errors_dict(data)
            field_errors["licensePeriods"][0]["startDate"] = [
                serializers.ErrorDetail(
                    string=szer.error_messages["required"],
                    code="required",
                )
            ]
            raise serializers.ValidationError(field_errors)

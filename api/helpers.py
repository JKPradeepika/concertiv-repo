"""
    Helpers functions
"""
import datetime
from datetime import date
from typing import Any, Callable, TypeVar, Optional

from djmoney.money import Money
from rest_framework import serializers
from django.db.models import Aggregate, CharField, Value
from rest_framework.renderers import JSONRenderer as RFJSONRenderer
from rest_framework.utils.encoders import JSONEncoder as RFJSONEncoder

F = TypeVar("F", bound=Callable[..., Any])


class JSONEncoder(RFJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Money):
            return str(obj)
        return super().default(obj)


class JSONRenderer(RFJSONRenderer):
    encoder_class = JSONEncoder


def transform_camelcase_to_snakecase(key: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in key]).lstrip("_")


def convert_str_to_date(date_string: str) -> Optional[date]:
    """
    Function to convert str to date
    :param date_string: 2022-01-20
    :return: date
    """
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    except Exception as ex:
        print(ex.__str__())
        return None


# Base class to map Constants
class ConstantEntity:
    def __init__(self, obj):
        self.id = obj[0]
        self.name = obj[1]

    def to_dict(self):
        return self.__dict__


class GroupConcat(Aggregate):
    """can be used to return a stringified representation
    of a Django entity's list of children"""

    function = "GROUP_CONCAT"
    template = "%(function)s(%(expressions)s)"

    def __init__(self, expression, delimiter=", ", distinct=False, **extra):
        output_field = extra.pop("output_field", CharField())
        delimiter = Value(delimiter)
        self.template = "%(function)s(DISTINCT %(expressions)s)" if distinct else "%(function)s(%(expressions)s)"
        super(GroupConcat, self).__init__(expression, delimiter, output_field=output_field, **extra)

    def as_postgresql(self, compiler, connection):
        self.function = "STRING_AGG"
        return super(GroupConcat, self).as_sql(compiler, connection)


# Custom class to represent constants choices in serializers
class ConstantChoiceField(serializers.ChoiceField):
    """
    Custom class that extends from ChoiceField serializer for constants (overwrite to_representation method)
    """

    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj

        return {
            "id": obj,
            "name": self._choices[obj],
        }

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == "" and self.allow_blank:
            return ""

        for key, val in self._choices.items():
            if key == data:
                return key
        self.fail("invalid_choice", input=data)


# helper function to derive bucket subdirs based on fk fields
def derive_subdir_path_based_on_fk_fields(instance, filename):
    # Supplier
    if instance.supplier:
        return f"suppliers/{filename}"
    elif instance.product:
        return f"products/{filename}"
    elif instance.contract:
        return f"contracts/{filename}"
    elif instance.buyer:
        return f"buyers/{filename}"
    else:
        return f"documents/{filename}"

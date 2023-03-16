from enum import Enum
from shlex import split as quote_sensitive_split
from typing import Any, Optional, Union

from django.core.paginator import InvalidPage
from django.db.models import Q, QuerySet
from django.http.request import QueryDict
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.pagination import PageNumberPagination

PAGE_SIZE_ALL = "all"


class PageSetPagination(PageNumberPagination):
    page_size = PAGE_SIZE_ALL
    page_size_query_param = "pageSize"
    max_page_size = 100

    def paginate_queryset(self, queryset: QuerySet, request: Request, view=None):
        """
        Paginate a queryset by returning a page object.
        If page_size provided is None, return a single page with all results.
        """
        page_size = self.get_page_size(request)
        if page_size and page_size != PAGE_SIZE_ALL:
            return super().paginate_queryset(queryset, request, view)

        page_size = queryset.count() or self.max_page_size
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(page_number=page_number, message=str(exc))
            raise NotFound(msg)

        self.request = request
        return list(self.page)


class FilterOperator(Enum):
    CONTAINS = 1
    EQUALS = 2
    STARTS_WITH = 3
    ENDS_WITH = 4
    IS_EMPTY = 5
    IS_NOT_EMPTY = 6


class ExpectedFilterOperators:
    EXPECTED_FILTER_OPERATORS = {
        "contains": FilterOperator.CONTAINS,
        "equals": FilterOperator.EQUALS,
        "startswith": FilterOperator.STARTS_WITH,
        "endswith": FilterOperator.ENDS_WITH,
        "isempty": FilterOperator.IS_EMPTY,
        "isnotempty": FilterOperator.IS_NOT_EMPTY,
    }


class FilterOperatorManager:
    @staticmethod
    def create_query(column_name: str, column_operator: FilterOperator, column_content: str) -> Q:
        _operator: str
        _column_content: Union[str, bool] = column_content

        if column_operator == FilterOperator.CONTAINS:
            _operator = "__icontains"
        elif column_operator == FilterOperator.EQUALS:
            _operator = "__iexact"
        elif column_operator == FilterOperator.STARTS_WITH:
            _operator = "__istartswith"
        elif column_operator == FilterOperator.ENDS_WITH:
            _operator = "__iendswith"
        elif column_operator == FilterOperator.IS_EMPTY:
            _operator = "__isnull"
            _column_content = True
        elif column_operator == FilterOperator.IS_NOT_EMPTY:
            _operator = "__isnull"
            _column_content = False

        return Q(**{f"{column_name}{_operator}": _column_content})

    @staticmethod
    def convert_input_column_operator(column_operator: str) -> FilterOperator:
        return_operator = ExpectedFilterOperators.EXPECTED_FILTER_OPERATORS.get(column_operator.lower())
        if not return_operator:
            raise ValueError("The provided filtering operator was not found")
        return return_operator


def sort_queryset(
    initial_queryset: QuerySet[Any],
    column_name_mappings: dict[str, str],
    sort_content: Optional[str] = None,
) -> QuerySet[Any]:
    queryset = initial_queryset
    if sort_content:
        order_by_string = ""
        [sort_column, sort_type] = sort_content.split(" ")
        if sort_type.upper() == "DESC":
            order_by_string = "-"
        order_by_string += column_name_mappings[sort_column.lower()]
        queryset = queryset.order_by(order_by_string)
    else:
        queryset = queryset.order_by("id")

    return queryset


def filter_queryset(
    initial_queryset: QuerySet[Any],
    column_name_mappings: dict[str, str],
    filter_content: Optional[str] = None,
    filter_operator: Optional[str] = None,
) -> QuerySet[Any]:
    queryset = initial_queryset
    column_content = ""
    if filter_content and filter_operator:
        filter_tokens = quote_sensitive_split(filter_content)
        frontend_column_name = filter_tokens[0]
        column_operator = filter_tokens[1]
        casted_column_operator = FilterOperatorManager.convert_input_column_operator(column_operator)
        if (casted_column_operator != FilterOperator.IS_EMPTY) and (
            casted_column_operator != FilterOperator.IS_NOT_EMPTY
        ):
            column_content = filter_tokens[2]
        filter_query = FilterOperatorManager.create_query(
            column_operator=casted_column_operator,
            column_name=column_name_mappings[frontend_column_name.lower()],
            column_content=column_content,
        )
        queryset = queryset.filter(filter_query)
    return queryset


def sort_and_filter_queryset(
    initial_queryset: QuerySet[Any], column_name_mappings: dict[str, str], query_params: QueryDict
) -> QuerySet[Any]:
    filter_content = query_params.get("filterContent")
    filter_operator = query_params.get("filterOperator")
    sort_content = query_params.get("sortContent")
    queryset = filter_queryset(initial_queryset, column_name_mappings, filter_content, filter_operator)
    queryset = sort_queryset(queryset, column_name_mappings, sort_content)
    return queryset

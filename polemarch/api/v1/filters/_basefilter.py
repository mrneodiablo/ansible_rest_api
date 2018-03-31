# -*- coding: utf-8 -*-
from rest_framework import filters as rest_filter
from django_filters import CharFilter


def _extra_search(queryset, field, value, stype):
    vals = field.split("__")
    field, tp = vals[0], (list(vals)[1:2] + [""])[0]
    field += "__{}".format(stype)
    value = value.split(",") if stype == "in" else value
    if tp.upper() == "NOT":
        return queryset.exclude(**{field: value})
    return queryset.filter(**{field: value})


def extra_filter(queryset, field, value):
    return _extra_search(queryset, field, value, "in")


def name_filter(queryset, field, value):
    return _extra_search(queryset, field, value, "contains")


def variables_filter(queryset, field, value):
    # filter applicable only to variables
    # pylint: disable=unused-argument
    items = value.split(",")
    kwargs = {item.split(":")[0]: item.split(":")[1] for item in items}
    return queryset.var_filter(**kwargs)



class _BaseFilter(rest_filter.FilterSet):
    id = CharFilter(method=extra_filter)
    id__not = CharFilter(method=extra_filter)
    name__not = CharFilter(method=name_filter)
    name = CharFilter(method=name_filter)


class _BaseHGIFilter(_BaseFilter):
    variables = CharFilter(method=variables_filter)

# -*- coding: utf-8 -*-
from django_filters import IsoDateTimeFilter
from polemarch.main import models
from _basefilter import _BaseFilter
from django_filters import NumberFilter
from rest_framework import filters as rest_filters

class HistoryFilter(_BaseFilter):
    start_time__gt = IsoDateTimeFilter(name="start_time",
                                       lookup_expr=('gt'))
    stop_time__gt = IsoDateTimeFilter(name="stop_time",
                                      lookup_expr=('gt'))
    start_time__lt = IsoDateTimeFilter(name="start_time",
                                       lookup_expr=('lt'))
    stop_time__lt = IsoDateTimeFilter(name="stop_time",
                                      lookup_expr=('lt'))
    start_time__gte = IsoDateTimeFilter(name="start_time",
                                        lookup_expr=('gte'))
    stop_time__gte = IsoDateTimeFilter(name="stop_time",
                                       lookup_expr=('gte'))
    start_time__lte = IsoDateTimeFilter(name="start_time",
                                        lookup_expr=('lte'))
    stop_time__lte = IsoDateTimeFilter(name="stop_time",
                                       lookup_expr=('lte'))

    class Meta:
        model = models.History
        fields = ('id',
                  'mode',
                  'kind',
                  'project',
                  'status',
                  'inventory',
                  'start_time',
                  'stop_time',
                  'initiator',
                  'initiator_type')


class HistoryLinesFilter(rest_filters.FilterSet):
    after = NumberFilter(name="line_number", lookup_expr=('gt'))
    before = NumberFilter(name="line_number", lookup_expr=('lt'))

    class Meta:
        model = models.HistoryLines
        fields = (
            'line_number',
        )

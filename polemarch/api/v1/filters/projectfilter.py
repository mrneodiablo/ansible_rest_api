# -*- coding: utf-8 -*-

from _basefilter import _BaseHGIFilter, extra_filter
from polemarch.main import models
from django_filters import CharFilter


class ProjectFilter(_BaseHGIFilter):
    status = CharFilter(method=extra_filter)
    status__not = CharFilter(method=extra_filter)

    class Meta:
        model = models.Project
        fields = ('id',
                  'name',
                  'status',)

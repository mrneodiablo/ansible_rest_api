# -*- coding: utf-8 -*-
from django_filters import CharFilter
from _basefilter import _BaseFilter, name_filter
from polemarch.main import models

class TaskFilter(_BaseFilter):
    playbook__not = CharFilter(method=name_filter)
    playbook = CharFilter(method=name_filter)

    class Meta:
        model = models.Task
        fields = ('id',
                  'name',
                  'playbook',
                  'project')

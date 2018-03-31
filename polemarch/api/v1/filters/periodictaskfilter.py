# -*- coding: utf-8 -*-
from polemarch.main import models
from _basefilter import _BaseFilter


class PeriodicTaskFilter(_BaseFilter):
    class Meta:
        model = models.PeriodicTask
        fields = ('id',
                  'mode',
                  'kind',
                  'type',
                  'project')




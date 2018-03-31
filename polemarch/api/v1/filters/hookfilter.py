# -*- coding: utf-8 -*-
from _basefilter import _BaseFilter
from polemarch.main import models


class HookFilter(_BaseFilter):
    class Meta:
        model = models.Hook
        fields = (
            'id',
            'name',
            'type',
        )
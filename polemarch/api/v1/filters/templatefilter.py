# -*- coding: utf-8 -*-
from _basefilter import _BaseFilter
from polemarch.main import models


class TemplateFilter(_BaseFilter):
    class Meta:
        model = models.Template
        fields = (
            'id',
            'name',
            'kind',
            'project',
            'inventory'
        )


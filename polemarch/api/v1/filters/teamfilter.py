# -*- coding: utf-8 -*-
from polemarch.main import models
from _basefilter import _BaseFilter

class TeamFilter(_BaseFilter):
    class Meta:
        model = models.UserGroup
        fields = (
            'id',
            "name"
        )

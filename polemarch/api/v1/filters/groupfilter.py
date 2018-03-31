# -*- coding: utf-8 -*-
from polemarch.main import models
from _basefilter import _BaseHGIFilter

class GroupFilter(_BaseHGIFilter):
    class Meta:
        model = models.Group
        fields = ('id',
                  'name',)


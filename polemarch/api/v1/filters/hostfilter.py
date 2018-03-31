# -*- coding: utf-8 -*-
from polemarch.main import models
from _basefilter import _BaseHGIFilter



class HostFilter(_BaseHGIFilter):
    class Meta:
        model = models.Host
        fields = ('id',
                  'name',
                  'type')
# -*- coding: utf-8 -*-
from _basefilter import _BaseHGIFilter
from polemarch.main import models

class InventoryFilter(_BaseHGIFilter):
    class Meta:
        model = models.Inventory
        fields = ('id',
                  'name',)

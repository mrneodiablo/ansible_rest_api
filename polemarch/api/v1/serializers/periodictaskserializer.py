# -*- coding: utf-8 -*-
from django.db import transaction

from  _bashserializer import ( _WithVariablesSerializer,
                               DictField)
from rest_framework import serializers
from ....main import models
from ....main import exceptions as main_exceptions

# respone class for re format overwrite django-rest
from ...base import Response as APIRespone



class PeriodictaskSerializer(_WithVariablesSerializer):
    vars = DictField(required=False, write_only=True)
    schedule = serializers.CharField(allow_blank=True)
    inventory = serializers.CharField()

    class Meta:
        model = models.PeriodicTask
        fields = ('id',
                  'name',
                  'type',
                  'schedule',
                  'mode',
                  'kind',
                  'project',
                  'inventory',
                  'save_result',
                  'enabled',
                  'vars',
                  'url',)

    @transaction.atomic
    def permissions(self, request):  # noce
        raise main_exceptions.NotApplicable("See project permissions.")

    def owner(self, request):  # noce
        raise main_exceptions.NotApplicable("See project owner.")


class OnePeriodictaskSerializer(PeriodictaskSerializer):
    vars = DictField(required=False)

    class Meta:
        model = models.PeriodicTask
        fields = ('id',
                  'name',
                  'type',
                  'schedule',
                  'mode',
                  'kind',
                  'project',
                  'inventory',
                  'save_result',
                  'enabled',
                  'vars',
                  'url',)

    def execute(self):
        inventory = self.instance.inventory
        history_id = self.instance.execute(sync=False)
        rdata = dict(detail="Started at inventory {}.".format(inventory),
                     history_id=history_id)
        return APIRespone(rdata, 201)
# -*- coding: utf-8 -*-
from _bashserializer import _SignalSerializer
from ....main import models

class VariableSerializer(_SignalSerializer):
    class Meta:
        model = models.Variable
        fields = ('key',
                  'value',)

    def to_representation(self, instance):
        # we are not using that. This function here just in case.
        return {instance.key: instance.value}  # nocv

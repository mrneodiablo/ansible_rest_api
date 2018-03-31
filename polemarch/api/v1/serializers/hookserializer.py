# -*- coding: utf-8 -*-
from rest_framework import serializers
from ....main import models


class HookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hook
        fields = (
            'id',
            'name',
            'type',
            'when',
            'recipients'
        )
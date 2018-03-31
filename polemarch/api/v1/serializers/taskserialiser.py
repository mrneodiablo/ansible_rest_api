# -*- coding: utf-8 -*-
from rest_framework import serializers
from _bashserializer import _WithVariablesSerializer, ModelRelatedField
from ....main import models

class TaskSerializer(_WithVariablesSerializer):
    class Meta:
        model = models.Task
        fields = ('id',
                  'name',
                  'playbook',
                  'project',
                  'url',)

    def to_representation(self, instance):
        return super(TaskSerializer, self).to_representation(
            instance, hidden_vars=[]
        )


class OneTaskSerializer(TaskSerializer):
    project = ModelRelatedField(read_only=True)
    playbook = serializers.CharField(read_only=True)

    class Meta:
        model = models.Task
        fields = ('id',
                  'name',
                  'playbook',
                  'project',
                  'url',)
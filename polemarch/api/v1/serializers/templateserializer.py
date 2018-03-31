# -*- coding: utf-8 -*-
from collections import OrderedDict

from _bashserializer import _WithVariablesSerializer, DictField
from polemarch.main import models
from userserializer import UserSerializer
from projectserializer import OneProjectSerializer

class TemplateSerializer(_WithVariablesSerializer):
    data = DictField(required=True, write_only=True)
    options = DictField(write_only=True)
    options_list = DictField(read_only=True)

    class Meta:
        model = models.Template
        fields = (
            'id',
            'name',
            'kind',
            'data',
            'options',
            'options_list',
        )

    def get_vars(self, representation):
        try:
            return representation['data']['vars']
        except KeyError:
            return None

    def set_opts_vars(self, rep, hidden_vars):
        if not rep.get('vars', None):
            return rep
        var = rep['vars']
        for mask_key in hidden_vars:
            if mask_key in var.keys():
                var[mask_key] = "[~~ENCRYPTED~~]"
        return rep

    def repr_options(self, instance, data, hidden_vars):
        hv = hidden_vars
        hv = instance.HIDDEN_VARS if hv is None else hv
        for name, rep in data.get('options', {}).items():
            data['options'][name] = self.set_opts_vars(rep, hv)

    def to_representation(self, instance):
        data = OrderedDict()
        if instance.kind in ["Task", "PeriodicTask", "Module"]:
            hidden_vars = models.PeriodicTask.HIDDEN_VARS
            data = super(TemplateSerializer, self).to_representation(
                instance, hidden_vars=hidden_vars
            )
            self.repr_options(instance, data, hidden_vars)
        elif instance.kind in ["Host", "Group"]:
            data = super(TemplateSerializer, self).to_representation(
                instance, hidden_vars=models.Inventory.HIDDEN_VARS
            )
        return data


class OneTemplateSerializer(TemplateSerializer):
    data = DictField(required=True)
    owner = UserSerializer(read_only=True)
    options = DictField(required=False)
    options_list = DictField(read_only=True)

    class Meta:
        model = models.Template
        fields = (
            'id',
            'name',
            'kind',
            'owner',
            'data',
            'options',
            'options_list',
        )

    def execute(self, request):
        serializer = OneProjectSerializer(self.instance.project)
        return self.instance.execute(
            serializer, request.user, request.data.get('option', None)
        )
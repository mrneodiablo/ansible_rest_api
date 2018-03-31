# -*- coding: utf-8 -*-
from _bashserializer import _WithVariablesSerializer, _InventoryOperations, DictField
from hostserializer import HostSerializer
from groupserializer import GroupSerializer
from userserializer import UserSerializer
from ....main import models


class InventorySerializer(_WithVariablesSerializer):
    vars = DictField(required=False, write_only=True)

    class Meta:
        model = models.Inventory
        fields = ('id',
                  'name',
                  'vars',
                  'url',)


class OneInventorySerializer(InventorySerializer, _InventoryOperations):
    vars = DictField(required=False)
    all_hosts = HostSerializer(read_only=True, many=True)
    hosts = HostSerializer(read_only=True, many=True, source="hosts_list")
    groups = GroupSerializer(read_only=True, many=True, source="groups_list")
    owner = UserSerializer(read_only=True)

    class Meta:
        model = models.Inventory
        fields = ('id',
                  'name',
                  'hosts',
                  'all_hosts',
                  "groups",
                  'vars',
                  'owner',
                  'url',)
# -*- coding: utf-8 -*-
from _bashserializer import (   _WithVariablesSerializer,
                                DictField,
                                _InventoryOperations )

from hostserializer import HostSerializer
from userserializer import UserSerializer
from polemarch.main import models

from rest_framework import exceptions as rest_exceptions

class GroupSerializer(_WithVariablesSerializer):
    vars = DictField(required=False, write_only=True)

    class Meta:
        model = models.Group
        fields = ('id',
                  'name',
                  'vars',
                  'children',
                  'url',)


class OneGroupSerializer(GroupSerializer, _InventoryOperations):
    vars = DictField(required=False)
    hosts = HostSerializer(read_only=True, many=True)
    groups = GroupSerializer(read_only=True, many=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = models.Group
        fields = ('id',
                  'name',
                  'hosts',
                  "groups",
                  'vars',
                  'children',
                  'owner',
                  'url',)

    class ValidationException(rest_exceptions.ValidationError):
        status_code = 409

    def hosts_operations(self, method, data):
        if self.instance.children:
            raise self.ValidationException("Group is children.")
        return super(OneGroupSerializer, self).hosts_operations(method, data)

    def groups_operations(self, method, data):
        if not self.instance.children:
            raise self.ValidationException("Group is not children.")
        return super(OneGroupSerializer, self).groups_operations(method, data)
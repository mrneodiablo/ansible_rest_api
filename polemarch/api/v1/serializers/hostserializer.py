# -*- coding: utf-8 -*-
from _bashserializer import _WithVariablesSerializer,DictField
from userserializer import UserSerializer
from ....main import models

class HostSerializer(_WithVariablesSerializer):
    vars = DictField(required=False, write_only=True)

    class Meta:
        model = models.Host
        fields = ('id',
                  'name',
                  'type',
                  'vars',
                  'url',)


class OneHostSerializer(HostSerializer):
    owner = UserSerializer(read_only=True)
    vars = DictField(required=False)

    class Meta:
        model = models.Host
        fields = ('id',
                  'name',
                  'type',
                  'vars',
                  'owner',
                  'url',)
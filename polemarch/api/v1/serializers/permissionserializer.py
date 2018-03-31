# -*- coding: utf-8 -*-
from _bashserializer import _SignalSerializer
from rest_framework import serializers as rest_serializers
from polemarch.main import models

class PermissionsSerializer(_SignalSerializer):
    member = rest_serializers.IntegerField()
    member_type = rest_serializers.CharField()

    class Meta:
        model = models.ACLPermission
        fields = ("member",
                  "role",
                  "member_type")


# -*- coding: utf-8 -*-
from _bashserializer import _WithPermissionsSerializer, DictField
from polemarch.main import models

class TeamSerializer(_WithPermissionsSerializer):

    users_list = DictField(required=False, write_only=True)

    class Meta:
        model = models.UserGroup
        fields = (
            'id',
            "name",
            "users_list",
            'url',
        )


try:
    from userserializer import UserSerializer
except:
    UserSerializer = None

class OneTeamSerializer(TeamSerializer):
    users = UserSerializer(many=True, required=False)
    users_list = DictField(required=False)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = models.UserGroup
        fields = (
            'id',
            "name",
            "users",
            "users_list",
            "owner",
            'url',
        )
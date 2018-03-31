# -*- coding: utf-8 -*-
from _bashserializer import _SignalSerializer
from userserializer import UserSerializer
from inventoryserializer import InventorySerializer
from projectserializer import ProjectSerializer
from ....main import models

# serializer cho scripts model
# dongvt add new feature for tool
class ScriptSerializer(_SignalSerializer):
    inventory = InventorySerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = models.Script
        fields = ("id",
                  "name",
                  "lang",
                  "script",
                  "options",
                  "description",
                  "date_created",
                  "date_modified",
                  "owner",
                  "inventory",
                  "project"
                  )


# serializer cho 1 script model
class OneScriptSerializer(ScriptSerializer):
    class Meta:
        model = models.Script
        fields = ("id",
                  "name",
                  "lang",
                  "script",
                  "options",
                  "description",
                  "date_created",
                  "date_modified",
                  "owner",
                  "inventory",
                  "project"
                  )
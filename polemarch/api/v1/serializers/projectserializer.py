# -*- coding: utf-8 -*-
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from _bashserializer import _InventoryOperations, DictField
from hostserializer import HostSerializer
from groupserializer import GroupSerializer
from polemarch.api.base import Response as APIResponse
from userserializer import UserSerializer
from inventoryserializer import InventorySerializer
from ....main import models
from ....main import exceptions as main_exceptions
from ....main.models import Inventory, Script


class ProjectSerializer(_InventoryOperations):
    status = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    vars = DictField(required=False, write_only=True)

    class Meta:
        model = models.Project
        fields = ('id',
                  'name',
                  'status',
                  'type',
                  'vars',
                  'url',)

    @transaction.atomic
    def _do_with_vars(self, *args, **kw):
        instance = super(ProjectSerializer, self)._do_with_vars(*args, **kw)
        return instance if instance.repo_class else None


class OneProjectSerializer(ProjectSerializer, _InventoryOperations):
    vars = DictField(required=False)
    hosts = HostSerializer(read_only=True, many=True)
    groups = GroupSerializer(read_only=True, many=True)
    inventories = InventorySerializer(read_only=True, many=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = models.Project
        fields = ('id',
                  'name',
                  'status',
                  'repository',
                  'hosts',
                  "groups",
                  'inventories',
                  'vars',
                  'owner',
                  'revision',
                  'branch',
                  'url',)

    def inventories_operations(self, method, data):
        return self.get_operation(method, data, attr="inventories")

    @transaction.atomic()
    def sync(self):
        self.instance.start_repo_task("sync")
        data = dict(detail="Sync with {}.".format(self.instance.repository))
        return APIResponse(data, 200)

    def _execution(self, kind, data, user):
        """

        :param kind: playbook/module/script 
        :param data: là data POST lên {"playbook":"testing.yml","script_remote_path":"/tmp/ping.sh","lang":"bash","limit":"pj-blog2","inventory":"2"}
        :param user: là object user, chạy theo permission
        :return: 
        """
        inventory = data.pop("inventory")
        try:
            # get object inventory from model
            inventory = Inventory.objects.get(id=int(inventory))
            if not inventory.viewable_by(user):  # nocv
                raise PermissionDenied(
                    "You don't have permission to inventory."
                )
        except ValueError:
            pass

        # goi exec function cua model
        # kind: playbook/module/script
        # str(data.pop(kind))=*args: lấy giá trị trong data kind xóa giá trị đó trong data "playbook":"testing.yml"
        history_id = self.instance.execute(
            kind, str(data.pop(kind)), inventory,
            initiator=user.id, **data
        )
        rdata = dict(detail="Started at inventory {}.".format(inventory),
                     history_id=history_id)
        return APIResponse(rdata, 201)

    def execute_playbook(self, request):
        return self._execution("playbook", dict(request.data), request.user)

    def execute_module(self, request):
        return self._execution("module", dict(request.data), request.user)


    #################################### AUTH: DONGVT #######################################
    # serialize chạy ansible python client api

    def _execution_api(self, kind, user, data):
        """

        :param kind: playbook/module/script
        :param user: là object user, chạy theo permission
        :param data: là data POST lên {"list-hosts":"","inventory":"1","module":"shell","group":"groupapi","args":"ifconfig"}
        :return: 
        """

        # lấy inventory từ request post lên
        inventory = data.pop("inventory")

        try:
            # get object inventory from model
            inventory = Inventory.objects.get(id=int(inventory))
            # check permisioon
            if not inventory.viewable_by(user):  # nocv
                raise PermissionDenied(
                    "You don't have permission to inventory."
                )

        except ValueError:
            pass

        extra = {
            "data": data,
            "inventory": inventory,
            "sync": False,
            "user": user
        }
        #goi exec function cua model
        #kind: playbook/module/script
        #str(data.pop(kind))=*args: lấy giá trị trong data kind xóa giá trị đó trong data "playbook":"testing.yml"

        history_id = self.instance.execute_api( kind=kind, **extra)
        rdata = dict(detail="Started at inventory {}.".format(inventory),
                     history_id=history_id)

        return APIResponse(rdata, 201)


    # chạy private function
    def execute_module_api(self, request):
        return self._execution_api("moduleapi", request.user, dict(request.data))


    def execute_script(self, request):
        """
        data request post len phai theo format
        :param request.data: {"id":"<id script>","script_remote_path": "/tmp/ping.sh","limit":"pj-blog2","inventory":"2"}
         xủ lý lấy thông tin để tạo request.data 

        output xủ lý  
        {   "extra-vars":"name=testing  script=/mto_automation/polemarch/projects/1/ping.sh  script_remote_path=/tmp/ping.sh  lang=bash","limit":"pj-blog2","playbook":"init.yml","inventory":"2"}
        :return: về phương thức  private _execution
        """
        data = {}

        try:
            script_id = dict(request.data)["id"]

            # get object script from model
            scriptobj = Script.objects.get(id=int(script_id))
        except:
            raise main_exceptions.PMException("{id} not in correct")

        data["extra-vars"] = "name=" + scriptobj.name + " script=" + scriptobj.script + " script_remote_path=" + dict(request.data)["script_remote_path"] + \
                             " lang=" + scriptobj.lang

        data["limit"] = request.data["limit"]
        data["inventory"] = request.data["inventory"]
        data["playbook"] = "init.yml"

        # tra ve phuong thuc private execut kind, data, user
        return self._execution("playbook", dict(data), request.user)
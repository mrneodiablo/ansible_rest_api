# pylint: disable=no-member,unused-argument
# -*- coding: utf-8 -*-
# author: dongvt

import json

import six
from django import dispatch
from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import serializers
from rest_framework import exceptions
from rest_framework.exceptions import PermissionDenied
from ....main import models
from ...base import Response as APIResponse


# NOTE: we can freely remove that because according to real behaviour all our
#  models always have queryset at this stage, so this code actually doing
# nothing
#
# Serializers field for usability
class ModelRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        model = kwargs.pop("model", None)
        assert not ((model is not None or self.queryset is not None) and
                    kwargs.get('read_only', None)), (
            'Relational fields should not provide a `queryset` or `model`'
            ' argument, when setting read_only=`True`.'
        )
        if model is not None:
            kwargs["queryset"] = model.objects.all()
        super(ModelRelatedField, self).__init__(**kwargs)

class DictField(serializers.CharField):
    def to_internal_value(self, data):
        return (
            data
            if (
                isinstance(data, (six.string_types, six.text_type)) or
                isinstance(data, (dict, list))
            )
            else self.fail("Unknown type.")
        )

    def to_representation(self, value):
        return (
            json.loads(value)
            if not isinstance(value, (dict, list))
            else value
        )


api_pre_save = dispatch.Signal(providing_args=["instance", "user"])
api_post_save = dispatch.Signal(providing_args=["instance", "user"])


def with_signals(func):
    '''
    Decorator for send api_pre_save and api_post_save signals from serializers.
    '''
    def func_wrapper(*args, **kwargs):
        user = args[0].context['request'].user
        with transaction.atomic():
            instance = func(*args, **kwargs)
            api_pre_save.send(
                sender=instance.__class__, instance=instance, user=user
            )
        with transaction.atomic():
            api_post_save.send(
                sender=instance.__class__, instance=instance, user=user
            )
        return instance

    return func_wrapper


# Serializers
class _SignalSerializer(serializers.ModelSerializer):
    @with_signals
    def create(self, validated_data):
        return super(_SignalSerializer, self).create(validated_data)

    @with_signals
    def update(self, instance, validated_data):
        return super(_SignalSerializer, self).update(instance, validated_data)


class _WithPermissionsSerializer(_SignalSerializer):
    perms_msg = "You do not have permission to perform this action."

    def _get_objects(self, model, objs_id):
        user = self.context['request'].user
        qs = model.objects.all().user_filter(user)
        return list(qs.filter(id__in=objs_id))

    def create(self, validated_data):
        validated_data["owner"] = self.current_user()
        return super(_WithPermissionsSerializer, self).create(validated_data)

    def current_user(self):
        return self.context['request'].user

    def __get_all_permission_serializer(self):  # noce
        return PermissionsSerializer(
            self.instance.acl.all(), many=True
        )

    def __duplicates_check(self, data):
        without_role = [
            frozenset({e['member'], e['member_type']}) for e in data
        ]
        if len(without_role) != len(list(set(without_role))):
            raise ValueError("There is duplicates in your permissions set.")

    def __permission_set(self, data, remove_old=True):  # noce
        self.__duplicates_check(data)
        for permission_args in data:
            if remove_old:
                self.instance.acl.extend().filter(
                    member=permission_args['member'],
                    member_type=permission_args['member_type']
                ).delete()
            self.instance.acl.create(**permission_args)

    @transaction.atomic
    def permissions(self, request):  # noce
        user = self.current_user()
        if request.method != "GET" and not self.instance.manageable_by(user):
            raise PermissionDenied(self.perms_msg)
        if request.method == "DELETE":
            self.instance.acl.filter_by_data(request.data).delete()
        elif request.method == "POST":
            self.__permission_set(request.data)
        elif request.method == "PUT":
            self.instance.acl.clear()
            self.__permission_set(request.data, False)
        return APIResponse(self.__get_all_permission_serializer().data, 200)

    def _change_owner(self, request):  # noce
        if not self.instance.owned_by(self.current_user()):
            raise PermissionDenied(self.perms_msg)
        self.instance.set_owner(User.objects.get(pk=request.data))
        return APIResponse("Owner changed", 200)

    def owner(self, request):  # noce
        if request.method == "GET":
            return APIResponse(self.instance.owner.id, 200)
        elif request.method == "PUT":
            return self._change_owner(request)


class _WithVariablesSerializer(_WithPermissionsSerializer):
    operations = dict(DELETE="remove",
                      POST="add",
                      PUT="set",
                      GET="all")

    def get_operation(self, method, data, attr):
        tp = getattr(self.instance, attr)
        obj_list = self._get_objects(tp.model, data)
        return self._operate(method, data, attr, obj_list)

    def _response(self, total, found, code=200):
        data = dict(total=len(total))
        data["operated"] = len(found)
        data["not_found"] = data["total"] - data["operated"]
        found_ids = [item.id for item in found]
        data["failed_list"] = [i for i in total if i not in found_ids]
        return APIResponse(data, status=code)

    @transaction.atomic
    def _do_with_vars(self, method_name, *args, **kwargs):
        method = getattr(super(_WithVariablesSerializer, self), method_name)
        instance = method(*args, **kwargs)
        return instance

    @transaction.atomic()
    def _operate(self, method, data, attr, obj_list):
        action = self.operations[method]
        tp = getattr(self.instance, attr)
        if action == "all":
            answer = tp.values_list("id", flat=True)
            return APIResponse(answer, status=200)
        elif action == "set":
            getattr(tp, "clear")()
            action = "add"
        getattr(tp, action)(*obj_list)
        return self._response(data, obj_list)

    def create(self, validated_data):
        return self._do_with_vars("create", validated_data=validated_data)

    def update(self, instance, validated_data):
        if "children" in validated_data:
            raise exceptions.ValidationError("Children not allowed to update.")
        return self._do_with_vars(
            "update", instance, validated_data=validated_data
        )

    def get_vars(self, representation):
        return representation.get('vars', None)

    def to_representation(self, instance, hidden_vars=None):
        rep = super(_WithVariablesSerializer, self).to_representation(instance)
        hv = hidden_vars
        hv = instance.HIDDEN_VARS if hv is None else hv
        vars = self.get_vars(rep)
        if vars is not None:
            for mask_key in hv:
                if mask_key in vars.keys():
                    vars[mask_key] = "[~~ENCRYPTED~~]"
        return rep


###################################
# Subclasses for operations
# with hosts and groups
class _InventoryOperations(_WithVariablesSerializer):

    def hosts_operations(self, method, data):
        return self.get_operation(method, data, attr="hosts")

    def groups_operations(self, method, data):
        return self.get_operation(method, data, attr="groups")


###################################





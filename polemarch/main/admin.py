# -*- coding: utf-8 -*-
from django.contrib import admin

from polemarch.main.models import ACLPermission
# from polemarch.main.models.acl import ACLModel
from .models import Script, History, Inventory, Host, Hook, UserGroup


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('name', 'lang', 'date_created', 'project', 'inventory', 'owner')
    pass


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'mode', 'project', 'start_time', 'status')
    pass

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'owner')


@admin.register(Host)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type')


@admin.register(Hook)
class HookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'when')


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('users',)
#
# @admin.register(ACLModel)
# class ACLModelAdmin(admin.ModelAdmin):
#     list_display = ('id',)

@admin.register(ACLPermission)
class ACLPermissionAdmin(admin.ModelAdmin):
    list_display = ('id',)
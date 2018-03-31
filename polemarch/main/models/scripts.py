# -*- coding: utf-8 -*-
# author: dongvt

from __future__ import unicode_literals

import logging
import os
from collections import OrderedDict

import six
from django.db import models

from polemarch.main.tasks import SendHook
from ..exceptions import PMException
from ..utils import ModelHandlers, AnsibleArgumentsReference
from .vars import AbstractVarsQuerySet, BManager
from projects import Project
from hosts import Inventory
from acl import ACLModel
from django.utils import timezone
from django.core.validators import ValidationError


logger = logging.getLogger("polemarch")


class ScriptQuerySet(AbstractVarsQuerySet):
    task_handlers = ModelHandlers("TASKS_HANDLERS", "Unknown execution type!")

# model script
class Script(ACLModel):

    #
    objects = BManager.from_queryset(ScriptQuerySet)()
    task_handlers = objects._queryset_class.task_handlers


    LANG_CHOICES = (
        ('BASH', 'BASH SHELL'),
        ('PYTHON', 'PYTHON')
    )
    name = models.CharField(max_length=512)
    lang = models.CharField(max_length=10, choices=LANG_CHOICES)
    script = models.TextField(max_length=5000, blank=False)
    options = models.TextField(max_length=512, blank=True)
    description = models.TextField(blank=True, max_length=1024)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    inventory = models.ForeignKey(Inventory,
                                  on_delete=models.CASCADE,
                                  blank=True, null=True, default=None, related_query_name="scripts")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_query_name="scripts")


    class Meta:
        default_related_name = "scripts"
        index_together = [
                            "id",
                            "name",
                            "lang",
                            "date_created",
                            "project"
        ]

    def __unicode__(self):
        return str(self.name)

    def _get_history(self, kind, inventory, **extra):
        initiator = extra.pop("initiator", 0)
        initiator_type = extra.pop("initiator_type", "users")
        save_result = extra.pop("save_result", True)
        command = "ansible-playbook"

        # cho nay sex validate bien nhap vao
        # ansible_args = dict(extra)
        # AnsibleArgumentsReference().validate_args(command, ansible_args)

        if not save_result:
            return None, extra
        from .tasks import History
        history_kwargs = dict(start_time=timezone.now(),
            inventory=inventory, project=None,
            kind=kind, raw_stdout="", execute_args=extra,
            initiator=initiator, initiator_type=initiator_type,
        )
        if isinstance(inventory, (six.string_types, six.text_type)):
            history_kwargs['inventory'] = None
        return History.objects.create(status="DELAY", **history_kwargs), extra

    def check_path(self, inventory):
        if not isinstance(inventory, (six.string_types, six.text_type)):
            return
        path = "{}/{}".format(self.path, inventory)
        path = os.path.abspath(os.path.expanduser(path))
        if self.path not in path:
            errors = dict(inventory="Inventory should be in project dir.")
            raise ValidationError(errors)

    def _prepare_kw(self, kind, inventory, **extra):
        self.check_path(inventory)
        # if not mod_name:
        #     raise PMException("Empty playbook/module name.")


        if extra.get("script_remote_path") == None:
            raise PMException("Empty var script_remote_path")

        ## in put : {"script_name": "name","script_local_path":"dd", "script_type":"bash", "script_remote_path":"dddd"}
        ## out put : script_remote_path=dddd script_local_path=dd script_name=name script_type=bash
        extra["extra-vars"] = "name=" + self.name + " " + "lang=" + self.lang + " " + "script_remote_path=" + extra["script_remote_path"]
        history, extra = self._get_history(kind,inventory, **extra)
        kwargs = dict(inventory=inventory, history=history, project=None)
        kwargs.update(extra)
        return kwargs

    # def _send_hook(self, when, kind, kwargs):
    #     msg = OrderedDict(execution_type=kind, when=when)
    #     inventory = kwargs['inventory']
    #     if isinstance(inventory, Inventory):
    #         inventory = inventory.get_hook_data(when)
    #     msg['target'] = OrderedDict(
    #         name=kwargs['target'],
    #         inventory=inventory,
    #         project=kwargs['project'].get_hook_data(when)
    #     )
    #     if kwargs['history'] is not None:
    #         msg['history'] = kwargs['history'].get_hook_data(when)
    #     else:
    #         msg['history'] = None
    #     SendHook.delay(when, msg)

    def execute(self, kind, *args, **extra):
        kind = kind.upper()
        task_class = self.task_handlers.backend(kind)
        sync = extra.pop("sync", False)

        # set biến playbook file
        extra["playbook"] = "/mto_automation/polemarch/projects/1/init.yml"


        kwargs = self._prepare_kw(kind, *args, **extra)
        history = kwargs['history']
        if True:
            # self._send_hook('on_execution', kind, kwargs)
            task_class(**kwargs)
            # self._send_hook('after_execution', kind, kwargs)
        else:
            task_class.delay(**kwargs)
        return history.id if history is not None else history

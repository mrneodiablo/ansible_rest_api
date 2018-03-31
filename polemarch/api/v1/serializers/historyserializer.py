# -*- coding: utf-8 -*-
from  _bashserializer import _SignalSerializer
from rest_framework import serializers
import re
from ....main import models


# history serializer cung cấp serializer
class HistorySerializer(_SignalSerializer):
    class Meta:
        model = models.History
        fields = ("id",
                  "project",
                  "mode",
                  "kind",
                  "status",
                  "inventory",
                  "start_time",
                  "stop_time",
                  "initiator",
                  "initiator_type",
                  "url")


class OneHistorySerializer(_SignalSerializer):
    raw_stdout = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.History
        fields = ("id",
                  "project",
                  "mode",
                  "kind",
                  "status",
                  "start_time",
                  "stop_time",
                  "inventory",
                  "raw_inventory",
                  "raw_args",
                  "raw_stdout",
                  "initiator",
                  "initiator_type",
                  "execute_args",
                  "revision",
                  "url")

    def get_raw(self, request):
        params = request.query_params
        color = params.get("color", "no")
        if color == "yes":
            return self.instance.raw_stdout
        else:
            ansi_escape = re.compile(r'\x1b[^m]*m')
            return ansi_escape.sub('', self.instance.raw_stdout)

    def get_raw_stdout(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri("raw/")

    def get_facts(self, request):
        return self.instance.facts


class HistoryLinesSerializer(_SignalSerializer):
    class Meta:
        model = models.HistoryLines
        fields = ("line_number",
                  "line",)
# -*- coding: utf-8 -*-
from django_filters import CharFilter
from rest_framework import filters as rest_filters
from django.contrib.auth.models import User
from _basefilter import extra_filter, name_filter

class UserFilter(rest_filters.FilterSet):
    id = CharFilter(method=extra_filter)
    id__not = CharFilter(method=extra_filter)
    username__not = CharFilter(method=name_filter)
    username = CharFilter(method=name_filter)

    class Meta:
        model = User
        # fields = (
        #           'id',
        #           'id__not',
        #           'username',
        #           'username__not',
        #           'is_active',
        #           'first_name',
        #           'last_name',
        #           'email',)

        fields = (
                  'id',
                  'id__not',
                  'username',
                  'username__not',)

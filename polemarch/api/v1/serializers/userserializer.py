# -*- coding: utf-8 -*-
from rest_framework import serializers as rest_serializers
from django.contrib.auth.models import User
from rest_framework import exceptions as rest_exceptions
from _bashserializer import with_signals



# User Serializer class để serializer và deserilizer User
# Cung cấp các phương thức create, update vào model User
class UserSerializer(rest_serializers.ModelSerializer):
    class UserExist(rest_exceptions.ValidationError):
        status_code = 409

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'is_active',
                  'is_staff',
                  'url',)
        read_only_fields = ('is_superuser',)

    @with_signals
    def create(self, data):
        if not self.context['request'].user.is_staff:
            raise rest_exceptions.PermissionDenied
        valid_fields = ['username', 'password', 'is_active', 'is_staff',
                        "email", "first_name", "last_name"]
        creditals = {d: data[d] for d in valid_fields
                     if data.get(d, None) is not None}
        raw_passwd = self.initial_data.get("raw_password", "False")
        user = super(UserSerializer, self).create(creditals)
        if not raw_passwd == "True":
            user.set_password(creditals['password'])
            user.save()
        return user

    def is_valid(self, raise_exception=False):
        if self.instance is None:
            try:
                User.objects.get(username=self.initial_data['username'])
                raise self.UserExist({'username': ["Already exists."]})
            except User.DoesNotExist:
                pass
        return super(UserSerializer, self).is_valid(raise_exception)

    @with_signals
    def update(self, instance, validated_data):
        if not self.context['request'].user.is_staff and \
                        instance.id != self.context['request'].user.id:
            # can't be tested because PATCH from non privileged user to other
            # user fails at self.get_object() in View
            raise exceptions.PermissionDenied  # nocv
        instance.username = validated_data.get('username',
                                               instance.username)
        instance.is_active = validated_data.get('is_active',
                                                instance.is_active)
        instance.email = validated_data.get('email',
                                            instance.email)
        instance.first_name = validated_data.get('first_name',
                                                 instance.first_name)
        instance.last_name = validated_data.get('last_name',
                                                instance.last_name)
        instance.is_staff = validated_data.get('is_staff',
                                               instance.is_staff)
        if validated_data.get('password', False):
            instance.set_password(validated_data.get('password', None))
        instance.save()
        return instance

try:
    from teamserializer import TeamSerializer
except:
    TeamSerializer = None
class OneUserSerializer(UserSerializer):
    """
    Serialize cho User model detail
    """
    groups = TeamSerializer(read_only=True, many=True)
    raw_password = rest_serializers.HiddenField(default=False, initial=False)

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'password',
                  'raw_password',
                  'is_active',
                  'is_staff',
                  'first_name',
                  'last_name',
                  'email',
                  'groups',
                  'url',)
        read_only_fields = ('is_superuser',
                            'date_joined',)
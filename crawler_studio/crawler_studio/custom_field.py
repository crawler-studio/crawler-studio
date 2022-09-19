"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/6/19 下午5:26
"""
import json
from rest_framework import serializers


class Str2IntSerializerField(serializers.Field):

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return int(data)


class Str2ListSerializerField(serializers.Field):

    def to_representation(self, value):
        return value.split(',')

    def to_internal_value(self, data):
        return ','.join(data)


class Str2DictSerializerField(serializers.Field):

    def to_representation(self, value):
        return json.loads(value)

    def to_internal_value(self, data):
        return json.dumps(data, ensure_ascii=False)

"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/1/21 下午8:51
"""
from app_source.models import SourceBase, ConfigBase, Category, Source2Category, SourceState
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class Source2CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Source2Category
        fields = '__all__'

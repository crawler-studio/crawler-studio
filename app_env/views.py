from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework.authtoken.views import APIView, AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from app_env.models import EnvVariable
from app_env.ser import EnvVariableSerializer


class EnvVariableCRUD(APIView):

    def get(self, request, **kwargs):
        data = EnvVariable.objects.all()
        ser = EnvVariableSerializer(data, many=True)
        return Response(ser.data)

    def post(self, request, **kwargs):
        pass

    def delete(self, request, **kwargs):
        pass

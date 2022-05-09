from django.contrib.auth.models import User
from rest_framework.authtoken.views import APIView, AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


# 用户注册
class Register(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        if User.objects.filter(username=username).exists():
            resp = {
                'status': False,
                'data': '用户名已被注册'
            }
        else:
            user = User.objects.create_user(username=username,password=password)
            token, created = Token.objects.get_or_create(user=user)
            resp = {
                'status': True,
                'token': token.key,
                'user_id': user.pk,
                'user_name': user.username,
            }
        return Response(resp)


# 用户登录
class Login(APIView):

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'status': True,
            'token': token.key,
            'user_id': user.pk,
            'user_name': user.username,
        })
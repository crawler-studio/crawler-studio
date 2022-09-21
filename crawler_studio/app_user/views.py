from django.contrib.auth.models import User
from rest_framework.authtoken.views import APIView, AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny


# 用户注册
class Register(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        if User.objects.filter(username=username).exists():
            resp = {
                'status': False,
                'data': '用户名已被注册'
            }
        else:
            user = User.objects.create_user(username=username, password=password)
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

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            res = {
                'code': 200,
                'data': {
                    'data': {
                        'status': True,
                        'token': token.key,
                        'user_id': user.pk,
                        'user_name': user.username,
                    }
                },
                'message': '登陆成功'
            }
            return Response(res)